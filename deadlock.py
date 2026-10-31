# Dos recursos exclusivos y un ciclo de espera entre dos procesos.


class GestorDeadlock:
    def __init__(self, gestor):
        self.gestor = gestor
        self.recursos = {"Recurso 1": None, "Recurso 2": None}
        # Relaciona cada PID bloqueado con el recurso que está solicitando.
        self.esperando = {}

    def simular(self, pid_a, pid_b):
        if self.esperando:
            raise ValueError("Primero resuelva el deadlock actual.")
        if pid_a == pid_b:
            raise ValueError("Debe seleccionar dos procesos distintos.")
        proceso_a = self.gestor.buscar_proceso(pid_a)
        proceso_b = self.gestor.buscar_proceso(pid_b)
        if proceso_a is None or proceso_b is None:
            raise ValueError("Uno de los PID no existe.")
        if proceso_a.estado != "Listo" or proceso_b.estado != "Listo":
            raise ValueError("Ambos procesos deben estar en estado Listo.")

        self.recursos["Recurso 1"] = pid_a
        self.recursos["Recurso 2"] = pid_b
        print(f"PID {pid_a} obtiene Recurso 1.")
        print(f"PID {pid_b} obtiene Recurso 2.")
        self.esperando[pid_a] = "Recurso 2"
        self.esperando[pid_b] = "Recurso 1"
        proceso_a.estado = "Bloqueado (deadlock)"
        proceso_b.estado = "Bloqueado (deadlock)"
        print(f"PID {pid_a} solicita Recurso 2, retenido por PID {pid_b}: Bloqueado.")
        print(f"PID {pid_b} solicita Recurso 1, retenido por PID {pid_a}: Bloqueado.")
        self.mostrar_estado()

    def detectar(self):
        # Se sigue el grafo de espera: proceso -> propietario del recurso pedido.
        for pid in self.esperando:
            visitados = set()
            actual = pid
            while actual in self.esperando:
                if actual in visitados:
                    return True
                visitados.add(actual)
                actual = self.recursos[self.esperando[actual]]
        return False

    def abortar(self, pid):
        if pid not in self.esperando:
            raise ValueError("El PID debe pertenecer al deadlock actual.")

        proceso = self.gestor.buscar_proceso(pid)
        self.gestor.finalizar_proceso(proceso, abortado=True)
        del self.esperando[pid]
        for recurso, propietario in self.recursos.items():
            if propietario == pid:
                self.recursos[recurso] = None
        print(f"PID {pid}: Abortado. Libera sus recursos y {proceso.memoria} MB de RAM.")

        # En este escenario de dos procesos, el sobreviviente consigue el recurso
        # faltante, termina de usar ambos recursos y vuelve a la cola de listos.
        for otro_pid, solicitado in list(self.esperando.items()):
            if self.recursos[solicitado] is None:
                self.recursos[solicitado] = otro_pid
                print(f"PID {otro_pid} obtiene {solicitado}; se rompe la espera circular.")
                for recurso, propietario in self.recursos.items():
                    if propietario == otro_pid:
                        self.recursos[recurso] = None
                self.gestor.buscar_proceso(otro_pid).estado = "Listo"
                del self.esperando[otro_pid]
                print(f"PID {otro_pid} libera ambos recursos y vuelve a Listo.")
        print("Deadlock resuelto. Puede ejecutar Round Robin.")

    def mostrar_estado(self):
        print("\n========== RECURSOS Y DEADLOCK ==========")
        for recurso, propietario in self.recursos.items():
            print(f"{recurso}: " + ("Libre" if propietario is None else f"PID {propietario}"))
        for pid, recurso in self.esperando.items():
            print(f"PID {pid} espera {recurso}.")
        if self.detectar():
            print("ALERTA: Deadlock detectado por espera circular.")
            print("Use la opción de abortar un proceso para romper el ciclo.")
        else:
            print("No se detecta deadlock.")
