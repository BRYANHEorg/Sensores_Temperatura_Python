import locale
import random
from datetime import datetime, timedelta
from functools import reduce

locale.setlocale(locale.LC_ALL, "es")

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

DIAS = [
    'Lunes', 'Martes', 'Miércoles', 'Jueves',
    'Viernes', 'Sábado', 'Domingo'
]

INICIO = datetime(2026, 9, 14)


def fecha_texto(fecha):
    return '{0} {1:02d}/{2:02d}/{3}'.format(
        DIAS[fecha.weekday()],
        fecha.day,
        fecha.month,
        fecha.year
    )


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
    return round(
        max(rango[0], min(valor, rango[1])),
        2
    )


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
        'humedad_pct': round(
            random.uniform(*RANGOS['humedad_pct']),
            2
        ),
        'presion_hpa': round(
            random.uniform(*RANGOS['presion_hpa']),
            2
        )
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
        lambda estacion: generar_datos_estacion(
            estacion,
            inicio
        ),
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
    estacion = buscar_estacion(
        estaciones,
        poblacion
    )

    if estacion is None:
        raise ValueError(
            'La población no está registrada.'
        )

    return list(map(
        lambda hora: {
            'hora': '{0:02d}:00'.format(hora),
            'temperatura_promedio_c':
                promedio_temperatura(
                    list(filter(
                        lambda lectura:
                            int(lectura['hora'][:2]) == hora,
                        estacion['lecturas']
                    ))
                )
        },
        range(24)
    ))


# Devuelve una lista con la lectura más calurosa de cada estación.
def momento_mas_caluroso(estaciones):
    return list(map(
        lambda estacion: {
            'estacion_id': estacion['id'],
            'poblacion': estacion['poblacion'],
            'lectura': max(
                estacion['lecturas'],
                key=lambda lectura:
                    lectura['temperatura_c']
            )
        },
        estaciones
    ))


def resumen_presion(estacion, fecha):
    lecturas = list(filter(
        lambda lectura:
            lectura['fecha'] == fecha,
        estacion['lecturas']
    ))

    if not lecturas:
        return {
            'estacion_id': estacion['id'],
            'poblacion': estacion['poblacion'],
            'fecha': fecha,
            'estado': 'Sin datos'
        }

    presiones = list(map(
        lambda lectura:
            lectura['presion_hpa'],
        lecturas
    ))

    minima = min(presiones)
    maxima = max(presiones)

    return {
        'estacion_id': estacion['id'],
        'poblacion': estacion['poblacion'],
        'fecha': fecha,
        'presion_minima_hpa': minima,
        'presion_maxima_hpa': maxima,
        'fluctuacion_hpa': round(
            maxima - minima,
            2
        )
    }


def fluctuacion_barometrica(estaciones, fecha_inicial):
    inicio = datetime.strptime(
        fecha_inicial,
        '%d-%m-%Y'
    )

    fechas = list(map(
        lambda numero:
            (
                inicio + timedelta(days=numero)
            ).strftime('%d-%m-%Y'),
        range(7)
    ))

    return list(map(
        lambda fecha: {
            'fecha': fecha,
            'estaciones': list(map(
                lambda estacion:
                    resumen_presion(
                        estacion,
                        fecha
                    ),
                estaciones
            ))
        },
        fechas
    ))


def fecha_hora(lectura):
    return datetime.strptime(
        '{0} {1}'.format(
            lectura['fecha'],
            lectura['hora']
        ),
        '%d-%m-%Y %H:%M'
    )


def agrupar_alerta(grupos, lectura):
    momento = fecha_hora(lectura)

    criticidad = round(
        (lectura['temperatura_c'] - 32)
        * (lectura['humedad_pct'] - 80),
        2
    )

    # Unir solamente lecturas consecutivas del mismo día.
    if grupos:
        ultimo = grupos[-1]

        fin_anterior = datetime.strptime(
            ultimo['fin'],
            '%d-%m-%Y %H:%M'
        )

        if (
            momento - fin_anterior
            == timedelta(minutes=10)
            and momento.date()
            == fin_anterior.date()
        ):
            ultimo['fin'] = momento.strftime(
                '%d-%m-%Y %H:%M'
            )

            ultimo['criticidad'] = max(
                ultimo['criticidad'],
                criticidad
            )

            return grupos

    grupos.append({
        'inicio': momento.strftime(
            '%d-%m-%Y %H:%M'
        ),
        'fin': momento.strftime(
            '%d-%m-%Y %H:%M'
        ),
        'criticidad': criticidad
    })

    return grupos


def alertas_estacion(estacion):
    criticas = sorted(
        filter(
            lambda lectura:
                lectura['temperatura_c'] > 32
                and lectura['humedad_pct'] > 80,
            estacion['lecturas']
        ),
        key=fecha_hora
    )

    rangos = reduce(
        agrupar_alerta,
        criticas,
        []
    )

    return list(map(
        lambda rango: {
            'estacion_id': estacion['id'],
            'poblacion': estacion['poblacion'],
            **rango
        },
        rangos
    ))


def alertas_bochorno(estaciones):
    alertas = reduce(
        lambda acumuladas, nuevas:
            acumuladas + nuevas,
        map(
            alertas_estacion,
            estaciones
        ),
        []
    )

    return sorted(
        alertas,
        key=lambda alerta:
            alerta['criticidad'],
        reverse=True
    )


def imprimir_resultados(resultados):
    if not resultados:
        print('No se encontraron resultados.')
        return

    # Consumir map para imprimir cada resultado.
    list(map(print, resultados))


def mostrar_menu(estaciones):
    opcion = ''

    while opcion != '0':
        print('\n1. Temperaturas promedio por hora')
        print('2. Momento más caluroso por estación')
        print('3. Fluctuación barométrica')
        print('4. Alertas de bochorno')
        print('0. Salir')

        opcion = input(
            'Seleccione una opción: '
        ).strip()

        try:
            if opcion == '1':
                poblacion = input(
                    'Población: '
                )

                imprimir_resultados(
                    temperaturas_por_hora(
                        estaciones,
                        poblacion
                    )
                )

            elif opcion == '2':
                imprimir_resultados(
                    momento_mas_caluroso(
                        estaciones
                    )
                )

            elif opcion == '3':
                fecha = input(
                    'Fecha inicial (DD-MM-AAAA): '
                )

                imprimir_resultados(
                    fluctuacion_barometrica(
                        estaciones,
                        fecha
                    )
                )

            elif opcion == '4':
                imprimir_resultados(
                    alertas_bochorno(
                        estaciones
                    )
                )

            elif opcion != '0':
                print('Opción inválida.')

        except ValueError as error:
            print(
                'Revise el dato ingresado: {0}'.format(
                    error
                )
            )


if __name__ == '__main__':
    random.seed(42)

    inicio = datetime(
        2026,
        9,
        21
    )

    estaciones = generar_datos_semana(
        inicio
    )

    print(
        'Semana simulada: '
        '21 al 27 de septiembre de 2026'
    )

    print(
        'Estaciones: {0}'.format(
            len(estaciones)
        )
    )

    print(
        'Lecturas: {0}'.format(
            sum(map(
                lambda estacion:
                    len(estacion['lecturas']),
                estaciones
            ))
        )
    )

    mostrar_menu(estaciones)