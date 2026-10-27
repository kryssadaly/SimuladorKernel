# Administración de RAM con asignación contigua dinámica (primer ajuste).


class MemoriaRAM:
    def __init__(self):
        self.total = 100
        self.utilizada = 0
        # Cada bloque conserva su dirección inicial, tamaño y proceso propietario.
        self.bloques = []

    def memoria_disponible(self):
        return self.total - self.utilizada

    def asignar_memoria(self, cantidad, pid=None):
        if type(cantidad) is not int or cantidad <= 0:
            return False
        if pid is not None and any(b["pid"] == pid for b in self.bloques):
            return False

        # Se busca el primer hueco contiguo suficientemente grande.
        inicio = 0
        for bloque in sorted(self.bloques, key=lambda b: b["inicio"]):
            if bloque["inicio"] - inicio >= cantidad:
                break
            inicio = bloque["inicio"] + bloque["tamano"]

        if inicio + cantidad > self.total:
            return False

        self.bloques.append({"pid": pid, "inicio": inicio, "tamano": cantidad})
        self.bloques.sort(key=lambda b: b["inicio"])
        self.utilizada += cantidad
        return True

    def direccion_de(self, pid):
        for bloque in self.bloques:
            if bloque["pid"] == pid:
                return bloque["inicio"]
        return None

    def liberar_memoria(self, cantidad, pid=None):
        # Solo se libera un bloque existente; nunca se permite RAM negativa.
        for bloque in self.bloques:
            if bloque["tamano"] == cantidad and (pid is None or bloque["pid"] == pid):
                self.bloques.remove(bloque)
                self.utilizada -= cantidad
                return True
        return False

    def mostrar_memoria(self):
        print("\n========== ESTADO DE MEMORIA RAM ==========")
        print(f"Memoria total: {self.total} MB")
        print(f"Memoria utilizada: {self.utilizada} MB")
        print(f"Memoria disponible: {self.memoria_disponible()} MB")
        print("Asignación contigua dinámica: primer ajuste.")
        inicio = 0
        for bloque in self.bloques:
            if bloque["inicio"] > inicio:
                print(f"  [{inicio}, {bloque['inicio']}) MB: Libre")
            fin = bloque["inicio"] + bloque["tamano"]
            print(f"  [{bloque['inicio']}, {fin}) MB: PID {bloque['pid']}")
            inicio = fin
        if inicio < self.total:
            print(f"  [{inicio}, {self.total}) MB: Libre")
        print("Los intervalos incluyen el inicio y excluyen el final.")
