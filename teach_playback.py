#!/usr/bin/env python3
"""
Sistema Teach and Playback para RoArm-M3.

Flujo general:
1) Conectar por puerto serie al controlador.
2) Desactivar torque para poder mover el brazo a mano.
3) Guardar posiciones manuales (teach).
4) Reproducir esas posiciones con movimiento suave (playback).
"""

import argparse
import json
import os
import select
import sys
import threading
import time

import serial

# En Linux/macOS se usa tty/termios para leer teclas sin Enter.
try:
    import tty
    import termios
except ImportError:
    tty = None
    termios = None

# En Windows se usa msvcrt para lectura no bloqueante de teclado.
try:
    import msvcrt
except ImportError:
    msvcrt = None


class TeachPlaybackController:
    """Controlador principal del modo teach/playback."""

    def __init__(self, port=None, baudrate=115200):
        # Puerto por defecto según plataforma.
        if port is None:
            port = "COM3" if os.name == "nt" else "/dev/tty.usbserial-110"

        self.port = port
        self.baudrate = baudrate

        # Estado de conexión/ejecución.
        self.ser = None
        self.running = False

        # Telemetría actual recibida desde el robot.
        self.current_position = {}

        # Lista de poses grabadas por el usuario.
        self.recorded_positions = []

        # Posición de home tomada de la interfaz web original.
        self.home_position = {
            "x": 235,
            "y": 0,
            "z": 234,
            "t": 0,
            "r": 0,
            "g": 3.14,
        }

        # Parámetros de movimiento.
        self.move_speed = 0.25
        self.interpolation_steps = 20
        self.step_delay = 0.1

    def connect(self):
        """Abre el puerto serie y lanza el hilo de telemetría."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"[OK] Conectado a RoArm en {self.port}")

            self.running = True
            self.telemetry_thread = threading.Thread(target=self._read_telemetry, daemon=True)
            self.telemetry_thread.start()

            # Pequeña espera para estabilizar la comunicación serie.
            time.sleep(2)
            return True
        except Exception as exc:
            print(f"[ERROR] Fallo de conexion: {exc}")
            return False

    def disconnect(self):
        """Cierra conexión y detiene la lectura de telemetría."""
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[INFO] Desconectado")

    def _read_telemetry(self):
        """Lee líneas JSON de telemetría en segundo plano."""
        buffer = ""

        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="ignore")
                    buffer += chunk

                    # Se procesa por líneas completas.
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if line.startswith("{") and line.endswith("}"):
                            try:
                                data = json.loads(line)

                                # Guardamos ejes cartesianos y algunos estados de servo.
                                self.current_position = {
                                    "x": data.get("x", 0),
                                    "y": data.get("y", 0),
                                    "z": data.get("z", 0),
                                    "tit": data.get("tit", 0),
                                    "r": data.get("r", 0),
                                    "g": data.get("g", 3.14),
                                    "tB": data.get("tB", 0),
                                    "tS": data.get("tS", 90),
                                    "tE": data.get("tE", 90),
                                    "tT": data.get("tT", 0),
                                    "tR": data.get("tR", 0),
                                    "tG": data.get("tG", 0),
                                }
                            except json.JSONDecodeError:
                                # Si llega una línea corrupta/incompleta, se ignora.
                                pass
            except Exception as exc:
                if self.running:
                    print(f"[WARN] Error de telemetria: {exc}")

            # Evita consumir CPU innecesariamente.
            time.sleep(0.02)

    def send_command(self, command, quiet=False):
        """Envía un comando JSON al robot."""
        if self.ser and self.ser.is_open:
            try:
                command_str = json.dumps(command) + "\n"
                self.ser.write(command_str.encode())
                if not quiet:
                    print(f"[TX] {command}")
                time.sleep(0.1)
                return True
            except Exception as exc:
                print(f"[ERROR] Envio fallido: {exc}")
                return False
        return False

    def initialize_robot(self):
        """Inicializa el robot con el comando de arranque y va a home."""
        print("[INFO] Inicializando robot...")

        # T=100 es el comando de inicialización usado por el firmware/interfaz.
        self.send_command({"T": 100}, quiet=True)
        time.sleep(1)

        self.move_to_home()

    def turn_off_torque(self):
        """Desactiva torque para mover el brazo manualmente."""
        print("[INFO] Torque OFF (modo manual)")
        return self.send_command({"T": 210, "cmd": 0}, quiet=True)

    def turn_on_torque(self):
        """Activa torque para movimiento controlado por comandos."""
        print("[INFO] Torque ON (modo controlado)")
        return self.send_command({"T": 210, "cmd": 1}, quiet=True)

    def record_current_position(self):
        """Guarda la posición actual reportada por telemetría."""
        if not self.current_position:
            print("[ERROR] Aun no hay telemetria de posicion")
            return False

        position = {
            "x": round(self.current_position.get("x", 0), 2),
            "y": round(self.current_position.get("y", 0), 2),
            "z": round(self.current_position.get("z", 0), 2),
            "t": round(self.current_position.get("tit", 0), 3),
            "r": round(self.current_position.get("r", 0), 3),
            "g": round(self.current_position.get("g", 3.14), 3),
        }

        self.recorded_positions.append(position)

        print(f"[OK] Posicion {len(self.recorded_positions)} guardada")
        print(
            f"     x={position['x']}, y={position['y']}, z={position['z']}, "
            f"t={position['t']}, r={position['r']}, g={position['g']}"
        )
        return True

    def move_to_home(self):
        """Mueve a la posición home definida en `self.home_position`."""
        print("[INFO] Moviendo a HOME...")

        self.turn_on_torque()
        time.sleep(0.1)

        home_cmd = {
            "T": 104,
            "x": self.home_position["x"],
            "y": self.home_position["y"],
            "z": self.home_position["z"],
            "t": self.home_position["t"],
            "r": self.home_position["r"],
            "g": self.home_position["g"],
            "spd": self.move_speed,
        }
        return self.send_command(home_cmd, quiet=True)

    def display_recorded_positions(self):
        """Imprime la lista de poses grabadas."""
        if not self.recorded_positions:
            print("[INFO] No hay posiciones grabadas")
            return

        print("\n[INFO] Posiciones grabadas:")
        for i, pos in enumerate(self.recorded_positions, 1):
            print(
                f"  {i}. x={pos['x']}, y={pos['y']}, z={pos['z']}, "
                f"t={pos['t']}, r={pos['r']}, g={pos['g']}"
            )
        with open("recorded_positions.json", "w") as f:
            json.dump(self.recorded_positions, f, indent=2)
        print("[INFO] Posiciones guardadas en 'recorded_positions.json'")

    def get_key_input(self):
        """Lee una tecla sin bloquear toda la aplicación."""
        if msvcrt:
            if msvcrt.kbhit():
                return msvcrt.getwch()
            return ""

        try:
            if termios is None or tty is None:
                return ""

            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            return key
        except Exception:
            # Fallback simple en terminales no compatibles.
            return input()

    def run_teach_playback(self):
        """Bucle principal de interacción por teclado."""
        print("\nTEACH & PLAYBACK MODE")
        print("=" * 50)
        print("Controles:")
        print("  SPACE  - Grabar posicion actual")
        print("  r      - Volver a HOME")
        print("  p      - Reproducir posiciones")
        print("  l      - Listar posiciones")
        print("  c      - Limpiar posiciones")
        print("  t      - Alternar torque ON/OFF")
        print("  q      - Salir")
        print("=" * 50)

        self.initialize_robot()

        # No se cambia torque automaticamente: solo con tecla `t`.
        # initialize_robot() -> move_to_home() deja torque activado.
        torque_on = True

        print("\n[INFO] Esperando telemetria de posicion...")

        try:
            while True:
                # Línea de estado en tiempo real.
                if self.current_position:
                    pos = self.current_position
                    print(
                        (
                            "\r[POS] "
                            f"x={pos.get('x', 0):.1f}, "
                            f"y={pos.get('y', 0):.1f}, "
                            f"z={pos.get('z', 0):.1f} | "
                            f"Torque: {'ON' if torque_on else 'OFF'} | "
                            f"Grabadas: {len(self.recorded_positions)}"
                        ),
                        end="",
                        flush=True,
                    )

                # Entrada no bloqueante en Windows y POSIX.
                key = ""
                if msvcrt:
                    key = self.get_key_input()
                else:
                    if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                        key = self.get_key_input()

                if key:
                    key = key.lower()
                    print()

                    if key == "q":
                        break
                    elif key == " ":
                        if self.record_current_position():
                            print("[OK] Posicion grabada")
                    elif key == "r":
                        print("[INFO] Volviendo a HOME...")
                        self.move_to_home()
                        time.sleep(2)
                        torque_on = True
                    elif key == "p":
                        if self.recorded_positions:
                            print(f"[INFO] Reproduciendo {len(self.recorded_positions)} posiciones...")
                            self.playback_positions()
                            # Se mantiene el estado de torque.
                            # Solo cambia por accion explicita del usuario.
                            torque_on = True
                        else:
                            print("[ERROR] No hay posiciones para reproducir")
                    elif key == "l":
                        self.display_recorded_positions()
                    elif key == "c":
                        self.recorded_positions.clear()
                        print("[INFO] Lista de posiciones vaciada")
                    elif key == "t":
                        if torque_on:
                            self.turn_off_torque()
                            torque_on = False
                        else:
                            self.turn_on_torque()
                            torque_on = True
                    else:
                        print(f"[WARN] Comando desconocido: '{key}'")

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[INFO] Interrumpido por usuario")

        print("\n[INFO] Saliendo de teach & playback...")

    def playback_positions(self):
        """Reproduce la secuencia completa de posiciones grabadas."""
        if not self.recorded_positions:
            print("[ERROR] No hay posiciones para reproducir")
            return

        print(f"[INFO] Inicio de playback ({len(self.recorded_positions)} posiciones)")

        # La secuencia arranca desde HOME para consistencia.
        self.move_to_home()
        time.sleep(2)

        for i, position in enumerate(self.recorded_positions, 1):
            print(f"\n[INFO] Posicion {i}/{len(self.recorded_positions)}")
            print(
                f"[INFO] Objetivo -> x={position['x']:.1f}, "
                f"y={position['y']:.1f}, z={position['z']:.1f}"
            )
            self.turn_on_torque()
            time.sleep(0.1)
            move_cmd = {
                "T": 104,
                "x": position["x"],
                "y": position["y"],
                "z": position["z"],
                "t": position["t"],
                "r": position["r"],
                "g": position["g"],
                "spd": self.move_speed,
            }
            self.send_command(move_cmd)
            time.sleep(1)

        print("\n[INFO] Retornando a HOME...")
        self.move_to_home()
        self.turn_on_torque()

        print("[OK] Playback finalizado")


def main():
    """Punto de entrada del script."""
    parser = argparse.ArgumentParser(description="Teach and Playback controller for RoArm-M3")
    parser.add_argument("--port", default=None, help="Puerto serie (ej. COM3 o /dev/ttyUSB0)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baudrate serie")
    args = parser.parse_args()

    controller = TeachPlaybackController(port=args.port, baudrate=args.baudrate)

    try:
        if controller.connect():
            controller.run_teach_playback()
        else:
            print("[ERROR] No se pudo conectar al robot")
    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido por usuario")
    finally:
        controller.disconnect()


if __name__ == "__main__":
    main()
