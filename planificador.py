# Planificación Round Robin sobre una cola FIFO de procesos listos.
from collections import deque

QUANTUM = 3


def ejecutar_round_robin(gestor):
    cola = deque(p for p in gestor.procesos if p.estado == "Listo")
    print(f"\n========== ROUND ROBIN (quantum = {QUANTUM}) ==========")
    if not cola:
        print("No hay procesos listos. Libere los bloqueados si corresponde.")
        return []

    tiempo = 0
    traza = []
    while cola:
        proceso = cola.popleft()
        proceso.estado = "Ejecutando"
        turno = min(QUANTUM, proceso.cpu_restante)
        inicio = tiempo
        tiempo += turno
        proceso.cpu_restante -= turno
        traza.append((proceso.pid, inicio, tiempo))
        print(
            f"Tiempo {inicio} -> {tiempo}: PID {proceso.pid}, "
            f"ejecuta {turno}; CPU restante: {proceso.cpu_restante}."
        )

        if proceso.cpu_restante == 0:
            gestor.finalizar_proceso(proceso)
            print(f"  PID {proceso.pid}: Terminado. Libera {proceso.memoria} MB.")
        else:
            proceso.estado = "Listo"
            cola.append(proceso)
            print(f"  Cambio de contexto: PID {proceso.pid} vuelve al final de la cola.")

    print(f"Round Robin finalizado. Tiempo simulado de esta ejecución: {tiempo}.")
    print("Los turnos representan unidades de CPU; no se utiliza tiempo real.")
    return traza
