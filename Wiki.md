Docuemntacion sobre el funcioamiento del robot
el Robot cuenta con lo que llamamos 6 grados de libertad, esto significa que tiene 6 ejes de movimiento, de forma simple, 6 motores que actuan en ejes de rotacion diferentes.
# Documentación básica de funcionamiento del robot

## 1. Introducción

El robot con el que vais a trabajar es un **brazo robótico con 6 grados de libertad (6 DOF)**.  
Esto significa que dispone de **seis ejes de movimiento independientes**, cada uno controlado por un motor.

De forma simplificada:

- Cada **motor controla una articulación** del brazo.
- Cada **articulación rota en un eje distinto**.
- La combinación de estos movimientos permite posicionar la herramienta del robot (la punta del brazo) en diferentes posiciones y orientaciones en el espacio.

En otras palabras, el robot puede **moverse en el espacio tridimensional y orientar su extremo** gracias a estos seis ejes.

---

## 2. ¿Qué son los grados de libertad?

Los **grados de libertad (DOF)** indican cuántos movimientos independientes puede realizar un sistema.

En el caso de este robot:

| Eje | Función |
|----|----|
| J1 | Rotación de la base |
| J2 | Elevación del brazo |
| J3 | Extensión del brazo |
| J4 | Inclinación de la muñeca |
| J5 | Rotación de la muñeca  |
| J6 | Abrir/Cerrar pinza |

La posición completa del robot se define mediante **seis valores**, uno para cada eje.

Por ejemplo:

J1 = 0.12
J2 = 1.57
J3 = 0.44
J4 = 0.90
J5 = 0.30
J6 = 3.14

Cada conjunto de valores representa **una postura concreta del brazo**.

---

# 3. Sistema de enseñanza del robot (Teach)

Para facilitar el uso del robot, os hemos proporcionado un **script en Python** que permite registrar posiciones del brazo.

El funcionamiento es el siguiente:

1. Movéis el robot **manualmente con la mano** hasta una posición concreta.
2. El script **lee la posición de los seis ejes**.
3. Esos valores se **guardan en un archivo**.

De esta forma podéis crear una **secuencia de posiciones** que el robot repetirá posteriormente.

Este método se conoce como:

**Teach & Playback**

- **Teach (enseñar):** mover el robot manualmente para registrar posiciones.
- **Playback (reproducir):** el robot repite automáticamente esas posiciones.

---

# 4. Flujo de trabajo recomendado

El proceso habitual para crear una tarea es el siguiente:

### Paso 1 — Definir la tarea

Pensad primero qué queréis que haga el robot.

Por ejemplo:

- mover un objeto
- pulsar un botón
- colocar una pieza en una posición
- simular un proceso repetitivo

---

### Paso 2 — Marcar los puntos clave

Identificad los **puntos importantes del movimiento**, por ejemplo:

- posición inicial
- posición sobre el objeto
- posición de agarre
- posición de transporte
- posición final

Cada uno de estos puntos será **una posición registrada del robot**.

---

### Paso 3 — Enseñar las posiciones

Movéis manualmente el robot hasta cada punto y ejecutáis el script para registrar la posición.

El script guardará algo similar a esto:
posiciones = [
{"j1":0.12,"j2":1.57,"j3":0.44,"j4":0.90,"j5":0.30,"j6":3.14},
{"j1":0.20,"j2":1.40,"j3":0.50,"j4":1.00,"j5":0.10,"j6":3.14}
]

Cada elemento de la lista representa **un punto del recorrido**.

---

### Paso 4 — Ejecutar la secuencia

Una vez definidas todas las posiciones, el robot puede **reproducirlas automáticamente en orden**.

El robot irá pasando de un punto a otro siguiendo la secuencia que habéis definido.

---

# 5. Tipo de sistema de control

El sistema que estamos utilizando es un **sistema de control en lazo abierto**.

Esto significa que:

- El robot **no recibe información del entorno**.
- Simplemente **repite una secuencia de movimientos previamente definida**.

En otras palabras:

> El robot no sabe si la tarea se ha realizado correctamente.  
> Solo repite exactamente los mismos movimientos.

---

# 6. Limitaciones del sistema

Al no haber retroalimentación del entorno, el sistema tiene algunas limitaciones importantes:

- El robot **no detecta objetos**.
- No puede **adaptarse a cambios en la posición de los objetos**.
- No puede **corregir errores automáticamente**.

Por este motivo, es fundamental que **todo el entorno esté siempre en la misma posición**.

---

# 7. Preparación del entorno de trabajo

Para asegurar un funcionamiento correcto se recomienda:

### 1️⃣ Fijar el robot a una mesa

El robot debe estar **firmemente sujeto a una superficie estable**, para evitar desplazamientos.

---

### 2️⃣ Marcar posiciones de los objetos

Es recomendable marcar en la mesa:

- posiciones de los objetos
- zonas de recogida
- zonas de entrega

Se puede hacer con:

- cinta adhesiva
- marcas permanentes
- plantillas

---

### 3️⃣ Mantener el entorno constante

Durante el funcionamiento:

- los objetos deben colocarse **siempre en la misma posición**
- la mesa **no debe moverse**
- el robot **no debe cambiar de base**

---

# 8. Consejos para programar movimientos

Al crear una secuencia de movimientos:

✔ Utilizad **puntos intermedios** si el movimiento es complejo  
✔ Evitad movimientos demasiado rápidos  
✔ Comprobad cada punto antes de ejecutar toda la secuencia  
✔ Aseguraos de que el robot **no colisiona con la mesa u objetos**

---

# 10. Resumen

En este proyecto:

- El robot tiene **6 grados de libertad**.
- Registráis posiciones moviendo el robot manualmente.
- El **script en Python guarda esas posiciones**.
- El robot **reproduce la secuencia automáticamente**.
- El sistema funciona en **lazo abierto**, por lo que el entorno debe permanecer constante.

---
