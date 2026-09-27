# Informe Ejecutivo — Procesador de Inventario v3

**Empresa:** DIMAULE SpA  
**Área:** Centro de Distribución, Curicó  
**Proyecto:** Robustez operacional y ciclo ágil de mejora  
**Fecha:** Septiembre de 2026  

## Resumen de resultados

Se desarrolló una versión 3.0 del procesador de inventario de DIMAULE SpA para fortalecer la continuidad operacional del proceso de reposición. La nueva solución reemplaza el script monolítico de la Unidad 2 por una aplicación modular, validada y trazable.

Durante la ejecución con el archivo de inventario se leyeron 500 registros. De ellos, 362 fueron considerados válidos y 138 fueron descartados por incumplir reglas de negocio. El motivo principal de descarte fue RN-05, asociado a categorías que no pertenecen al catálogo autorizado. Esta situación evidencia la necesidad de revisar la estandarización de categorías provenientes del WMS antes de que la información sea utilizada para decisiones de abastecimiento.

El programa identificó 25 productos de extrema urgencia. Estos casos corresponden a productos válidos cuyo stock actual está por debajo del stock mínimo y cuyo plazo de reposición es superior a cinco días. Para los productos bajo stock válidos se estimó una reposición total de 21.723 unidades, con un costo aproximado de $37.309.170.

## Recomendación logística

Se recomienda al Jefe del Centro de Distribución priorizar inmediatamente las 25 órdenes de compra urgente generadas por el sistema, debido a que combinan riesgo de quiebre de stock con tiempos de reposición superiores a cinco días. Estas órdenes deben ser revisadas con los proveedores correspondientes y gestionadas antes de la siguiente planificación semanal.

Adicionalmente, se recomienda establecer una validación previa en el WMS para impedir el ingreso de categorías no autorizadas. La presencia de 138 registros descartados por categoría afecta la calidad de los análisis y podría ocultar productos críticos si no se corrige el catálogo maestro. Como medida de mejora continua, se propone revisar periódicamente `errores.log` y asignar la corrección de los registros descartados al equipo responsable de calidad de datos.

## Mejoras implementadas

La versión 3.0 incorporó funciones con responsabilidad única para lectura del CSV, validación de tipos, validación de reglas de negocio, cálculo de reposición, generación de salida y reporte por consola. También se agregó manejo de excepciones para archivo inexistente, permisos, errores de tipo y errores de valor.

El archivo `errores.log` permite identificar fecha, hora, nivel, mensaje y contexto del producto afectado. El proyecto mantiene trazabilidad mediante commits en GitHub y un tablero Kanban que registra las actividades de cada fase.

## Caso de depuración y traceback

Durante una prueba controlada de desarrollo se ejecutó la función de cálculo utilizando un registro no validado cuyo campo `stock_actual` contenía el texto `N/A`. El traceback obtenido fue similar al siguiente:

```text
Traceback (most recent call last):
  File "prueba_traceback.py", line 17, in <module>
    calcular_reposicion(registro_con_error)
  File "procesador_inventario_v3.py", line 295, in calcular_reposicion
   es_bajo_stock = stock_actual < stock_minimo
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: '<' not supported between instances of 'str' and 'int'
```

La causa fue intentar restar un valor de tipo `str` a un valor de tipo `int`. La corrección aplicada consistió en asegurar que todos los registros sean procesados primero por la función `validar_tipos()`. Si la conversión falla, el registro se descarta, se registra en `errores.log` y nunca llega a `calcular_reposicion()`.