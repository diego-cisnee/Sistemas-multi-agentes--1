"""Ejecuta 40 simulaciones y muestra únicamente la tabla de promedios."""

import random
from statistics import mean

from robot_limpieza import ejecutar_simulacion


AGENTES = (1, 2, 5, 10)
REPETICIONES = 10


def ejecutar():
    resultados = {agentes: [] for agentes in AGENTES}

    # Diez simulaciones independientes por cada cantidad de robots.
    for _ in range(REPETICIONES):
        cantidades = list(AGENTES)
        random.shuffle(cantidades)

        for agentes in cantidades:
            modelo = ejecutar_simulacion(
                filas=10,
                columnas=10,
                porcentaje_suciedad=50,
                numero_agentes=agentes,
                tiempo_maximo=10,
            )

            resultados[agentes].append({
                'tiempo': modelo.tiempo_transcurrido,
                'limpieza': modelo.porcentaje_limpio(),
                'movimientos': modelo.movimientos,
                'pasos': modelo.elapsed_steps,
            })

    filas = []
    for agentes in AGENTES:
        grupo = resultados[agentes]
        filas.append((
            str(agentes),
            f"{mean(r['tiempo'] for r in grupo):.6f}",
            f"{mean(r['limpieza'] for r in grupo):.1f} %",
            f"{mean(r['movimientos'] for r in grupo):.1f}",
            f"{mean(r['pasos'] for r in grupo):.1f}",
        ))

    encabezados = (
        'Robots',
        'Tiempo promedio (s)',
        'Limpieza final promedio',
        'Movimientos totales promedio',
        'Pasos promedio',
    )
    anchos = [max(len(fila[i]) for fila in [encabezados, *filas])
              for i in range(len(encabezados))]

    print(' | '.join(titulo.ljust(ancho)
                     for titulo, ancho in zip(encabezados, anchos)))
    print('-+-'.join('-' * ancho for ancho in anchos))
    for fila in filas:
        print(' | '.join(valor.rjust(ancho)
                         for valor, ancho in zip(fila, anchos)))


if __name__ == '__main__':
    ejecutar()
