
"""
SIMULACION DE ROBOTS DE LIMPIEZA
Sistema Multiagente desarrollado con Mesa.

INSTALAR MESA: 
pip install mesa numpy

PARAMETROS:
- Numero de filas y columnas.
- Numero de agentes.
- Porcentaje de celdas inicialmente sucias.
- Tiempo maximo de ejecucion en segundos.

ESTADISTICAS:
- Tiempo real transcurrido.
- Porcentaje de celdas limpias.
- Numero total de movimientos.
"""

import mesa
import time
import numpy as np


# ==========================================================
# CLASE AGENTE: ROBOT DE LIMPIEZA
# ==========================================================

class RobotLimpieza(mesa.discrete_space.CellAgent):
    """
    Representa un robot de limpieza.

    1. Si la celda esta sucia, la aspira.
    2. Si esta limpia, elige una celda vecina aleatoria.
    3. Si no tiene vecinos, permanece en su lugar.
    """

    def __init__(self, model, cell):
        super().__init__(model)

        self.cell = cell
        self.movimientos = 0

    def step(self):

        x, y = self.cell.coordinate

        # Si la celda esta sucia, limpiarla.
        if self.model.habitacion[x, y]:

            self.model.habitacion[x, y] = False

        else:

            # Obtener las celdas vecinas.
            vecinos = list(self.cell.neighborhood)

            if vecinos:

                # Elegir una celda aleatoria.
                nueva_celda = self.random.choice(vecinos)

                if nueva_celda != self.cell:

                    self.cell = nueva_celda

                    self.movimientos += 1
                    self.model.movimientos += 1


# ==========================================================
# CLASE MODELO
# ==========================================================

class ModeloLimpieza(mesa.Model):

    def __init__(
        self,
        filas,
        columnas,
        porcentaje_suciedad,
        numero_agentes
    ):

        super().__init__()

        self.filas = filas
        self.columnas = columnas

        # Crear la cuadricula.
        self.grid = mesa.discrete_space.OrthogonalMooreGrid(
            (columnas, filas),
            torus=False,
            random=self.random
        )

        # Matriz de la habitacion.
        # True = sucia.
        # False = limpia.
        self.habitacion = np.zeros(
            (columnas, filas),
            dtype=bool
        )

        # Calcular las celdas sucias.
        total_celdas = filas * columnas

        cantidad_sucia = round(
            total_celdas * porcentaje_suciedad / 100
        )

        # Seleccionar posiciones aleatorias.
        posiciones = self.random.sample(
            range(total_celdas),
            cantidad_sucia
        )

        for posicion in posiciones:

            x = posicion // filas
            y = posicion % filas

            self.habitacion[x, y] = True

        # Estadisticas.
        self.movimientos = 0
        self.elapsed_steps = 0

        # Posicion inicial de todos los robots: [1,1].
        celda_inicial = next(
            cell for cell in self.grid.all_cells
            if cell.coordinate == (0, 0)
        )

        # Crear los agentes.
        for _ in range(numero_agentes):

            RobotLimpieza(self, celda_inicial)

        # Recopilador de datos.
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Porcentaje limpio":
                    lambda m: m.porcentaje_limpio(),

                "Movimientos":
                    lambda m: m.movimientos,

                "Celdas sucias":
                    lambda m: m.contar_sucias()
            }
        )

        self.datacollector.collect(self)

        # Comprobar si comienza limpia.
        if self.contar_sucias() == 0:
            self.running = False

    def contar_sucias(self):

        return int(np.sum(self.habitacion))

    def porcentaje_limpio(self):

        total = self.filas * self.columnas

        limpias = total - self.contar_sucias()

        return (limpias / total) * 100

    def step(self):

        # Activar los robots en orden aleatorio.
        self.agents.shuffle_do("step")

        self.elapsed_steps += 1

        self.datacollector.collect(self)

        # Detener si toda la habitacion esta limpia.
        if self.contar_sucias() == 0:

            self.running = False


# ==========================================================
# FUNCION DE SIMULACION
# ==========================================================

def ejecutar_simulacion(
    filas,
    columnas,
    porcentaje_suciedad,
    numero_agentes,
    tiempo_maximo
):

    # Crear el modelo.
    modelo = ModeloLimpieza(
        filas,
        columnas,
        porcentaje_suciedad,
        numero_agentes
    )

    modelo.tiempo_maximo = tiempo_maximo

    # Iniciar el cronometro en segundos.
    inicio = time.perf_counter()

    # Ejecutar mientras haya suciedad y tiempo disponible.
    while modelo.running:

        tiempo_transcurrido = time.perf_counter() - inicio

        # Comprobar si se alcanzo el limite de tiempo.
        if tiempo_transcurrido >= tiempo_maximo:
            break

        # Ejecutar un paso de todos los agentes.
        modelo.step()

    # Registrar el tiempo real transcurrido.
    modelo.tiempo_transcurrido = time.perf_counter() - inicio

    # Comprobar si se completo la limpieza.
    modelo.limpieza_completa = (
        modelo.contar_sucias() == 0
    )

    if modelo.limpieza_completa:

        modelo.tiempo_limpieza = modelo.tiempo_transcurrido

    else:

        modelo.tiempo_limpieza = None

    return modelo


# ==========================================================
# MOSTRAR RESULTADOS
# ==========================================================

def mostrar_resultados(modelo):

    print("\n========== RESULTADOS ==========")

    print("Numero de agentes:", len(modelo.agents))

    print(
        "Tiempo maximo establecido:",
        modelo.tiempo_maximo,
        "segundos"
    )

    print(
        "Tiempo real que corrio la simulacion:",
        round(modelo.tiempo_transcurrido, 4),
        "segundos"
    )

    if modelo.limpieza_completa:

        print(
            "Tiempo necesario para limpiar:",
            round(modelo.tiempo_limpieza, 4),
            "segundos"
        )

        print("Estado: Habitacion completamente limpia.")

    else:

        print("Estado: Tiempo maximo alcanzado.")
        print("La habitacion no se limpio completamente.")

    print(
        "Porcentaje de celdas limpias:",
        round(modelo.porcentaje_limpio(), 2),
        "%"
    )

    print(
        "Movimientos realizados:",
        modelo.movimientos
    )

    print(
        "Celdas sucias restantes:",
        modelo.contar_sucias()
    )

    print(
        "Pasos ejecutados:",
        modelo.elapsed_steps
    )

    print("================================")


# ==========================================================
# VISUALIZAR HABITACION
# ==========================================================

def visualizar_habitacion(modelo):

    print("\n===== ESTADO FINAL DE LA HABITACION =====")

    robots = {}

    for robot in modelo.agents:

        posicion = robot.cell.coordinate

        robots[posicion] = robots.get(posicion, 0) + 1

    for y in reversed(range(modelo.filas)):

        fila = ""

        for x in range(modelo.columnas):

            if (x, y) in robots:

                cantidad = robots[(x, y)]

                if cantidad == 1:
                    fila += " R  "
                else:
                    fila += f"R{cantidad:<3}"

            elif modelo.habitacion[x, y]:

                fila += " ## "

            else:

                fila += " .. "

        print(fila)

    print("\nLeyenda:")
    print("## = Sucia")
    print(".. = Limpia")
    print("R  = Robot")
    print("R2 = Dos robots")


# ==========================================================
# VALIDACION DE PARAMETROS
# ==========================================================

def solicitar_entero(mensaje, minimo):

    while True:

        try:

            valor = int(input(mensaje))

            if valor >= minimo:
                return valor

            print("El valor minimo permitido es", minimo)

        except ValueError:

            print("Introduce un numero entero valido.")


def solicitar_porcentaje(mensaje):

    while True:

        try:

            valor = float(input(mensaje))

            if 0 <= valor <= 100:
                return valor

            print("El porcentaje debe estar entre 0 y 100.")

        except ValueError:

            print("Introduce un porcentaje valido.")


def solicitar_tiempo(mensaje):

    while True:

        try:

            valor = float(input(mensaje))

            if valor >= 0:
                return valor

            print("El tiempo no puede ser negativo.")

        except ValueError:

            print("Introduce un tiempo valido.")


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    print("\n===== SIMULACION DE ROBOTS DE LIMPIEZA =====")

    filas = solicitar_entero(
        "Numero de filas (M): ", 1
    )

    columnas = solicitar_entero(
        "Numero de columnas (N): ", 1
    )

    numero_agentes = solicitar_entero(
        "Numero de agentes: ", 1
    )

    porcentaje_suciedad = solicitar_porcentaje(
        "Porcentaje de celdas sucias (0-100): "
    )

    tiempo_maximo = solicitar_tiempo(
        "Tiempo maximo de ejecucion (segundos): "
    )

    print("\nIniciando simulacion...")

    modelo = ejecutar_simulacion(
        filas,
        columnas,
        porcentaje_suciedad,
        numero_agentes,
        tiempo_maximo
    )

    mostrar_resultados(modelo)

    visualizar_habitacion(modelo)
