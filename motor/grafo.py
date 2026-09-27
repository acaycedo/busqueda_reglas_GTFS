import networkx as nx


class ConstructorGrafo:

    def __init__(self, base_conocimiento):

        self.base = base_conocimiento


    # ==========================================
    # CONSTRUIR GRAFO
    # ==========================================

    def construir(self):

        grafo = nx.MultiDiGraph()

        self._agregar_estaciones(grafo)

        self._agregar_conexiones(grafo)

        return grafo


    # ==========================================
    # AGREGAR ESTACIONES
    # ==========================================

    def _agregar_estaciones(self, grafo):

        estaciones = self.base.estaciones[
            [
                "stop_id",
                "stop_name"
            ]
        ].drop_duplicates(
            subset="stop_id"
        )


        for estacion in estaciones.itertuples(
            index=False
        ):

            grafo.add_node(
                estacion.stop_id,
                nombre=estacion.stop_name
            )


    # ==========================================
    # AGREGAR CONEXIONES
    # ==========================================

    def _agregar_conexiones(self, grafo):

        viajes = self.base.viajes[
            [
                "trip_id",
                "route_id"
            ]
        ].drop_duplicates(
            subset="trip_id"
        )


        horarios = self.base.horarios[
            [
                "trip_id",
                "stop_id",
                "stop_sequence"
            ]
        ].copy()


        # Relacionar cada viaje con su ruta

        horarios = horarios.merge(
            viajes,
            on="trip_id",
            how="inner"
        )


        # Ordenar las estaciones de cada viaje

        horarios = horarios.sort_values(
            [
                "trip_id",
                "stop_sequence"
            ]
        )


        # Obtener la siguiente estación

        horarios[
            "siguiente_stop"
        ] = (
            horarios
            .groupby("trip_id")[
                "stop_id"
            ]
            .shift(-1)
        )


        # Conservar conexiones válidas

        conexiones = horarios[
            horarios[
                "siguiente_stop"
            ].notna()
        ].copy()


        # Evitar conexiones hacia la misma estación

        conexiones = conexiones[
            conexiones["stop_id"]
            !=
            conexiones["siguiente_stop"]
        ]


        # Conservar únicamente los datos necesarios

        conexiones = conexiones[
            [
                "stop_id",
                "siguiente_stop",
                "route_id"
            ]
        ]


        # Eliminar conexiones repetidas

        conexiones = conexiones.drop_duplicates(
            subset=[
                "stop_id",
                "siguiente_stop",
                "route_id"
            ]
        )


        # Crear las conexiones del grafo

        for conexion in conexiones.itertuples(
            index=False
        ):

            grafo.add_edge(
                conexion.stop_id,
                conexion.siguiente_stop,
                route_id=conexion.route_id
            )