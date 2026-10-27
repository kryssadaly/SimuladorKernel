
# Proyecto Final - Sistemas Operativos I
# Simulador de Funciones del Kernel
# Universidad Mariano Gálvez de Guatemala


# Función principal del programa
from procesos import GestorProcesos

def mostrar_menu():
    print("\n========== MENÚ PRINCIPAL ==========")
    print("1. Crear proceso")
    print("2. Ver procesos")
    print("3. Ejecutar Round Robin")
    print("4. Consultar memoria RAM")
    print("5. Simular semáforo")
    print("6. Simular Deadlock")
    print("7. Salir")
    print("====================================")

def main():
    print("======================================")
    print("    SIMULADOR DE FUNCIONES DEL KERNEL")
    print("======================================")
    print("Universidad Mariano Gálvez de Guatemala")
    print("Curso: Sistemas Operativos I")

    # Crear el gestor de procesos
    gestor = GestorProcesos()

    while True:
        mostrar_menu()

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            gestor.crear_proceso()

        elif opcion == "2":
            gestor.ver_procesos()

        elif opcion == "3":
            print("\nOpción seleccionada: Ejecutar Round Robin")

        elif opcion == "4":
            print("\nOpción seleccionada: Consultar memoria RAM")

        elif opcion == "5":
            print("\nOpción seleccionada: Simular semáforo")

        elif opcion == "6":
            print("\nOpción seleccionada: Simular Deadlock")

        elif opcion == "7":
            print("\nCerrando el simulador...")
            break

        else:
            print("\nError: seleccione una opción válida.")


if __name__ == "__main__":
    main()
