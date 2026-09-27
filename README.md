# Sistema Inteligente de Rutas - TransMilenio

Proyecto universitario desarrollado en Python para encontrar una ruta entre dos estaciones del sistema TransMilenio utilizando una base de conocimiento, reglas y búsqueda sobre un grafo.

## Requisitos

Antes de ejecutar el proyecto se necesita:

* Python 3.10 o superior.
* Git.
* Conexión a Internet para descargar el repositorio y las dependencias.

## 1. Clonar el repositorio

Abrir una terminal y ejecutar:

```bash
git clone URL_DEL_REPOSITORIO
```

Entrar a la carpeta del proyecto:

```bash
cd sistema_rutas
```

> Reemplazar `https://github.com/acaycedo/busqueda_reglas_GTFS.git` por la URL del repositorio de GitHub.

## 2. Instalar las dependencias

Ejecutar:

```bash
pip install -r requirements.txt
```

Las principales bibliotecas utilizadas son:

* `pandas`: lectura y procesamiento de los archivos GTFS.
* `networkx`: construcción y manejo del grafo de estaciones.

`heapq` forma parte de Python, por lo que no necesita instalarse.

## 3. Preparar los archivos GTFS

Los datos GTFS se encuentran comprimidos en:

```text
datos/
└── gtfs.zip
```

Es necesario descomprimir el archivo antes de ejecutar el programa.

La estructura debe quedar así:

```text
datos/
└── gtfs/
    ├── routes.txt
    ├── trips.txt
    ├── stop_times.txt
    └── stops.txt
```

### Windows

Hacer clic derecho sobre `gtfs.zip` y seleccionar **Extraer todo...**

La carpeta resultante debe llamarse `gtfs` y quedar dentro de la carpeta `datos`.


> Verificar que los archivos `.txt` estén directamente dentro de `datos/gtfs/`.

## 4. Ejecutar el programa

Desde la carpeta principal del proyecto:

```bash
python main.py
```

El programa solicitará el nombre de la estación de origen y la estación de destino.

Ejemplo:

```text
Ingrese el nombre de la estación de origen: AC 63 - KR 111
Ingrese el nombre de la estación de destino: AC 1 - KR 5A
```

El sistema mostrará:

* Estación de origen.
* Estación de destino.
* ID de las estaciones.
* Ruta encontrada.
* Estaciones del recorrido.
* Número de conexiones.
* Número de transbordos.
* Costo calculado.

## 5. Estructura del proyecto

```text
sistema_rutas_transmilenio/
│
├── main.py
├── requirements.txt
├── README.md
│
├── datos/
│   └── gtfs.zip
│
├── fuentes/
│   ├── __init__.py
│   └── gtfs_loader.py
│
├── conocimiento/
│   ├── __init__.py
│   ├── base_conocimiento.py
│   └── reglas.py
│
└── motor/
    ├── __init__.py
    ├── grafo.py
    └── rutas.py
```

## 6. Flujo del sistema

```text
Archivos GTFS
     ↓
GTFSLoader
     ↓
Base de conocimiento
     ↓
Reglas
     ↓
Construcción del grafo
     ↓
Motor de búsqueda
     ↓
Origen y destino
     ↓
Ruta encontrada
     ↓
Resultados
```

## 7. Solución de problemas

### No se encuentran los archivos GTFS

Si aparece un error relacionado con:

```text
routes.txt
stops.txt
trips.txt
stop_times.txt
```

verificar que la estructura sea:

```text
datos/
└── gtfs/
    ├── routes.txt
    ├── trips.txt
    ├── stop_times.txt
    └── stops.txt
```

### No se encuentra pandas o networkx

Si aparece un error como:

```text
ModuleNotFoundError: No module named 'pandas'
```

ejecutar:

```bash
pip install -r requirements.txt
```

### No se encuentra una estación

El nombre ingresado debe coincidir con el nombre registrado en los datos GTFS.

Por ejemplo:

```text
AC 63 - KR 111
```

Si no existe, el sistema informará que la estación no fue encontrada.

## Tecnologías utilizadas

* Python
* Pandas
* NetworkX
* GTFS
* Búsqueda en grafos
* Sistemas basados en reglas

## Objetivo

Desarrollar un sistema inteligente capaz de encontrar una ruta entre dos estaciones del sistema TransMilenio utilizando una base de conocimiento construida a partir de datos GTFS, reglas de validación y un algoritmo de búsqueda sobre un grafo.
