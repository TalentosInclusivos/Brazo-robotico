# RoArm-M3 Python (Windows)
informacion extra en la [wiki](https://github.com/TalentosInclusivos/Brazo-robotico/wiki/Wiki)

## Que incluye este repo
- `teach_playback.py`: modo teach/playback por puerto serie.
- `run_teach_playback.cmd`: crea/usa `.venv`, instala dependencias y lanza `teach_playback.py`.
- `recorded_positions.json`: posiciones guardadas desde teach.

## Requisitos
- Windows + `cmd`
- Python 3.10+ (recomendado usar `py -3`) (IMPORTANTE, al instalar phython, hay que activar el path, es decirle que si al instalador cuando os pregunte)
- Brazo conectado por USB serie (ej: `COM3`)


## Uso de teach_playback
Script:
primero de todos, comprobamos en que puerto se encuentra el robot conectado. 
clicamos boton de windows + R
escrbimos `cmd`
abrir terminal
escribimos `mode`
tras unos segundos vemos, por ejemplo:

```
Estado para dispositivo COM8:
-----------------------------
    Baudios:             115200
    Paridad:             None
    Bits de datos:       8
    Bits de paro:        1
    Tiempo de espera:    OFF
    XON / XOFF:          OFF
    Protocolo CTS:       OFF
    Protocolo DSR:       OFF
    Sensibilidad de DSR: OFF
    Circuito DTR:        ON
    Circuito RTS:        ON


Estado para dispositivo CON:
----------------------------
    Líneas:              30
    Columnas:            120
    Ritmo del teclado:   31
    Retardo del teclado: 1
    Página de códigos:    850

```

en este caso, vemos que es COM8

iniciamos el run_teach_playback.com

nos pregunta que puerto usar, en este caso seria escribir `COM8`

esto crea un entorno virtual, con todas las dependecias y bibliotecas necesarias para ejecutar el scrip, que nos servira para programar el brazo, conociendo los puntos exactos de su trayetoria

Controles principales:
- `SPACE`: guardar posicion actual.
- `p`: reproducir posiciones guardadas (OJO: el script controla y **mueve el robot**).
- `l`: listar y guardar las posiciones guardadas en el fichero `recorded_positions.json`.
- `t`: torque ON/OFF (cero torque con `T:210,cmd:0`: para mover *"libremente"* el brazo a la posicion deseada).

- `q`: salir.

Importante:
- Para guardar en archivo JSON, usa `l` (*list*).
- El fichero json **se sobrescribe** cada vez que se pulsa la `l`, recomendado renombrar el fichero una vez se tiene una ruta adecuada (conjunto de puntos), para evitar perderla
- El fichero json se puede editar con cualquier editor de textos y se pueden eliminar o añadir puntos (lineas enteras) de otros ficheros similares (es un proceso *delicado*)

## Flujo recomendado
1. Ejecutar `teach_playback` por serie.
2. Desactivar el torque (recomendado que alguien mueva el robot mientras otra persona maneja la consola)
3. Mover el robot manualmente a cada posicion deseada
4. Para cada posicion, guardar puntos con `SPACE`.
5. Guardar JSON con `l`.

es recomendable establecer todos los puntos intermedios necesarios 
## Troubleshooting rapido
- Si falla serie: prueba otro puerto `COM` (`COM4`, `COM5`, etc).
- Si no se crea JSON: en teach, pulsa `l` antes de salir.

## Agradecimientos

Este proyecto incluye una adaptación de scripts basados en el trabajo de Kevin McAleer para el robot RoArm.

Repositorio original:
https://github.com/kevinmcaleer/roarm

Parte del código utilizado en este proyecto está inspirado o adaptado a partir de los ejemplos proporcionados en dicho repositorio.
