
# Módulo de gestión de procesos
# Proyecto Final - Sistemas Operativos I

class Proceso:
    # Constructor del Bloque de Control de Procesos (PCB)
    def __init__(self, pid, memoria, rafaga_cpu):
        self.pid = pid
        self.estado = "Listo"
        self.memoria = memoria
        self.cpu_total = rafaga_cpu
        self.cpu_restante = rafaga_cpu


class GestorProcesos:
    def __init__(self):
        self.procesos = []
        self.siguiente_pid = 1

    # Registra un nuevo proceso
    def crear_proceso(self):
        print("\n========== CREAR PROCESO ==========")

        try:
            memoria = int(input("Ingrese tamaño en memoria (MB): "))
            cpu = int(input("Ingrese ráfaga de CPU: "))

            if memoria <= 0 or cpu <= 0:
                print("\nError: los valores deben ser mayores que cero.")
                return

            proceso = Proceso(self.siguiente_pid, memoria, cpu)
            self.procesos.append(proceso)
            self.siguiente_pid += 1

            print("\nProceso creado correctamente.")
            print(f"PID: {proceso.pid}")
            print(f"Estado: {proceso.estado}")
            print(f"Memoria: {proceso.memoria} MB")
            print(f"CPU total: {proceso.cpu_total}")
            print(f"CPU restante: {proceso.cpu_restante}")

        except ValueError:
            print("\nError: debe ingresar números enteros.")

    # Muestra los procesos registrados
    def ver_procesos(self):
        print("\n========== LISTA DE PROCESOS ==========")

        if not self.procesos:
            print("No hay procesos registrados.")
            return

        for proceso in self.procesos:
            print(f"\nPID: {proceso.pid}")
            print(f"Estado: {proceso.estado}")
            print(f"Memoria: {proceso.memoria} MB")
            print(f"CPU total: {proceso.cpu_total}")
            print(f"CPU restante: {proceso.cpu_restante}")
            print("--------------------------------")
