import random 
# Estaciones array
Estaciones = {
    "EST-01": "Puntarenas Centro", 
    "EST-02": "Playa Jacó", 
    "EST-03": "Parrita",
    "EST-04": "Manuel Antonio", 
    "EST-05": "Playa Dominical", 
    "EST-06": "Palmar Sur",
    "EST-07": "Bahía Drake", 
    "EST-08": "Puerto Jiménez", 
    "EST-09": "Golfito",
    "EST-10": "Paso Canoas",
}


# Rango 
rangos = {
    'temperatura': [28, 40],
    'humedad': [60, 100],
    'presion': [1005, 1015]
}


# Function to generate the
for dia in range(1, 8):
    for hora in range(24):
        for minuto in range(0, 60, 10):
            for estacion in estaciones:

                lectura = {
                    'dia': dia,
                    'hora': hora,
                    'minuto': minuto,

                    'temperatura': round(random.uniform(
                        rangos['temperatura'][0],
                        rangos['temperatura'][1]
                    ), 2),

                    'humedad': round(random.uniform(
                        rangos['humedad'][0],
                        rangos['humedad'][1]
                    ), 2),

                    'presion': round(random.uniform(
                        rangos['presion'][0],
                        rangos['presion'][1]
                    ), 2)
                }

                estacion['lecturas'].append(lectura)
