
"""Entrena un modelo de regresión para estimar la duración de un viaje.

Este script toma la información de los archivos GTFS, prepara una base de datos
con las características más importantes del recorrido y luego entrena un
Random Forest para predecir la duración total del viaje en minutos.
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt


# Ubicación de los archivos del proyecto
BASE = Path(__file__).resolve().parents[1]
DATOS = BASE / "datos" / "gtfs"


def preparar_datos():
    """Lee GTFS y prepara una tabla con las variables útiles para predecir.

    La idea es transformar los datos crudos de trips.txt y stop_times.txt en un
    conjunto de filas donde cada viaje tiene información como:
    - la ruta a la que pertenece,
    - cuántas paradas tiene,
    - a qué hora sale,
    - y cuánto dura en minutos.
    """
    print("Cargando archivos GTFS...")

    # Primero cargamos las dos tablas principales de GTFS:
    # - trips.txt: identifica cada viaje y la ruta a la que pertenece.
    # - stop_times.txt: guarda la hora de salida/llegada de cada parada.
    viajes = pd.read_csv(
        DATOS / "trips.txt",
        usecols=["trip_id", "route_id"],
        dtype={"trip_id": str, "route_id": str},
    )

    horarios = pd.read_csv(
        DATOS / "stop_times.txt",
        usecols=[
            "trip_id",
            "arrival_time",
            "departure_time",
            "stop_sequence",
        ],
        low_memory=False,
    )

    # GTFS almacena las horas como texto (por ejemplo, "08:15:00").
    # Para poder calcular tiempos, las convertimos a objetos de duración.
    horarios["arrival"] = pd.to_timedelta(
        horarios["arrival_time"], errors="coerce"
    )
    horarios["departure"] = pd.to_timedelta(
        horarios["departure_time"], errors="coerce"
    )

    horarios = horarios.dropna(
        subset=["arrival", "departure", "stop_sequence"]
    )
    horarios = horarios.sort_values(["trip_id", "stop_sequence"])

    # Para cada viaje, calculamos el momento en que sale y llega por última vez.
    # Con eso podemos inferir la duración total del recorrido y la hora de salida.
    resumen = horarios.groupby("trip_id").agg(
        salida=("departure", "first"),
        llegada=("arrival", "last"),
        cantidad_paradas=("stop_sequence", "count"),
    )

    resumen["duracion_min"] = (
        resumen["llegada"] - resumen["salida"]
    ).dt.total_seconds() / 60

    resumen["hora_salida"] = (
        resumen["salida"].dt.total_seconds() / 3600
    ) % 24

    # Unimos la información del viaje con la ruta asociada.
    datos = resumen.reset_index().merge(
        viajes.drop_duplicates("trip_id"),
        on="trip_id",
        how="inner",
    )

    # Eliminamos registros anómalos: duración no válida, rutas faltantes o viajes
    # demasiado cortos para ser representativos.
    datos = datos[
        (datos["duracion_min"] > 0)
        & datos["route_id"].notna()
        & (datos["cantidad_paradas"] >= 2)
    ].copy()

    return datos[
        ["route_id", "cantidad_paradas", "hora_salida", "duracion_min"]
    ]


def entrenar():
    """Entrena y evalúa el modelo predictivo para estimar tiempos de viaje.

    El flujo es el siguiente:
    1. prepara la base de datos limpia,
    2. separa entrenamiento y prueba,
    3. transforma la columna de ruta con OneHotEncoder técnica de preprocesamiento de datos en aprendizaje automático,
    4. entrena un Random Forest,
    5. calcula métricas y guarda el modelo y gráficas.
    """
    datos = preparar_datos()

    print(f"Viajes válidos encontrados: {len(datos):,}")

    # Las variables que usamos para predecir son la ruta, la cantidad de paradas
    # y la hora de salida; la duración en minutos es la variable objetivo.
    X = datos[["route_id", "cantidad_paradas", "hora_salida"]]
    y = datos["duracion_min"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    # El codificador convierte rutas textuales en columnas binarias, mientras que
    # las demás características se dejan tal cual para que el modelo pueda usarlas.
    procesador = ColumnTransformer([
    (
        "ruta",
        OneHotEncoder(handle_unknown="ignore"),
        ["route_id"],
    ),
    (
        "numericas",
        "passthrough",
        ["cantidad_paradas", "hora_salida"],
    ),
    ])

    modelo = Pipeline([
        ("procesamiento", procesador),
        (
            "regresor",
            RandomForestRegressor(
                n_estimators=50,
                random_state=42,
                n_jobs=-1,
                min_samples_leaf=3,
            ),
        ),
    ])

    # Entrenamiento del algoritmo: el Random Forest aprende patrones a partir de
    # muchos árboles que combinan decisiones sobre las variables de entrada.
    print("Entrenando modelo...")
    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)

    # Guardamos los gráficos en una carpeta de resultados para revisar visualmente
    # si las predicciones se parecen a los valores reales.
    carpeta_graficos = BASE / "aprendizaje" / "graficos"
    carpeta_graficos.mkdir(parents=True, exist_ok=True)

    # Gráfico 1: comparación entre la duración real y la que predice el modelo.
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, predicciones, alpha=0.25, s=10)

    limite_min = min(y_test.min(), predicciones.min())
    limite_max = max(y_test.max(), predicciones.max())

    plt.plot(
        [limite_min, limite_max],
        [limite_min, limite_max],
        linestyle="--",
        label="Predicción ideal",
    )

    plt.xlabel("Duración real (minutos)")
    plt.ylabel("Duración predicha (minutos)")
    plt.title("Random Forest: valores reales frente a predicciones")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        carpeta_graficos / "supervisado_predicciones.png",
        dpi=150,
    )
    plt.close()

    # Gráfico 2: comparamos el error del modelo contra una referencia simple:
    # predecir siempre el promedio de duración de entrenamiento.
    mae_modelo = mean_absolute_error(y_test, predicciones)
    mae_media = mean_absolute_error(
        y_test, [y_train.mean()] * len(y_test)
    )

    plt.figure(figsize=(7, 5))
    plt.bar(
        ["Random Forest", "Predicción de la media"],
        [mae_modelo, mae_media],
    )
    plt.ylabel("Error absoluto medio (minutos)")
    plt.title("Comparación del error de predicción")
    plt.tight_layout()
    plt.savefig(
        carpeta_graficos / "supervisado_comparacion_mae.png",
        dpi=150,
    )
    plt.close()

    print(f"Gráficos supervisados guardados en: {carpeta_graficos}")

    # En esta sección calculamos métricas para comparar el modelo con una línea de
    # base muy simple: si siempre se adivina la media del conjunto de entrenamiento.
    prediccion_media = [y_train.mean()] * len(y_test)

    print("\n--- Comparación con una referencia sencilla ---")

    for nombre, valores in [
        ("Modelo Random Forest", predicciones),
        ("Predicción de la media", prediccion_media),
    ]:
        mae = mean_absolute_error(y_test, valores)
        rmse = mean_squared_error(y_test, valores) ** 0.5
        r2 = r2_score(y_test, valores)

        print(f"\n{nombre}")
        print(f"MAE:  {mae:.2f} minutos")
        print(f"RMSE: {rmse:.2f} minutos")
        print(f"R²:   {r2:.3f}")

    # Guardamos el modelo entrenado para reutilizarlo más tarde en producción o
    # en nuevas pruebas sin tener que volver a entrenar.
    salida_modelo = BASE / "aprendizaje" / "modelo_duracion.joblib"
    joblib.dump(modelo, salida_modelo)

    print(f"\nModelo guardado en: {salida_modelo}")

    # Segunda evaluación: separamos los datos por ruta, no por viaje individual.
    # Esto permite comprobar qué tan bien generaliza el modelo para rutas que no
    # fueron vistas durante el entrenamiento.
    print("\n--- Evaluación con rutas no vistas ---")

    divisor = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=42,
    )

    indices_train, indices_test = next(
        divisor.split(
            datos,
            datos["duracion_min"],
            groups=datos["route_id"],
        )
    )

    X_train_r = X.iloc[indices_train]
    X_test_r = X.iloc[indices_test]
    y_train_r = y.iloc[indices_train]
    y_test_r = y.iloc[indices_test]

    modelo_rutas = Pipeline([
        ("procesamiento", procesador),
        (
            "regresor",
            RandomForestRegressor(
                n_estimators=50,
                random_state=42,
                n_jobs=-1,
                min_samples_leaf=3,
            ),
        ),
    ])

    modelo_rutas.fit(X_train_r, y_train_r)
    pred_rutas = modelo_rutas.predict(X_test_r)

    print(f"Rutas para entrenar: {X_train_r['route_id'].nunique()}")
    print(f"Rutas para probar: {X_test_r['route_id'].nunique()}")
    print(f"MAE:  {mean_absolute_error(y_test_r, pred_rutas):.2f} minutos")
    print(
        f"RMSE: {mean_squared_error(y_test_r, pred_rutas) ** 0.5:.2f} minutos"
    )
    print(f"R²:   {r2_score(y_test_r, pred_rutas):.3f}")



if __name__ == "__main__":
    entrenar()
