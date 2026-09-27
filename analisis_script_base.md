# Análisis del script base — Procesador de Inventario DIMAULE SpA

**Proyecto:** procesador_inventario_v3  
**Curso:** Programación en Python — Unidad 3  
**Caso:** Robustez operacional y ciclo ágil de mejora  
**Script analizado:** `procesador_inventario_v2.py`

---

## 1. Identificación de flujos

> Nota: Los números de línea corresponden al archivo `procesador_inventario_v2.py` guardado como base del proyecto.

| Tipo de flujo | Líneas aproximadas | Propósito | Variables clave |
|---|---:|---|---|
| Secuencial | 9–13 | Importar la librería estándar `csv` y definir los nombres de los archivos de entrada y salida. | `ARCHIVO_ENTRADA`, `ARCHIVO_SALIDA` |
| Secuencial | 16–21 | Inicializar contadores y acumuladores para el resumen de inventario y costos de reposición. | `total_productos`, `total_bajo_stock`, `total_sobrestock`, `total_unidades_reponer`, `costo_total_reposicion` |
| Secuencial | 24–28 | Crear listas y diccionarios para almacenar registros, órdenes de compra, alertas por proveedor, categorías críticas y productos de extrema urgencia. | `registros_inventario`, `ordenes_compra`, `alertas_por_proveedor`, `bajo_stock_por_categoria`, `casos_extrema_urgencia` |
| Secuencial | 31–32 | Abrir el archivo CSV de entrada y crear un lector `DictReader`, que permite acceder a cada columna por su nombre. | `archivo`, `lector` |
| Iterativo | 35–89 | Recorrer cada fila del archivo CSV, convertir datos, guardar registros, evaluar stock y calcular alertas de reposición. | `fila`, `stock_actual`, `stock_minimo`, `stock_maximo`, `costo_unitario`, `lead_time_dias` |
| Secuencial | 37–46 | Extraer desde cada fila los campos de texto y convertir las columnas numéricas a `int` o `float`. | `id_producto`, `producto`, `categoria`, `proveedor`, `stock_actual`, `costo_unitario` |
| Secuencial | 50–62 | Guardar el registro convertido en la lista `registros_inventario` y aumentar el total de productos procesados. | `registros_inventario`, `total_productos` |
| Condicional | 65–88 | Detectar productos bajo stock, calcular reposición, generar una orden de compra, agrupar alertas y evaluar extrema urgencia. | `stock_actual`, `stock_minimo`, `cantidad_a_reponer`, `costo_reposicion` |
| Condicional | 67–68 | Verificar si el stock actual es menor que el stock mínimo. | `stock_actual`, `stock_minimo` |
| Secuencial | 69–73 | Actualizar contadores y calcular cantidad y costo de reposición para un producto bajo stock. | `total_bajo_stock`, `cantidad_a_reponer`, `costo_reposicion`, `costo_total_reposicion` |
| Secuencial | 76–82 | Agregar el producto bajo stock a la lista de órdenes de compra. | `ordenes_compra`, `id_producto`, `producto`, `proveedor` |
| Condicional | 85–87 | Comprobar si una categoría no existe aún en el diccionario antes de inicializar su contador. | `categoria`, `bajo_stock_por_categoria` |
| Condicional | 91–93 | Comprobar si un proveedor no existe aún en el diccionario antes de inicializar su contador. | `proveedor`, `alertas_por_proveedor` |
| Condicional | 97–101 | Identificar productos bajo stock cuyo lead time es superior a cinco días, clasificándolos como extrema urgencia. | `stock_actual`, `stock_minimo`, `lead_time_dias`, `casos_extrema_urgencia` |
| Condicional | 105–106 | Detectar sobrestock cuando el stock actual supera el máximo definido. | `stock_actual`, `stock_maximo`, `total_sobrestock` |
| Iterativo | 112–115 | Recorrer el diccionario de productos bajo stock por categoría para determinar la categoría con mayor número de alertas. | `categoria`, `cantidad`, `categoria_mas_critica`, `cantidad_categoria_critica` |
| Condicional | 113–115 | Comparar cada cantidad con el máximo actual para actualizar la categoría más crítica. | `cantidad`, `cantidad_categoria_critica`, `categoria_mas_critica` |
| Secuencial | 119–135 | Definir columnas, abrir el CSV de salida, escribir encabezados y escribir las órdenes de compra acumuladas. | `columnas_salida`, `archivo_salida`, `escritor`, `ordenes_compra` |
| Secuencial | 139–146 | Mostrar por consola el resumen global de inventario, alertas y costos de reposición. | `total_productos`, `total_bajo_stock`, `total_sobrestock`, `costo_total_reposicion` |
| Iterativo | 150–151 | Recorrer el diccionario de alertas por proveedor e imprimir sus resultados. | `proveedor`, `cantidad`, `alertas_por_proveedor` |
| Iterativo | 155–156 | Recorrer los casos de extrema urgencia e imprimir identificador y producto. | `caso`, `casos_extrema_urgencia` |

---

## 2. Traza paso a paso del ciclo `for` principal

El ciclo principal corresponde a:

```python
for fila in lector:
```

Este ciclo lee cada registro del archivo `inventario_cd.csv`. En cada iteración, convierte los datos, guarda el producto en memoria, evalúa si existe bajo stock o sobrestock y actualiza los contadores y acumuladores correspondientes.

Para esta traza se utilizaron las primeras cinco filas del archivo de inventario.

| Iteración | id_producto | stock_actual | stock_minimo | ¿Bajo stock? | Cantidad a reponer | Productos críticos acumulados | Costo acumulado de reposición |
|---:|---|---:|---:|---|---:|---:|---:|
| 1 | P001 | 213 | 34 | No | 0 | 0 | $0 |
| 2 | P002 | 213 | 68 | No | 0 | 0 | $0 |
| 3 | P003 | 29 | 27 | No | 0 | 0 | $0 |
| 4 | P004 | 35 | 42 | Sí | 62 | 1 | $79.980 |
| 5 | P005 | 132 | 57 | No | 0 | 1 | $79.980 |

### Desarrollo de la cuarta iteración

En la cuarta fila se procesa el producto `P004`, Pasta dental mentol 100 ml.

```text
stock_actual = 35
stock_minimo = 42
stock_maximo = 97
costo_unitario = 1290
```

Como `35 < 42`, el producto se considera bajo stock. El programa calcula:

```text
cantidad_a_reponer = stock_maximo - stock_actual
cantidad_a_reponer = 97 - 35
cantidad_a_reponer = 62
```

Luego calcula el costo de reposición:

```text
costo_reposicion = cantidad_a_reponer * costo_unitario
costo_reposicion = 62 * 1290
costo_reposicion = 79.980
```

Por ello, al finalizar esta iteración:

```text
total_bajo_stock = 1
total_unidades_reponer = 62
costo_total_reposicion = 79.980
```

### Entradas, transformaciones y salidas del ciclo

| Elemento | Descripción |
|---|---|
| Entradas | Cada `fila` del lector CSV contiene id_producto, producto, categoría, stocks, demanda, costo, proveedor y lead time. |
| Transformaciones | Se convierten valores numéricos, se crea un diccionario de producto, se compara el stock con mínimos y máximos, se calcula reposición, se agrupan alertas y se detectan urgencias. |
| Salidas intermedias | Registros almacenados en `registros_inventario`, órdenes en `ordenes_compra`, alertas por categoría y proveedor, contadores y lista de casos urgentes. |
| Salida final | Archivo CSV de órdenes de compra y resumen de resultados impreso por consola. |

---

## 3. Análisis estructurado

El script `procesador_inventario_v2.py` procesa un archivo CSV de inventario de DIMAULE SpA para identificar productos bajo stock, calcular las unidades y costos de reposición, detectar sobrestock y destacar casos de extrema urgencia. Sus entradas son el archivo `inventario_cd.csv` y sus diez columnas: identificador, producto, categoría, stocks, demanda semanal, costo unitario, proveedor y lead time. Sus salidas son el archivo `ordenes_compra_urgente.csv` y un resumen impreso en consola.

El flujo comienza con la definición de rutas, contadores y estructuras de datos. Posteriormente, abre el archivo CSV y recorre cada fila mediante un ciclo `for`. Durante cada iteración convierte los valores numéricos, almacena el registro y aplica condiciones para detectar bajo stock, sobrestock y extrema urgencia. Al finalizar el ciclo, identifica la categoría más crítica, escribe las órdenes de compra en un nuevo CSV y muestra indicadores por consola.

El script depende de la disponibilidad del archivo de entrada, de la existencia exacta de las columnas requeridas y de que todos los valores numéricos puedan convertirse correctamente. Presenta oportunidades de mejora importantes: primero, no maneja excepciones, por lo que un archivo inexistente o un valor como `N/A` detiene toda la ejecución; segundo, no valida reglas de negocio como stock mínimo mayor al máximo, costos cero o lead time inválido; tercero, concentra todo el flujo en un único bloque de código, dificultando el mantenimiento y las pruebas; finalmente, no registra errores ni eventos en un archivo de log, por lo que no existe trazabilidad operacional.