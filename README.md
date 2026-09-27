# Procesador de Inventario v3 — DIMAULE SpA

## Descripción

Proyecto desarrollado para la Unidad 3 de Programación en Python.

El programa procesa el inventario del Centro de Distribución de DIMAULE SpA, valida datos de entrada, identifica registros inválidos, calcula reposiciones, detecta productos de extrema urgencia y genera un archivo CSV con órdenes de compra urgentes.

La solución fue desarrollada bajo un enfoque iterativo ágil, utilizando control de versiones con Git y un tablero Kanban.

## Requisitos

- Python 3.10 o superior.
- Git.
- Editor de código, recomendado Visual Studio Code.
- No requiere librerías externas.

El proyecto utiliza exclusivamente librerías estándar de Python:

- `csv`
- `logging`
- `os`
- `re`

## Estructura del proyecto

```text
procesador_inventario_v3/
│
├── data/
│   └── inventario_cd.csv
│
├── analisis_script_base.md
├── errores.log
├── ordenes_compra_urgente_v3.csv
├── procesador_inventario_v2.py
├── procesador_inventario_v3.py
└── README.md
```

## Ejecución

Desde una terminal ubicada en la carpeta principal del proyecto, ejecutar:

```powershell
python procesador_inventario_v3.py
```

## Archivo de entrada

El programa utiliza el archivo:

```text
data/inventario_cd.csv
```

El archivo debe tener las siguientes columnas:

```text
id_producto
producto
categoria
stock_actual
stock_minimo
stock_maximo
demanda_semanal
costo_unitario
proveedor
lead_time_dias
```

## Validaciones aplicadas

El programa aplica las siguientes reglas de negocio:

- RN-01: Los stocks, demanda semanal y lead time deben ser enteros mayores o iguales a cero.
- RN-02: El costo unitario debe ser mayor que cero.
- RN-03: El stock mínimo no puede ser mayor que el stock máximo.
- RN-04: El lead time debe estar entre 1 y 30 días.
- RN-05: La categoría debe pertenecer al catálogo autorizado.
- RN-06: El proveedor no puede estar vacío.
- RN-07: El identificador debe tener una letra mayúscula seguida de tres dígitos.

## Resultados generados

Después de una ejecución exitosa se generan o actualizan los siguientes archivos:

```text
ordenes_compra_urgente_v3.csv
errores.log
```

El archivo `ordenes_compra_urgente_v3.csv` incluye solamente productos válidos de extrema urgencia: productos bajo su stock mínimo y con lead time superior a cinco días.

El archivo `errores.log` registra eventos, advertencias, errores de validación y errores críticos con fecha, hora, nivel y contexto.

## Manejo de errores

El programa maneja de manera controlada, entre otros, los siguientes casos:

- Archivo de entrada inexistente.
- Falta de permisos para lectura o escritura.
- Datos numéricos inválidos.
- Registros que incumplen reglas de negocio.
- Errores inesperados durante la ejecución.

## Autor

Ignacio Barria Llanca

## Repositorio

https://github.com/ignaciobarriarll/procesador_inventario_v3