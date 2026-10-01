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
INICIO = datetime(2026, 9, 14)



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


def limitar(valor, rango):
    return round(max(rango[0], min(valor, rango[1])), 2)


def generar_lectura(fecha, temperatura_anterior):
    # Variación gradual de temperatura entre lecturas.
    temperatura = limitar(
        temperatura_anterior + random.uniform(-0.5, 0.5),
        RANGOS['temperatura_c']
    )

    return {
        'fecha': fecha.strftime('%d-%m-%Y'),
        'hora': fecha.strftime('%H:%M'),
        'temperatura_c': temperatura,
        'humedad_pct': round(random.uniform(
            *RANGOS['humedad_pct']
        ), 2),
        'presion_hpa': round(random.uniform(
            *RANGOS['presion_hpa']
        ), 2)
    }


def generar_datos_estacion(estacion, inicio):
    temperatura = random.uniform(*RANGOS['temperatura_c'])
    lecturas = []

    # Ciclo usado para generar datos, no para consultas o cálculos.
    for numero in range(7 * 24 * 6):
        fecha = inicio + timedelta(minutes=numero * 10)
        lectura = generar_lectura(fecha, temperatura)
        lecturas.append(lectura)
        temperatura = lectura['temperatura_c']

    return {
        'id': estacion['id'],
        'poblacion': estacion['poblacion'],
        'lecturas': lecturas
    }


def generar_datos_semana(inicio):
    return list(map(
        lambda estacion: generar_datos_estacion(estacion, inicio),
        crear_estaciones()
    ))

def buscar_estacion(estaciones, poblacion):
    coincidencias = list(filter(
        lambda estacion:
            estacion['poblacion'].strip().lower()
            == poblacion.strip().lower(),
        estaciones
    ))

    return coincidencias[0] if coincidencias else None


def promedio_temperatura(lecturas):
    return round(
        sum(map(
            lambda lectura: lectura['temperatura_c'],
            lecturas
        )) / len(lecturas),
        2
    ) if lecturas else None


def temperaturas_por_hora(estaciones, poblacion):
    estacion = buscar_estacion(estaciones, poblacion)

    if estacion is None:
        raise ValueError('La población no está registrada.')

    return list(map(
        lambda hora: {
            'hora': '{0:02d}:00'.format(hora),
            'temperatura_promedio_c': promedio_temperatura(
                list(filter(
                    lambda lectura:
                        int(lectura['hora'][:2]) == hora,
                    estacion['lecturas']
                ))
            )
        },
        range(24)
    ))

# momento_mas_caluroso: Devuelve una lista de diccionarios con la estación, población y lectura más calurosa de cada estación.
def momento_mas_caluroso(estaciones):
    return list(map(
        lambda estacion: {
            'estacion_id': estacion['id'],
            'poblacion': estacion['poblacion'],
            'lectura': max(
                estacion['lecturas'],
                key=lambda lectura: lectura['temperatura_c']
            )
        },
        estaciones
    ))
