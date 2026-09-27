class ReglasTransporte:

    def __init__(self, base_conocimiento):

        self.base = base_conocimiento


    # REGLA 1 estacion existe

    def estacion_existe(
        self,
        stop_id
    ):

        estaciones = self.base.estaciones

        resultado = estaciones[
            estaciones["stop_id"] == stop_id
        ]

        return not resultado.empty

    # REGLA 2 ruta existe


    def ruta_existe(
        self,
        route_id
    ):

        rutas = self.base.rutas

        resultado = rutas[
            rutas["route_id"] == route_id
        ]

        return not resultado.empty


    # REGLA 3 obtener el viaje

    def obtener_viajes_ruta(
        self,
        route_id
    ):

        viajes = self.base.viajes

        resultado = viajes[
            viajes["route_id"] == route_id
        ]

        return resultado


    # REGLA 4 obtener la estacion de viaje

    def obtener_estaciones_viaje(
        self,
        trip_id
    ):

        horarios = self.base.horarios

        resultado = horarios[
            horarios["trip_id"] == trip_id
        ].sort_values(
            "stop_sequence"
        )

        return resultado