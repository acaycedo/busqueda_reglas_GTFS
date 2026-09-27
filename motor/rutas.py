import heapq


class MotorRutas:

    def __init__(self, grafo):

        self.grafo = grafo

        # Penalización por cada transbordo
        self.penalizacion_transbordo = 300


    # ==========================================
    # BUSCAR RUTA
    # ==========================================

    def buscar_ruta(self, origen, destino):

        # Verificar que las estaciones existan
        if origen not in self.grafo:
            raise ValueError(
                f"La estación de origen '{origen}' no existe."
            )

        if destino not in self.grafo:
            raise ValueError(
                f"La estación de destino '{destino}' no existe."
            )


        # Estado inicial:
        # estación de origen y ninguna ruta utilizada
        estado_inicial = (origen, None)


        # Cola de prioridad
        cola = []

        heapq.heappush(
            cola,
            (0, 0, 0, origen, None)
        )


        # Guarda el mejor costo conocido
        mejores_costos = {
            estado_inicial: 0
        }


        # Guarda las estaciones anteriores
        anteriores = {}


        # Buscar mientras existan opciones
        while cola:

            (
                costo_actual,
                conexiones_actuales,
                transbordos_actuales,
                estacion_actual,
                ruta_actual
            ) = heapq.heappop(cola)


            estado_actual = (
                estacion_actual,
                ruta_actual
            )


            # Ignorar una opción si ya encontramos una mejor
            if costo_actual > mejores_costos.get(
                estado_actual,
                float("inf")
            ):
                continue


            # Si llegamos al destino, reconstruimos la ruta
            if estacion_actual == destino:

                return self._reconstruir_ruta(
                    anteriores,
                    estado_actual
                )


            # Revisar las estaciones conectadas
            for destino_siguiente in self.grafo[
                estacion_actual
            ]:

                conexiones = self.grafo[
                    estacion_actual
                ][
                    destino_siguiente
                ]


                # Revisar las rutas disponibles
                for _, datos in conexiones.items():

                    nueva_ruta = datos["route_id"]


                    # Determinar si existe un transbordo
                    if ruta_actual is None:

                        nuevos_transbordos = (
                            transbordos_actuales
                        )

                    elif nueva_ruta != ruta_actual:

                        nuevos_transbordos = (
                            transbordos_actuales + 1
                        )

                    else:

                        nuevos_transbordos = (
                            transbordos_actuales
                        )


                    # Aumentar número de conexiones
                    nuevas_conexiones = (
                        conexiones_actuales + 1
                    )


                    # Calcular costo
                    nuevo_costo = (
                        nuevas_conexiones
                        +
                        (
                            nuevos_transbordos
                            * self.penalizacion_transbordo
                        )
                    )


                    nuevo_estado = (
                        destino_siguiente,
                        nueva_ruta
                    )


                    # Guardar si encontramos una mejor opción
                    if nuevo_costo < mejores_costos.get(
                        nuevo_estado,
                        float("inf")
                    ):

                        mejores_costos[
                            nuevo_estado
                        ] = nuevo_costo


                        anteriores[
                            nuevo_estado
                        ] = (
                            estado_actual,
                            nueva_ruta
                        )


                        heapq.heappush(
                            cola,
                            (
                                nuevo_costo,
                                nuevas_conexiones,
                                nuevos_transbordos,
                                destino_siguiente,
                                nueva_ruta
                            )
                        )


        # No se encontró una ruta
        return None


    # ==========================================
    # RECONSTRUIR RUTA
    # ==========================================

    def _reconstruir_ruta(
        self,
        anteriores,
        estado_final
    ):

        estaciones = []
        rutas = []


        estado_actual = estado_final


        # Recorrer desde el destino hasta el origen
        while estado_actual in anteriores:

            estaciones.append(
                estado_actual[0]
            )


            estado_anterior, ruta = anteriores[
                estado_actual
            ]


            rutas.append(ruta)


            estado_actual = estado_anterior


        # Agregar el origen
        estaciones.append(
            estado_actual[0]
        )


        # Colocar en orden origen → destino
        estaciones.reverse()
        rutas.reverse()


        return {
            "estaciones": estaciones,
            "rutas": rutas
        }


    # ==========================================
    # ANALIZAR RUTA
    # ==========================================

    def analizar_ruta(self, informacion):

        if informacion is None:
            return None


        estaciones = informacion["estaciones"]
        rutas = informacion["rutas"]


        # Número de conexiones
        conexiones = len(estaciones) - 1


        # Contar transbordos
        transbordos = 0
        ruta_anterior = None


        for ruta in rutas:

            if ruta_anterior is not None:

                if ruta != ruta_anterior:
                    transbordos += 1


            ruta_anterior = ruta


        # Calcular costo
        costo = (
            conexiones
            +
            (
                transbordos
                * self.penalizacion_transbordo
            )
        )


        return {
            "estaciones": estaciones,
            "rutas": rutas,
            "conexiones": conexiones,
            "transbordos": transbordos,
            "costo": costo
        }