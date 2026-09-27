import pandas as pd


class GTFSLoader:

    def __init__(self, ruta_gtfs):

        self.ruta_gtfs = ruta_gtfs


    def cargar(self):

        datos = {}

        datos["routes"] = self._cargar_archivo(
            "routes.txt"
        )

        datos["trips"] = self._cargar_archivo(
            "trips.txt"
        )

        datos["stop_times"] = self._cargar_archivo(
            "stop_times.txt"
        )

        datos["stops"] = self._cargar_archivo(
            "stops.txt"
        )

        return datos


    def _cargar_archivo(
        self,
        nombre_archivo
    ):

        ruta = (
            f"{self.ruta_gtfs}/"
            f"{nombre_archivo}"
        )

        return pd.read_csv(
            ruta,
            low_memory=False
        )