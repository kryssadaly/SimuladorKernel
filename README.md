# Simulador de Funciones del Kernel

Proyecto de consola para Sistemas Operativos I. Utiliza únicamente la biblioteca
estándar de Python 3. No requiere instalar paquetes. Los datos viven en memoria
durante la ejecución y se reinician al salir.

## Ejecución

Desde la carpeta del proyecto:

```powershell
python main.py
```

Para ejecutar las pruebas automatizadas:

```powershell
python -B -m unittest discover -s tests -v
```

## Archivos

- `main.py`: menú principal y submenús; validación de las entradas.
- `procesos.py`: PCB, creación, consulta y finalización de procesos.
- `memoria.py`: RAM de 100 MB y asignación contigua dinámica por primer ajuste.
- `planificador.py`: cola FIFO y Round Robin con quantum fijo de 3.
- `semaforos.py`: semáforo binario, cola FIFO y variable global compartida.
- `deadlock.py`: recursos exclusivos, detección de espera circular y recuperación.
- `tests/test_simulador.py`: pruebas de lógica e integración con el menú.

## Cómo probar el menú

### 1. Crear proceso

Seleccione `1`, indique memoria en MB y ráfaga de CPU como enteros positivos.
Cree PID 1 con 60 MB y CPU 7; luego intente crear otro con 41 MB y CPU 4.
Debe recibir `Out of Memory`. El intento rechazado no consume RAM ni PID.
Cree entonces PID 2 con 40 MB y CPU 4: la RAM debe quedar llena.
Pruebe también texto, cero y números negativos: deben rechazarse.

### 2. Ver procesos

Seleccione `2`. Cada PCB muestra PID, estado, tamaño de memoria, ubicación,
CPU total y CPU restante. Los procesos terminados y abortados se conservan
en el historial, pero su memoria ya está liberada.

### 3. Ejecutar Round Robin

Con los dos procesos anteriores, seleccione `3`. El orden esperado es:

| Intervalo de CPU | PID | CPU restante |
| --- | --- | --- |
| 0 a 3 | 1 | 4 |
| 3 a 6 | 2 | 1 |
| 6 a 9 | 1 | 1 |
| 9 a 10 | 2 | 0 |
| 10 a 11 | 1 | 0 |

Los procesos incompletos regresan al final de la cola. Al terminar liberan su
RAM. Seleccione `2` para comprobar su estado y `4` para comprobar los 100 MB
disponibles. Ejecutar de nuevo no debe liberar memoria dos veces.

El tiempo es simulado y comienza en cero en cada ejecución de esta opción.
Los procesos de la cola están disponibles desde ese instante. No se simula
un costo de CPU adicional por cambio de contexto.

### 4. Consultar memoria RAM

Seleccione `4` para ver total, utilizada, disponible y mapa de bloques.
Los intervalos se expresan como `[inicio, fin)` en MB.
Se busca el primer hueco que permita alojar el proceso completo. Por eso,
aunque haya suficiente RAM libre en total, una solicitud puede rechazarse
si los huecos están separados (fragmentación externa).

### 5. Simular semáforo

Reinicie el programa para comenzar con PID 1 y PID 2, y cree dos procesos
(por ejemplo 20 MB y CPU 5 cada uno). Abra la opción `5`:

1. Subopción `1`, PID `1`: obtiene el semáforo.
2. Subopción `1`, PID `2`: queda bloqueado en la cola.
3. Subopción `2`, PID `2`: acceso denegado a la variable compartida.
4. Subopción `2`, PID `1`: incrementa la variable de 0 a 1.
5. Subopción `3`, PID `1`: libera el semáforo; PID 2 entra.
6. Subopción `2`, PID `2`: incrementa la variable de 1 a 2.
7. Subopción `3`, PID `2`: libera el semáforo; ambos quedan Listos.
8. Subopción `0`: vuelve al menú principal.

La variable conserva su valor entre visitas al submenú. Solo el propietario
puede modificarla o ejecutar `signal()`. Los intentos repetidos de `wait()`
no duplican procesos en la cola. Las operaciones se muestran por pasos,
sin hilos reales ni esperas de reloj. La sección crítica usa un estado
didáctico `En sección crítica`; Round Robin solo ejecuta procesos `Listos`.
Libere el semáforo para que sus participantes puedan usar la CPU.

### 6. Simular y resolver deadlock

Con dos procesos Listos, abra `6`:

1. Subopción `1`: indique los PID de A y B.
2. A retiene Recurso 1 y espera Recurso 2; B retiene Recurso 2 y espera
   Recurso 1. Ambos quedan bloqueados y aparece la alerta de deadlock.
3. Subopción `3`: consulte los PCB bloqueados.
4. Subopción `0`: vuelva al menú y consulte RAM. Ambos conservan su memoria.
   Round Robin no ejecuta estos procesos mientras estén bloqueados.
5. Vuelva a `6` y elija subopción `2`; indique el PID que desea abortar.
6. Se libera la RAM y los recursos del abortado. El sobreviviente obtiene el
   recurso faltante, libera ambos recursos y vuelve a Listo.
7. Vuelva con `0` y ejecute Round Robin para terminar al sobreviviente.

La detección recorre las dependencias de espera y busca un ciclo.
No se permiten PID iguales, inexistentes, terminados, abortados o participantes
del semáforo para crear este deadlock. Se mantiene un escenario de dos
procesos y dos recursos a la vez.

### 7. Salir

Seleccione `7`. También puede cerrar con Ctrl+C o fin de entrada sin traza
de error. Las opciones no reconocidas muestran un mensaje y permiten continuar.

## Alcance de la entrega

Este repositorio implementa el simulador y sus pruebas. El reporte académico
en PDF, las capturas o volcados comentados y la presentación deben prepararse
aparte según el enunciado. No se modifica el documento personal existente.
