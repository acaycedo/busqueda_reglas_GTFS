class BaseConocimiento:

    def __init__(self, datos):

        # ==========================
        # Información de rutas
        # ==========================

        self.rutas = datos["routes"]


        # ==========================
        # Información de estaciones
        # ==========================

        self.estaciones = datos["stops"]


        # ==========================
        # Información de viajes
        # ==========================

        self.viajes = datos["trips"]


        # ==========================
        # Orden de las estaciones
        # ==========================

        self.horarios = datos["stop_times"]