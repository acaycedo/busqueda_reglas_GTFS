
"""Agrupa viajes del GTFS para encontrar patrones de comportamiento similares.

Este script lee los archivos GTFS, calcula características de cada recorrido y
usa K-Means para descubrir grupos de viajes con comportamiento parecidos según
la cantidad de paradas, la hora de salida y la duración total.
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt


# Rutas del proyecto
RAIZ = Path(__file__).resolve().parent.parent
CARPETA_GTFS = RAIZ / "datos" / "gtfs"
CARPETA_SALIDA = RAIZ / "aprendizaje"

ARCHIVO_VIAJES = CARPETA_GTFS / "trips.txt"
ARCHIVO_HORARIOS = CARPETA_GTFS / "stop_times.txt"


def main():
    """Carga los viajes, los agrupa y guarda resultados visuales y tabulares.

    El objetivo es identificar agrupaciones naturales dentro del conjunto de
    viajes para entender si existen perfiles recurrentes, por ejemplo recorridos
    cortos matutinos, viajes largos nocturnos o trayectos con muchas paradas.
    """
    print("Cargando archivos GTFS...")

    # Cargamos las tablas básicas del GTFS:
    # - trips.txt: relación entre trip_id y route_id.
    # - stop_times.txt: la secuencia de paradas y las horas de llegada/salida.
    viajes = pd.read_csv(
        ARCHIVO_VIAJES,
        dtype={"trip_id": str, "route_id": str}
    )

    horarios = pd.read_csv(
        ARCHIVO_HORARIOS,
        dtype={"trip_id": str}
    )

    # El GTFS guarda las horas como texto, por eso se convierten a timedeltas.
    # Esto permite restar tiempos y calcular la duración real del servicio.
    horarios["arrival_td"] = pd.to_timedelta(
        horarios["arrival_time"], errors="coerce"
    )
    horarios["departure_td"] = pd.to_timedelta(
        horarios["departure_time"], errors="coerce"
    )

    horarios["stop_sequence"] = pd.to_numeric(
        horarios["stop_sequence"], errors="coerce"
    )

    horarios = horarios.dropna(
        subset=["trip_id", "stop_sequence"]
    )

    horarios = horarios.sort_values(
        ["trip_id", "stop_sequence"]
    )

    # En este bloque resumimos cada viaje con 3 atributos clave:
    # - primera_salida: cuándo comienza el recorrido,
    # - ultima_llegada: cuándo termina,
    # - cantidad_paradas: cuánto dura la ruta en términos de etapas.
    caracteristicas = horarios.groupby("trip_id").agg(
        primera_salida=("departure_td", "first"),
        ultima_llegada=("arrival_td", "last"),
        cantidad_paradas=("stop_sequence", "count")
    ).reset_index()

    # Relacionamos el resumen del viaje con la ruta a la que pertenece.
    datos = viajes[["trip_id", "route_id"]].merge(
        caracteristicas, on="trip_id", how="inner"
    )

    # La duración del viaje se calcula como la diferencia entre la última llegada
    # y la primera salida, transformada a minutos.
    datos["duracion_min"] = (
        datos["ultima_llegada"] - datos["primera_salida"]
    ).dt.total_seconds() / 60

    # También extraemos la hora de salida para detectar patrones según el horario.
    datos["hora_salida"] = (
        datos["primera_salida"].dt.total_seconds() / 3600
    ) % 24

    # Dejamos solo los registros completos y coherentes para evitar valores nulos o
    # viajes imposibles que puedan distorsionar el agrupamiento.
    datos = datos.dropna(
        subset=[
            "route_id",
            "cantidad_paradas",
            "duracion_min",
            "hora_salida"
        ]
    )

    datos = datos[
        (datos["cantidad_paradas"] >= 2)
        & (datos["duracion_min"] > 0)
    ].copy()

    print(f"Viajes válidos: {len(datos):,}")

    if len(datos) < 5:
        raise ValueError("No hay suficientes viajes para agrupar.")

    # Estas son las tres características que definen el perfil del viaje para la
    # agrupación: cuántas paradas tiene, a qué hora sale y cuánto tarda.
    variables = [
        "cantidad_paradas",
        "hora_salida",
        "duracion_min"
    ]

    X = datos[variables]

    # Antes de aplicar K-Means, escalamos las variables para que ninguna domine a
    # otra solo por tener valores con mayor magnitud.
    escalador = StandardScaler()
    X_escalado = escalador.fit_transform(X)

    # K-Means busca agrupar los viajes en cuatro perfiles similares.
    modelo = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10
    )

    datos["cluster"] = modelo.fit_predict(X_escalado)

    # Creamos la carpeta de resultados para guardar las gráficas del análisis.
    carpeta_graficos = CARPETA_SALIDA / "graficos"
    carpeta_graficos.mkdir(parents=True, exist_ok=True)

    # Tomamos una muestra pequeña para dibujar la comparación más rápido y con
    # menos carga computacional, sin perder el sentido general del resultado.
    muestra_grafico = datos.sample(
        n=min(5000, len(datos)),
        random_state=42
    )

    # Gráfica 1: cada punto representa un viaje; los colores muestran a qué grupo
    # pertenece de acuerdo con su cantidad de paradas y duración.
    plt.figure(figsize=(9, 6))

    for grupo in sorted(muestra_grafico["cluster"].unique()):
        parte = muestra_grafico[
            muestra_grafico["cluster"] == grupo
        ]

        plt.scatter(
            parte["cantidad_paradas"],
            parte["duracion_min"],
            label=f"Grupo {grupo}",
            alpha=0.45,
            s=12
        )

    plt.xlabel("Cantidad de paradas")
    plt.ylabel("Duración programada (minutos)")
    plt.title("Agrupamiento de viajes mediante K-Means")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        carpeta_graficos / "no_supervisado_clusters.png",
        dpi=150
    )
    plt.close()

    # Gráfica 2: muestra la duración promedio de cada grupo para que sea fácil
    # identificar qué tipo de servicio domina en cada cluster.
    duraciones = datos.groupby("cluster")["duracion_min"].mean()

    plt.figure(figsize=(8, 5))
    duraciones.plot(kind="bar")

    plt.xlabel("Grupo")
    plt.ylabel("Duración media (minutos)")
    plt.title("Duración programada media por grupo")
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        carpeta_graficos / "no_supervisado_duracion_media.png",
        dpi=150
    )
    plt.close()

    print("Gráficas guardadas en:", carpeta_graficos)

    # La silueta mide qué tan bien definidos están los grupos: valores cercanos a 1
    # indican separación clara entre clusters, mientras que valores cercanos a 0
    # sugieren que los grupos están muy mezclados.
    muestra = X_escalado[
        :min(5000, len(X_escalado))
    ]

    etiquetas_muestra = datos["cluster"].iloc[
        :len(muestra)
    ]

    silueta = silhouette_score(
        muestra,
        etiquetas_muestra
    )

    print("\n--- Evaluación del agrupamiento ---")
    print(f"Coeficiente de silueta: {silueta:.3f}")

    # Resumimos cada grupo para entender qué define a cada cluster.
    resumen = datos.groupby("cluster").agg(
        cantidad_viajes=("trip_id", "count"),
        rutas_distintas=("route_id", "nunique"),
        promedio_paradas=("cantidad_paradas", "mean"),
        promedio_hora=("hora_salida", "mean"),
        promedio_duracion=("duracion_min", "mean")
    ).round(2)

    print("\n--- Características de los grupos ---")
    print(resumen.to_string())

    # Guardamos los resultados para que puedan reutilizarse en análisis posteriores
    # o en una evaluación más detallada del comportamiento de los viajes.
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

    columnas_resultado = [
        "trip_id",
        "route_id",
        "cantidad_paradas",
        "hora_salida",
        "duracion_min",
        "cluster"
    ]

    datos[columnas_resultado].to_csv(
        CARPETA_SALIDA / "resultados_agrupamiento.csv",
        index=False
    )

    resumen.to_csv(
        CARPETA_SALIDA / "resumen_clusters.csv"
    )

    joblib.dump(
        {
            "escalador": escalador,
            "modelo": modelo,
            "variables": variables
        },
        CARPETA_SALIDA / "modelo_agrupamiento.joblib"
    )

    print("\nArchivos generados en:", CARPETA_SALIDA)


if __name__ == "__main__":
    main()
