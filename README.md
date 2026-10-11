# Análisis de viajes de TransMilenio mediante aprendizaje automático

## Descripción del proyecto

Este proyecto aplica técnicas de aprendizaje automático a datos GTFS de TransMilenio con el objetivo de analizar las características de los viajes programados. Se desarrollan dos enfoques: un modelo de aprendizaje supervisado para estimar la duración de los viajes y un modelo de aprendizaje no supervisado para identificar grupos de viajes con características similares.

## Objetivos

- Procesar y analizar datos GTFS de rutas y horarios.
- Estimar la duración programada de los viajes mediante un modelo de regresión.
- Evaluar el rendimiento del modelo supervisado con métricas de error.
- Agrupar viajes mediante técnicas de aprendizaje no supervisado.
- Visualizar e interpretar los resultados obtenidos.

## Tecnologías utilizadas

- Python
- Pandas
- Scikit-learn
- Joblib
- Matplotlib
- GTFS

## Requisitos e instalación

Se requiere Python y los archivos GTFS `trips.txt` y `stop_times.txt`.

Instala las dependencias ejecutando:

```bash
python -m pip install pandas scikit-learn joblib matplotlib
```

## Estructura del proyecto

```text
sistema_rutas_transmilenio/
├── datos/
│   └── gtfs/
│       ├── trips.txt
│       └── stop_times.txt
└── aprendizaje/
    ├── entrenar_modelo.py
    ├── agrupar_viajes.py
    └── graficos/
```

Los archivos de modelos, resultados y gráficas se generan al ejecutar los scripts.

## 1. Aprendizaje supervisado: predicción de duración

**Archivo principal:** `aprendizaje/entrenar_modelo.py`

Este modelo utiliza el algoritmo Random Forest Regressor para estimar la duración programada de los viajes a partir de tres características:

- Ruta.
- Cantidad de paradas.
- Hora de salida.

Los datos se dividen en conjuntos de entrenamiento y prueba. Para evaluar los resultados se utilizan las siguientes métricas:

- **MAE:** mide el error promedio de las predicciones en minutos.
- **RMSE:** mide el error y penaliza especialmente los errores grandes.
- **R²:** permite evaluar qué tan bien se ajusta el modelo en comparación con una referencia basada en la media.

### Resultados obtenidos

| Evaluación | MAE | RMSE | R² |
|---|---:|---:|---:|
| Random Forest, división aleatoria | 12,56 min | 19,30 min | 0,921 |
| Predicción basada en la media | 53,87 min | 68,46 min | Aproximadamente 0 |
| Evaluación con rutas no vistas | 30,25 min | 47,97 min | 0,433 |

Los resultados muestran que Random Forest supera la referencia basada en la media en la evaluación aleatoria. Sin embargo, su rendimiento disminuye cuando se evalúan rutas que no participaron en el entrenamiento, lo que evidencia la importancia de comprobar la capacidad de generalización del modelo.

### Ejecución

Desde la carpeta raíz del proyecto:

```bash
python aprendizaje/entrenar_modelo.py
```

El modelo entrenado se guarda en `aprendizaje/modelo_duracion.joblib`.

## 2. Aprendizaje no supervisado: agrupamiento de viajes

**Archivo principal:** `aprendizaje/agrupar_viajes.py`

Este modelo utiliza K-Means para agrupar los viajes en cuatro clusters según sus características, sin establecer previamente categorías.

Las variables utilizadas son:

- Cantidad de paradas.
- Hora de salida.
- Duración programada.

Antes del agrupamiento, las variables se estandarizan mediante StandardScaler. Posteriormente, se analizan los perfiles de los grupos y se calcula el coeficiente de silueta para evaluar su separación.

### Resultados obtenidos

En una ejecución se analizaron 105.122 viajes y se obtuvo un coeficiente de silueta de **0,299**.

Los grupos presentaron las siguientes características generales:

- **Cluster 0:** viajes con mayor cantidad de paradas y mayor duración promedio.
- **Cluster 1:** viajes con una cantidad elevada de paradas y duración intermedia.
- **Cluster 2:** grupo con la mayor cantidad de viajes.
- **Cluster 3:** viajes con menos paradas y menor duración promedio.

El coeficiente de silueta sugiere que existe cierta estructura en los grupos, aunque no están claramente separados. Los clusters son agrupaciones estadísticas y no categorías oficiales de TransMilenio.

### Ejecución

Desde la carpeta raíz del proyecto:

```bash
python aprendizaje/agrupar_viajes.py
```

Entre los archivos generados se encuentran:

- `aprendizaje/resultados_agrupamiento.csv`
- `aprendizaje/resumen_clusters.csv`
- `aprendizaje/modelo_agrupamiento.joblib`

## Visualización de resultados

Las gráficas permiten interpretar los resultados de ambos modelos:

- **Modelo supervisado:** comparación entre las duraciones programadas reales y las predicciones, y comparación del error medio absoluto frente a la referencia basada en la media.
- **Modelo no supervisado:** distribución de los viajes por cluster y comparación de la duración promedio de los grupos.

Las gráficas complementan las métricas y facilitan la explicación de los resultados.

## Limitaciones

- La duración se calcula a partir de los horarios programados en GTFS; no representa necesariamente el tiempo real de circulación.
- Los resultados dependen de la calidad y la versión de los datos utilizados.
- El modelo supervisado tiene un rendimiento menor cuando se evalúan rutas que no estuvieron presentes durante el entrenamiento.
- El número de clusters elegido para K-Means es una configuración inicial y no demuestra que existan exactamente cuatro categorías naturales.
- Las métricas y los perfiles pueden cambiar al utilizar otros datos o parámetros.

## Autoría

Proyecto académico de análisis de datos y aprendizaje automático aplicado a información GTFS de TransMilenio.