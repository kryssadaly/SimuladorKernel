# Gestión de procesos y bloques de control (PCB).
from memoria import MemoriaRAM


class Proceso:
    # Representa el PCB: los datos que el kernel necesita para controlar un proceso
    def __init__(self, pid, memoria, rafaga_cpu):
        # Al crearse queda Listo y todavía tiene toda su ráfaga de CPU pendiente
        self.pid = pid
        self.estado = "Listo"
        self.memoria = memoria
        self.cpu_total = rafaga_cpu
        self.cpu_restante = rafaga_cpu
        # El gestor asignará la dirección cuando reserve un bloque de RAM
        self.inicio_memoria = None


class GestorProcesos:
    # Mantiene el registro de PCB y coordina sus reservas con el administrador de RAM
    def __init__(self):
        # Se conserva el historial; los PID aumentan y no se reutilizan
        self.procesos = []
        self.siguiente_pid = 1
        self.memoria = MemoriaRAM()

    def registrar_proceso(self, memoria, cpu):
        # La lógica se separa de input() para poder comprobarla con pruebas.
        if type(memoria) is not int or type(cpu) is not int:
            raise ValueError("Debe ingresar números enteros")
        if memoria <= 0 or cpu <= 0:
            raise ValueError("Los valores deben ser mayores que cero")

        # Primero se reserva RAM; si falla, no se registra ni se consume el PID
        pid = self.siguiente_pid
        if not self.memoria.asignar_memoria(memoria, pid):
            raise ValueError(
                "Out of Memory: no hay un bloque contiguo suficiente "
                f"RAM disponible: {self.memoria.memoria_disponible()} MB"
            )

        proceso = Proceso(pid, memoria, cpu)
        proceso.inicio_memoria = self.memoria.direccion_de(pid)
        self.procesos.append(proceso)
        self.siguiente_pid += 1
        return proceso

    def crear_proceso(self):
        # Solicita los datos por consola y convierte los errores en mensajes legibles
        print("\n========== CREAR PROCESO ==========")
        try:
            memoria = int(input("Ingrese tamaño en memoria (MB): "))
            cpu = int(input("Ingrese ráfaga de CPU: "))
        except ValueError:
            print("\nError: debe ingresar números enteros")
            return

        try:
            proceso = self.registrar_proceso(memoria, cpu)
        except ValueError as error:
            print(f"\nError: {error}")
            return
        print("\nProceso creado correctamente.")
        self.mostrar_pcb(proceso)

    def buscar_proceso(self, pid):
        # Devuelve el PCB correspondiente, o None si ese identificador no existe
        return next((p for p in self.procesos if p.pid == pid), None)

    def finalizar_proceso(self, proceso, abortado=False):
        # Libera la RAM una sola vez y conserva el PCB para futuras consultas
        if proceso not in self.procesos:
            raise ValueError("El proceso no pertenece a este gestor")
        if proceso.estado in ("Terminado", "Abortado"):
            return False

        self.memoria.liberar_memoria(proceso.memoria, proceso.pid)
        proceso.inicio_memoria = None
        proceso.estado = "Abortado" if abortado else "Terminado"
        # Un aborto conserva la CPU pendiente; una terminación normal la deja en cero
        if not abortado:
            proceso.cpu_restante = 0
        return True

    @staticmethod
    def mostrar_pcb(proceso):
        # Presenta los datos de un PCB; no necesita acceder al estado del gestor
        print(f"PID: {proceso.pid}")
        print(f"Estado: {proceso.estado}")
        # El PCB conserva el tamaño original después de liberar su RAM.
        print(f"Memoria solicitada: {proceso.memoria} MB")
        if proceso.inicio_memoria is None:
            print("Ubicación en RAM: liberada")
        else:
            fin = proceso.inicio_memoria + proceso.memoria
            print(f"Ubicación en RAM: [{proceso.inicio_memoria}, {fin}) MB")
        print(f"CPU total: {proceso.cpu_total}")
        print(f"CPU restante: {proceso.cpu_restante}")

    def ver_procesos(self):
        # Incluye procesos activos, terminados y abortados en el mismo historial
        print("\n========== LISTA DE PROCESOS ==========")
        if not self.procesos:
            print("No hay procesos registrados")
            return
        for proceso in self.procesos:
            self.mostrar_pcb(proceso)
            print("--------------------------------")
