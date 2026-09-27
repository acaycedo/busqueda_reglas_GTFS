from fuentes.gtfs_loader import GTFSLoader
from conocimiento.base_conocimiento import BaseConocimiento
from conocimiento.reglas import ReglasTransporte
from motor.grafo import ConstructorGrafo
from motor.rutas import MotorRutas


def main():

    # ==========================================
    # 1. CARGAR DATOS GTFS
    # ==========================================

    loader = GTFSLoader(
        "datos/gtfs"
    )

    datos = loader.cargar()


    # ==========================================
    # 2. CREAR BASE DE CONOCIMIENTO
    # ==========================================

    base = BaseConocimiento(
        datos
    )


    # ==========================================
    # 3. CARGAR REGLAS
    # ==========================================

    reglas = ReglasTransporte(
        base
    )


    # ==========================================
    # 4. CONSTRUIR GRAFO
    # ==========================================

    constructor = ConstructorGrafo(
        base
    )

    grafo = constructor.construir()


    # ==========================================
    # 5. CREAR MOTOR DE RUTAS
    # ==========================================

    motor = MotorRutas(
        grafo
    )


    # ==========================================
    # 6. SELECCIONAR ORIGEN Y DESTINO
    # ==========================================

    nombre_origen = input(
        "\nIngrese el nombre de la estación de origen: "
    ).strip()

    nombre_destino = input(
        "Ingrese el nombre de la estación de destino: "
    ).strip()


    # ==========================================
    # 7. BUSCAR ID DE LAS ESTACIONES
    # ==========================================

    estaciones = base.estaciones


    origen_encontrado = estaciones[
        estaciones["stop_name"].str.strip().str.lower()
        == nombre_origen.lower()
    ]


    destino_encontrado = estaciones[
        estaciones["stop_name"].str.strip().str.lower()
        == nombre_destino.lower()
    ]


    # ==========================================
    # 8. VALIDAR ESTACIÓN DE ORIGEN
    # ==========================================

    if origen_encontrado.empty:

        print(
            f"\nLa estación de origen "
            f"'{nombre_origen}' no existe."
        )

        return


    # ==========================================
    # 9. VALIDAR ESTACIÓN DE DESTINO
    # ==========================================

    if destino_encontrado.empty:

        print(
            f"\nLa estación de destino "
            f"'{nombre_destino}' no existe."
        )

        return


    # ==========================================
    # 10. OBTENER LOS ID
    # ==========================================

    origen = origen_encontrado.iloc[0][
        "stop_id"
    ]

    destino = destino_encontrado.iloc[0][
        "stop_id"
    ]


    # ==========================================
    # 11. VALIDAR ESTACIONES
    # ==========================================

    if not reglas.estacion_existe(origen):

        print(
            f"\nLa estación de origen "
            f"'{origen}' no existe."
        )

        return


    if not reglas.estacion_existe(destino):

        print(
            f"\nLa estación de destino "
            f"'{destino}' no existe."
        )

        return


    # ==========================================
    # 12. BUSCAR RUTA
    # ==========================================

    resultado = motor.buscar_ruta(
        origen,
        destino
    )


    # ==========================================
    # 13. ANALIZAR RESULTADO
    # ==========================================

    informacion = motor.analizar_ruta(
        resultado
    )


    # ==========================================
    # 14. MOSTRAR RESULTADO
    # ==========================================

    print(
        "\n========================================"
    )

    print(
        "       SISTEMA INTELIGENTE DE RUTAS"
    )

    print(
        "========================================"
    )


    print(
        f"\nOrigen: {nombre_origen}"
    )

    print(
        f"Destino: {nombre_destino}"
    )

    print(
        f"ID origen: {origen}"
    )

    print(
        f"ID destino: {destino}"
    )


    if informacion is None:

        print(
            "\nNo existe una ruta "
            "entre las estaciones."
        )

        return


    estaciones_ruta = (
        informacion[
            "estaciones"
        ]
    )


    print(
        "\n----------------------------------------"
    )

    print(
        "RUTA ENCONTRADA"
    )

    print(
        "----------------------------------------"
    )


    for numero, stop_id in enumerate(
        estaciones_ruta,
        start=1
    ):

        estacion = base.estaciones[
            base.estaciones[
                "stop_id"
            ] == stop_id
        ]


        nombre = estacion.iloc[0][
            "stop_name"
        ]


        print(
            f"{numero}. {nombre}"
        )


    print(
        "\n----------------------------------------"
    )

    print(
        "RESULTADOS"
    )

    print(
        "----------------------------------------"
    )


    print(
        f"Conexiones  : "
        f"{informacion['conexiones']}"
    )


    print(
        f"Estaciones  : "
        f"{len(estaciones_ruta)}"
    )


    print(
        f"Transbordos : "
        f"{informacion['transbordos']}"
    )


    print(
        f"Costo       : "
        f"{informacion['costo']}"
    )


    print(
        "\n========================================"
    )


if __name__ == "__main__":

    main()