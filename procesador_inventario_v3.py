# ---------------------------------------------------------
# PROYECTO: procesador_inventario_v3
# CURSO: Programación en Python - Unidad 3
# CASO: DIMAULE SpA - Centro de Distribución Curicó
# OBJETIVO: Validar y procesar datos de inventario de forma
# robusta, trazable y modular.
# ---------------------------------------------------------

import re


# =========================================================
# CONFIGURACIÓN GLOBAL
# =========================================================

RUTA_ENTRADA = "data/inventario_cd.csv"
RUTA_SALIDA = "ordenes_compra_urgente_v3.csv"
RUTA_LOG = "errores.log"

CATEGORIAS_VALIDAS = {
    "Alimentos",
    "Bebestibles",
    "Limpieza",
    "Higiene Personal",
    "Cuidado Mascotas",
    "Lácteos"
}

CAMPOS_ENTEROS = (
    "stock_actual",
    "stock_minimo",
    "stock_maximo",
    "demanda_semanal",
    "lead_time_dias"
)

PATRON_ID = re.compile(r"^[A-Z]\d{3}$")


# =========================================================
# VALIDACIONES
# =========================================================

def validar_tipos(registro):
    """
    Convierte los campos numéricos de un registro a int o float.

    Parámetros:
        registro (dict): Diccionario con los valores crudos leídos
        desde una fila del archivo CSV.

    Retorna:
        tuple: (es_valido, registro_convertido, errores), donde
        es_valido es True si no se detectan errores de conversión,
        registro_convertido contiene los valores transformados y
        errores es una lista de mensajes de validación.
    """
    registro_convertido = registro.copy()
    errores = []

    id_producto = str(registro.get("id_producto", "")).strip()

    for campo in CAMPOS_ENTEROS:
        valor_original = registro.get(campo)

        try:
            registro_convertido[campo] = int(valor_original)
        except (ValueError, TypeError):
            errores.append(
                f"id_producto={id_producto or '<sin id>'} | "
                f"columna={campo} | "
                f"valor_recibido={valor_original!r} | "
                f"regla=TIPO | "
                f"Error: se esperaba un número entero."
            )

    valor_costo = registro.get("costo_unitario")

    try:
        registro_convertido["costo_unitario"] = float(valor_costo)
    except (ValueError, TypeError):
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=costo_unitario | "
            f"valor_recibido={valor_costo!r} | "
            f"regla=TIPO | "
            f"Error: se esperaba un número decimal mayor que cero."
        )

    for campo_texto in ("id_producto", "producto", "categoria", "proveedor"):
        valor = registro.get(campo_texto, "")
        registro_convertido[campo_texto] = str(valor).strip()

    return len(errores) == 0, registro_convertido, errores


def validar_reglas_negocio(registro):
    """
    Verifica las reglas de negocio RN-01 a RN-07 de un registro
    cuyos tipos numéricos ya fueron convertidos correctamente.

    Parámetros:
        registro (dict): Diccionario con datos previamente convertidos.

    Retorna:
        tuple: (es_valido, errores), donde es_valido es True si el
        registro cumple todas las reglas de negocio y errores contiene
        los incumplimientos detectados.
    """
    errores = []
    id_producto = registro.get("id_producto", "").strip()

    # RN-01: Campos numéricos enteros mayores o iguales a cero.
    for campo in CAMPOS_ENTEROS:
        valor = registro.get(campo)

        if valor < 0:
            errores.append(
                f"id_producto={id_producto or '<sin id>'} | "
                f"columna={campo} | "
                f"valor_recibido={valor!r} | "
                f"regla=RN-01 | "
                f"Error: el valor debe ser un entero mayor o igual a cero."
            )

    # RN-02: El costo unitario debe ser estrictamente mayor que cero.
    costo_unitario = registro.get("costo_unitario")

    if costo_unitario <= 0:
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=costo_unitario | "
            f"valor_recibido={costo_unitario!r} | "
            f"regla=RN-02 | "
            f"Error: el costo unitario debe ser mayor que cero."
        )

    # RN-03: El stock mínimo no puede ser superior al stock máximo.
    stock_minimo = registro.get("stock_minimo")
    stock_maximo = registro.get("stock_maximo")

    if stock_minimo > stock_maximo:
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=stock_minimo/stock_maximo | "
            f"valor_recibido={stock_minimo}/{stock_maximo} | "
            f"regla=RN-03 | "
            f"Error: stock_minimo no puede ser mayor que stock_maximo."
        )

    # RN-04: El lead time debe estar entre 1 y 30 días.
    lead_time_dias = registro.get("lead_time_dias")

    if not 1 <= lead_time_dias <= 30:
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=lead_time_dias | "
            f"valor_recibido={lead_time_dias!r} | "
            f"regla=RN-04 | "
            f"Error: el lead time debe estar entre 1 y 30 días."
        )

    # RN-05: La categoría debe existir en el catálogo autorizado.
    categoria = registro.get("categoria", "")

    if categoria not in CATEGORIAS_VALIDAS:
        categorias_permitidas = ", ".join(sorted(CATEGORIAS_VALIDAS))

        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=categoria | "
            f"valor_recibido={categoria!r} | "
            f"regla=RN-05 | "
            f"Error: categoría no válida. Categorías permitidas: "
            f"{categorias_permitidas}."
        )

    # RN-06: El proveedor no debe quedar vacío luego de aplicar strip().
    proveedor = registro.get("proveedor", "").strip()

    if not proveedor:
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=proveedor | "
            f"valor_recibido={proveedor!r} | "
            f"regla=RN-06 | "
            f"Error: el proveedor no puede estar vacío."
        )

    # RN-07: ID con una letra mayúscula y tres dígitos.
    if not PATRON_ID.fullmatch(id_producto):
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=id_producto | "
            f"valor_recibido={id_producto!r} | "
            f"regla=RN-07 | "
            f"Error: el identificador debe tener una letra mayúscula "
            f"seguida de tres dígitos, por ejemplo P001."
        )

    return len(errores) == 0, errores