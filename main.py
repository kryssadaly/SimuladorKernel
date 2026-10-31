# Proyecto Final - Sistemas Operativos I
# Simulador de Funciones del Kernel
# Universidad Mariano Gálvez de Guatemala
from procesos import GestorProcesos
from planificador import ejecutar_round_robin
from semaforos import SemaforoBinario
from deadlock import GestorDeadlock


def mostrar_menu():
    # Presenta las funciones del kernel disponibles para la demostración.
    print("\n========== MENÚ PRINCIPAL ==========")
    print("1. Crear proceso")
    print("2. Ver procesos")
    print("3. Ejecutar Round Robin")
    print("4. Consultar memoria RAM")
    print("5. Simular semáforo")
    print("6. Simular Deadlock")
    print("7. Salir")
    print("====================================")


def leer_proceso(gestor, mensaje="Ingrese PID: "):
    # Centraliza la lectura del PID y comprueba que exista un PCB con ese número
    try:
        pid = int(input(mensaje))
    except ValueError:
        raise ValueError("El PID debe ser un número entero.")
    proceso = gestor.buscar_proceso(pid)
    if proceso is None:
        raise ValueError("No existe un proceso con ese PID.")
    return proceso


def menu_semaforo(gestor, semaforo):
    # Permite ejecutar wait, modificar el dato protegido y ejecutar signal por pasos
    while True:
        semaforo.mostrar_estado()
        print("1. Solicitar entrada: wait()")
        print("2. Incrementar variable compartida (solo propietario)")
        print("3. Liberar sección crítica: signal()")
        print("4. Ver procesos")
        print("0. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()
        try:
            if opcion == "0":
                return
            if opcion == "1":
                semaforo.wait(leer_proceso(gestor))
            elif opcion == "2":
                semaforo.incrementar(leer_proceso(gestor))
            elif opcion == "3":
                semaforo.signal(leer_proceso(gestor))
            elif opcion == "4":
                gestor.ver_procesos()
            else:
                print("Error: seleccione una opción válida.")
        except ValueError as error:
            print(f"Error: {error}")


def menu_deadlock(gestor, deadlock):
    # Mantiene visible el bloqueo hasta que se elija un proceso para abortarlo
    while True:
        deadlock.mostrar_estado()
        print("1. Producir deadlock con dos procesos listos")
        print("2. Abortar un proceso del deadlock y liberar recursos")
        print("3. Ver procesos")
        print("0. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()
        try:
            if opcion == "0":
                return
            if opcion == "1":
                listos = [p.pid for p in gestor.procesos if p.estado == "Listo"]
                if len(listos) < 2:
                    print("Necesita al menos dos procesos Listos. Créelos o libere los bloqueados")
                    continue
                print(f"PID disponibles: {listos}")
                proceso_a = leer_proceso(gestor, "PID del proceso A: ")
                proceso_b = leer_proceso(gestor, "PID del proceso B: ")
                deadlock.simular(proceso_a.pid, proceso_b.pid)
            elif opcion == "2":
                proceso = leer_proceso(gestor, "PID que desea abortar: ")
                deadlock.abortar(proceso.pid)
            elif opcion == "3":
                gestor.ver_procesos()
            else:
                print("Error: seleccione una opción válida")
        except ValueError as error:
            print(f"Error: {error}")


def main():
    # Crea los componentes y conecta las opciones del menú con sus operaciones
    print("======================================")
    print("    SIMULADOR DE FUNCIONES DEL KERNEL")
    print("======================================")
    print("Universidad Mariano Gálvez de Guatemala")
    print("Curso: Sistemas Operativos I")
    print("Simulación lógica: no modifica procesos ni memoria reales")

    # Se crean una sola vez para conservar los PCB y los recursos entre submenús
    gestor = GestorProcesos()
    semaforo = SemaforoBinario()
    deadlock = GestorDeadlock(gestor)
    try:
        while True:
            mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()
            if opcion == "1":
                gestor.crear_proceso()
            elif opcion == "2":
                gestor.ver_procesos()
            elif opcion == "3":
                ejecutar_round_robin(gestor)
            elif opcion == "4":
                gestor.memoria.mostrar_memoria()
            elif opcion == "5":
                menu_semaforo(gestor, semaforo)
            elif opcion == "6":
                menu_deadlock(gestor, deadlock)
            elif opcion == "7":
                print("\nCerrando el simulador...")
                break
            else:
                print("\nError: seleccione una opción válida")
    # Permite cerrar desde cualquier menú con fin de entrada o Ctrl+C.
    except (EOFError, KeyboardInterrupt):
        print("\nCerrando el simulador...")


if __name__ == "__main__":
    main()
