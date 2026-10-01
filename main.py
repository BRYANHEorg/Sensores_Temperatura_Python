import locale
import random
locale.setlocale(locale.LC_ALL, "es")
from datetime import datetime, timedelta

RANGOS = {
    'temperatura_c': [24, 35],
    'humedad_pct': [60, 100],
    'presion_hpa': [1005, 1015]
}

POBLACIONES = [
    'Puntarenas Centro', 'Caldera', 'Tárcoles', 'Jacó',
    'Esterillos', 'Quepos', 'Dominical', 'Uvita',
    'Golfito', 'Puerto Jiménez'
]

DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
INICIO = datetime(2026, 9, 14)  # la semana de lecturas empieza el lunes 14/09/2026



def fecha_texto(fecha):
    return '{0} {1:02d}/{2:02d}/{3}'.format(DIAS[fecha.weekday()], fecha.day, fecha.month, fecha.year)


def crear_estaciones():
    return list(map(
        lambda dato: {
            'id': 'EST{0:02d}'.format(dato[0] + 1),
            'poblacion': dato[1],
            'lecturas': []
        },
        enumerate(POBLACIONES)
    ))


