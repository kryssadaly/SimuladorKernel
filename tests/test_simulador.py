# Casos de prueba sin dependencias externas
import io
from pathlib import Path
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

from deadlock import GestorDeadlock
from memoria import MemoriaRAM
from planificador import ejecutar_round_robin
from procesos import GestorProcesos
from semaforos import SemaforoBinario


class PruebasSimulador(unittest.TestCase):
    def setUp(self):
        self.salida = io.StringIO()
        self.redireccion = redirect_stdout(self.salida)
        self.redireccion.__enter__()
        self.addCleanup(self.redireccion.__exit__, None, None, None)
        self.gestor = GestorProcesos()

    def crear(self, memoria=20, cpu=5):
        return self.gestor.registrar_proceso(memoria, cpu)

    def test_limite_ram_rechazo_no_consume_pid(self):
        self.crear(60)
        with self.assertRaisesRegex(ValueError, "Out of Memory"):
            self.crear(41)
        segundo = self.crear(40)
        self.assertEqual(segundo.pid, 2)
        self.assertEqual(self.gestor.memoria.utilizada, 100)
        with self.assertRaises(ValueError):
            self.crear(1)
        self.assertEqual(len(self.gestor.procesos), 2)

    def test_entradas_invalidas_no_cambian_memoria(self):
        for memoria, cpu in [(0, 1), (-1, 2), (1, 0), (1, -2), ("a", 2), (2, 1.5)]:
            with self.subTest(memoria=memoria, cpu=cpu):
                with self.assertRaises(ValueError):
                    self.crear(memoria, cpu)
        self.assertEqual(self.gestor.memoria.utilizada, 0)
        self.assertEqual(self.gestor.siguiente_pid, 1)

    def test_fragmentacion_y_primer_ajuste(self):
        memoria = MemoriaRAM()
        for pid, cantidad in [(1, 30), (2, 40), (3, 30)]:
            self.assertTrue(memoria.asignar_memoria(cantidad, pid))
        self.assertTrue(memoria.liberar_memoria(30, 1))
        self.assertTrue(memoria.liberar_memoria(30, 3))
        self.assertEqual(memoria.memoria_disponible(), 60)
        self.assertFalse(memoria.asignar_memoria(50, 4))
        self.assertTrue(memoria.asignar_memoria(25, 4))
        self.assertEqual(memoria.direccion_de(4), 0)
        self.assertTrue(memoria.liberar_memoria(40, 2))
        self.assertTrue(memoria.asignar_memoria(75, 5))
        self.assertEqual(memoria.direccion_de(5), 25)

    def test_liberacion_invalida_no_corrompe_ram(self):
        memoria = MemoriaRAM()
        memoria.asignar_memoria(20, 1)
        for cantidad, pid in [(-10, 1), (30, 1), (20, 2)]:
            self.assertFalse(memoria.liberar_memoria(cantidad, pid))
        self.assertEqual(memoria.utilizada, 20)
        self.assertTrue(memoria.liberar_memoria(20, 1))
        self.assertFalse(memoria.liberar_memoria(20, 1))
        self.assertEqual(memoria.utilizada, 0)

    def test_round_robin_orden_quantum_y_liberacion(self):
        a = self.crear(60, 7)
        b = self.crear(40, 4)
        self.assertEqual(
            ejecutar_round_robin(self.gestor),
            [(1, 0, 3), (2, 3, 6), (1, 6, 9), (2, 9, 10), (1, 10, 11)],
        )
        for proceso in [a, b]:
            self.assertEqual(proceso.estado, "Terminado")
            self.assertEqual(proceso.cpu_restante, 0)
            self.assertIsNone(proceso.inicio_memoria)
        self.assertEqual(self.gestor.memoria.utilizada, 0)
        self.assertEqual(ejecutar_round_robin(self.gestor), [])
        self.assertEqual(self.gestor.memoria.utilizada, 0)
        self.assertEqual(self.crear(100, 1).pid, 3)

    def test_round_robin_cpu_menor_igual_y_mayor_quantum(self):
        for cpu in [1, 3, 6]:
            self.crear(10, cpu)
        traza = ejecutar_round_robin(self.gestor)
        self.assertEqual(traza, [(1, 0, 1), (2, 1, 4), (3, 4, 7), (3, 7, 10)])
        self.assertEqual(self.gestor.memoria.utilizada, 0)

    def test_semaforo_exclusion_fifo_y_acceso_denegado(self):
        a, b, c = self.crear(), self.crear(), self.crear()
        semaforo = SemaforoBinario()
        self.assertTrue(semaforo.wait(a))
        self.assertFalse(semaforo.wait(b))
        self.assertFalse(semaforo.wait(c))
        with self.assertRaises(ValueError):
            semaforo.incrementar(b)
        with self.assertRaises(ValueError):
            semaforo.signal(b)
        with self.assertRaises(ValueError):
            semaforo.wait(b)
        self.assertEqual(list(semaforo.cola_espera), [b, c])
        self.assertEqual(semaforo.incrementar(a), 1)
        self.assertIs(semaforo.signal(a), b)
        self.assertEqual(semaforo.incrementar(b), 2)
        self.assertIs(semaforo.signal(b), c)
        self.assertEqual(semaforo.incrementar(c), 3)
        self.assertIsNone(semaforo.signal(c))
        self.assertEqual(semaforo.valor, 1)
        self.assertTrue(all(p.estado == "Listo" for p in [a, b, c]))

    def test_round_robin_respeta_semaforo(self):
        a, b, c = self.crear(), self.crear(), self.crear(cpu=1)
        semaforo = SemaforoBinario()
        semaforo.wait(a)
        semaforo.wait(b)
        self.assertEqual(ejecutar_round_robin(self.gestor), [(c.pid, 0, 1)])
        self.assertEqual(self.gestor.memoria.utilizada, 40)
        semaforo.signal(a)
        semaforo.signal(b)
        ejecutar_round_robin(self.gestor)
        self.assertEqual(self.gestor.memoria.utilizada, 0)
        with self.assertRaises(ValueError):
            semaforo.wait(c)

    def test_deadlock_detectar_abortar_y_ejecutar_sobreviviente(self):
        for victima in (1, 2):
            with self.subTest(victima=victima):
                gestor = GestorProcesos()
                a = gestor.registrar_proceso(60, 7)
                b = gestor.registrar_proceso(40, 4)
                deadlock = GestorDeadlock(gestor)
                deadlock.simular(a.pid, b.pid)
                self.assertTrue(deadlock.detectar())
                self.assertEqual(ejecutar_round_robin(gestor), [])
                self.assertEqual(gestor.memoria.utilizada, 100)
                deadlock.abortar(victima)
                abortado = gestor.buscar_proceso(victima)
                vivo = b if victima == a.pid else a
                self.assertEqual(abortado.estado, "Abortado")
                self.assertEqual(vivo.estado, "Listo")
                self.assertEqual(gestor.memoria.utilizada, vivo.memoria)
                self.assertFalse(deadlock.detectar())
                self.assertTrue(all(pid is None for pid in deadlock.recursos.values()))
                with self.assertRaises(ValueError):
                    deadlock.abortar(victima)
                ejecutar_round_robin(gestor)
                self.assertEqual(gestor.memoria.utilizada, 0)

    def test_deadlock_entradas_invalidas_no_bloquean(self):
        a, b = self.crear(), self.crear()
        deadlock = GestorDeadlock(self.gestor)
        for pid_a, pid_b in [(a.pid, a.pid), (a.pid, 999)]:
            with self.assertRaises(ValueError):
                deadlock.simular(pid_a, pid_b)
        self.assertEqual(a.estado, "Listo")
        self.assertEqual(b.estado, "Listo")
        semaforo = SemaforoBinario()
        semaforo.wait(a)
        with self.assertRaises(ValueError):
            deadlock.simular(a.pid, b.pid)
        semaforo.signal(a)
        deadlock.simular(a.pid, b.pid)
        with self.assertRaises(ValueError):
            deadlock.simular(a.pid, b.pid)
        self.assertEqual(len(deadlock.esperando), 2)

    def test_deadlock_puede_repetirse(self):
        a, b, c = self.crear(), self.crear(), self.crear()
        deadlock = GestorDeadlock(self.gestor)
        deadlock.simular(a.pid, b.pid)
        deadlock.abortar(a.pid)
        deadlock.simular(b.pid, c.pid)
        self.assertTrue(deadlock.detectar())
        deadlock.abortar(c.pid)
        self.assertEqual(b.estado, "Listo")
        self.assertEqual(self.gestor.memoria.utilizada, b.memoria)


class PruebasMenu(unittest.TestCase):
    def ejecutar_menu(self, entradas):
        raiz = Path(__file__).resolve().parents[1]
        resultado = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", "main.py"],
            input=entradas, text=True, encoding="utf-8",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=raiz, timeout=10,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, "")
        return resultado.stdout

    def test_menu_validaciones_memoria_y_round_robin(self):
        salida = self.ejecutar_menu(
            "x\n2\n3\n1\ntexto\n1\n-1\n2\n"
            "1\n60\n7\n1\n41\n4\n1\n40\n4\n4\n2\n3\n4\n7\n"
        )
        for esperado in [
            "opción válida", "No hay procesos registrados", "No hay procesos listos",
            "números enteros", "mayores que cero", "Out of Memory",
            "Memoria utilizada: 100 MB", "Tiempo 10 -> 11",
            "Memoria disponible: 100 MB", "Cerrando el simulador",
        ]:
            self.assertIn(esperado, salida)

    def test_menu_semaforo_y_deadlock_completo(self):
        salida = self.ejecutar_menu(
            "1\n20\n5\n1\n20\n5\n"
            "5\nx\n1\nabc\n1\n999\n1\n1\n1\n2\n2\n2\n"
            "2\n1\n3\n1\n2\n2\n3\n2\n4\n0\n"
            "6\nx\n2\n1\n1\n1\n2\n3\n0\n3\n6\n2\n1\n0\n2\n3\n4\n7\n"
        )
        for esperado in [
            "PID debe ser un número entero", "No existe un proceso",
            "Acceso denegado", "de 0 a 1", "de 1 a 2",
            "Deadlock detectado", "Abortado", "Deadlock resuelto",
            "CPU restante: 0", "Memoria disponible: 100 MB",
        ]:
            self.assertIn(esperado, salida)

    def test_fin_de_entrada_en_menu_y_submenus(self):
        for entradas in ["", "5\n", "6\n", "1\n"]:
            with self.subTest(entradas=entradas):
                self.assertIn("Cerrando el simulador", self.ejecutar_menu(entradas))


if __name__ == "__main__":
    unittest.main()
