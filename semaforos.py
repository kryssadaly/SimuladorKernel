# Semáforo binario para una sección crítica simulada, sin hilos reales.
from collections import deque


class SemaforoBinario:
    def __init__(self):
        self.propietario = None
        self.cola_espera = deque()
        self.variable_compartida = 0

    @property
    def valor(self):
        return 1 if self.propietario is None else 0

    def wait(self, proceso):
        # Un proceso bloqueado se encola una sola vez.
        if self.propietario is proceso or proceso in self.cola_espera:
            raise ValueError("El proceso ya posee el semáforo o está en su cola.")
        if proceso.estado != "Listo":
            raise ValueError("Solo un proceso Listo puede solicitar este semáforo.")

        if self.propietario is None:
            self.propietario = proceso
            proceso.estado = "En sección crítica"
            print(f"wait(): PID {proceso.pid} obtiene el semáforo.")
            return True

        proceso.estado = "Bloqueado (semáforo)"
        self.cola_espera.append(proceso)
        print(f"wait(): PID {proceso.pid} queda Bloqueado en la cola de espera.")
        return False

    def incrementar(self, proceso):
        if self.propietario is not proceso:
            raise ValueError("Acceso denegado: el proceso no posee el semáforo.")
        anterior = self.variable_compartida
        self.variable_compartida += 1
        print(
            f"Sección crítica: PID {proceso.pid} cambia la variable global "
            f"de {anterior} a {self.variable_compartida}."
        )
        return self.variable_compartida

    def signal(self, proceso):
        if self.propietario is not proceso:
            raise ValueError("Solo el propietario puede liberar el semáforo.")

        proceso.estado = "Listo"
        self.propietario = None
        print(f"signal(): PID {proceso.pid} libera el semáforo.")
        if self.cola_espera:
            # Se entrega al primero en espera, sin permitir que otro se adelante.
            siguiente = self.cola_espera.popleft()
            self.propietario = siguiente
            siguiente.estado = "En sección crítica"
            print(f"  PID {siguiente.pid} sale de la cola y entra a la sección crítica.")
        return self.propietario

    def mostrar_estado(self):
        print("\n========== SEMÁFORO BINARIO ==========")
        print(f"Valor: {self.valor} (1 = libre; 0 = ocupado)")
        propietario = self.propietario.pid if self.propietario else "ninguno"
        print(f"Propietario: {propietario}")
        print(f"Cola de espera FIFO: {[p.pid for p in self.cola_espera]}")
        print(f"Variable global compartida: {self.variable_compartida}")
