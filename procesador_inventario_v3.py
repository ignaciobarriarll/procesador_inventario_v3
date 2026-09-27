# ---------------------------------------------------------
# PROYECTO: procesador_inventario_v3
# CURSO: Programación en Python - Unidad 3
# CASO: DIMAULE SpA - Centro de Distribución Curicó
# OBJETIVO: Validar y procesar inventario de forma robusta,
# modular y trazable.
# ---------------------------------------------------------

import csv
import re


# =========================================================
# CONFIGURACIÓN GLOBAL
# =========================================================

RUTA_ENTRADA = "data/inventario_cd.csv"
RUTA_SALIDA = "ordenes_compra_urgente_v3.csv"

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

LEAD_TIME_URGENTE = 5

PATRON_ID = re.compile(r"^[A-Z]\d{3}$")


# =========================================================
# VALIDACIONES
# =========================================================

def validar_tipos(registro):
    """
    Convierte campos numéricos de un registro a int o float.

    Parámetros:
        registro (dict): Fila cruda leída desde el archivo CSV.

    Retorna:
        tuple: (es_valido, registro_convertido, errores).
        es_valido es True si todas las conversiones son correctas.
        registro_convertido contiene los campos con tipos adecuados.
        errores contiene los mensajes de error detectados.
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
    Verifica las reglas RN-01 a RN-07 sobre un registro convertido.

    Parámetros:
        registro (dict): Registro con campos numéricos ya convertidos.

    Retorna:
        tuple: (es_valido, errores).
        es_valido es True cuando el registro cumple todas las reglas.
        errores contiene los incumplimientos identificados.
    """
    errores = []
    id_producto = registro.get("id_producto", "").strip()

    # RN-01: Enteros mayores o iguales a cero.
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

    # RN-02: Costo unitario estrictamente mayor que cero.
    costo_unitario = registro.get("costo_unitario")

    if costo_unitario <= 0:
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=costo_unitario | "
            f"valor_recibido={costo_unitario!r} | "
            f"regla=RN-02 | "
            f"Error: el costo unitario debe ser mayor que cero."
        )

    # RN-03: Stock mínimo no puede superar el stock máximo.
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

    # RN-04: Lead time entre 1 y 30 días.
    lead_time_dias = registro.get("lead_time_dias")

    if not 1 <= lead_time_dias <= 30:
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=lead_time_dias | "
            f"valor_recibido={lead_time_dias!r} | "
            f"regla=RN-04 | "
            f"Error: el lead time debe estar entre 1 y 30 días."
        )

    # RN-05: Categoría dentro del catálogo autorizado.
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

    # RN-06: Proveedor no vacío después de aplicar strip().
    proveedor = registro.get("proveedor", "").strip()

    if not proveedor:
        errores.append(
            f"id_producto={id_producto or '<sin id>'} | "
            f"columna=proveedor | "
            f"valor_recibido={proveedor!r} | "
            f"regla=RN-06 | "
            f"Error: el proveedor no puede estar vacío."
        )

    # RN-07: Letra mayúscula seguida de tres dígitos.
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


# =========================================================
# CÁLCULOS
# =========================================================

def calcular_reposicion(registro, lead_time_urgente=LEAD_TIME_URGENTE):
    """
    Calcula la reposición, su costo y la condición de extrema urgencia.

    Parámetros:
        registro (dict): Registro válido de inventario.
        lead_time_urgente (int): Días sobre los cuales una reposición
        bajo stock se considera de extrema urgencia.

    Retorna:
        dict: Copia del registro con cantidad_a_reponer,
        costo_total_reposicion, es_bajo_stock y
        es_extrema_urgencia.
    """
    registro_calculado = registro.copy()

    stock_actual = registro_calculado["stock_actual"]
    stock_minimo = registro_calculado["stock_minimo"]
    stock_maximo = registro_calculado["stock_maximo"]
    costo_unitario = registro_calculado["costo_unitario"]
    lead_time_dias = registro_calculado["lead_time_dias"]

    es_bajo_stock = stock_actual < stock_minimo
    cantidad_a_reponer = max(0, stock_maximo - stock_actual)
    costo_total_reposicion = cantidad_a_reponer * costo_unitario

    es_extrema_urgencia = (
        es_bajo_stock
        and lead_time_dias > lead_time_urgente
    )

    registro_calculado["es_bajo_stock"] = es_bajo_stock
    registro_calculado["cantidad_a_reponer"] = cantidad_a_reponer
    registro_calculado["costo_total_reposicion"] = round(
        costo_total_reposicion,
        2
    )
    registro_calculado["es_extrema_urgencia"] = es_extrema_urgencia

    return registro_calculado


# =========================================================
# ENTRADA Y SALIDA DE ARCHIVOS
# =========================================================

def leer_csv(ruta=RUTA_ENTRADA, encoding="utf-8", separador=","):
    """
    Lee un archivo CSV y devuelve sus filas como diccionarios crudos.

    Parámetros:
        ruta (str): Ruta relativa o absoluta del archivo CSV de entrada.
        encoding (str): Codificación utilizada al abrir el archivo.
        separador (str): Carácter que separa las columnas del CSV.

    Retorna:
        list: Lista de diccionarios, uno por cada fila del archivo.
    """
    with open(ruta, mode="r", encoding=encoding, newline="") as archivo:
        lector = csv.DictReader(archivo, delimiter=separador)
        registros = list(lector)

    return registros


def escribir_csv_salida(
    ruta=RUTA_SALIDA,
    registros=None,
    encoding="utf-8"
):
    """
    Escribe las órdenes de compra urgente en un archivo CSV.

    Parámetros:
        ruta (str): Ruta del archivo CSV de salida.
        registros (list): Lista de registros urgentes ya calculados.
        encoding (str): Codificación utilizada para escribir el archivo.

    Retorna:
        int: Cantidad de órdenes escritas en el archivo de salida.
    """
    if registros is None:
        registros = []

    columnas_salida = [
        "id_producto",
        "producto",
        "cantidad_a_reponer",
        "costo_total_reposicion",
        "proveedor",
        "dias_estimados_reposicion"
    ]

    with open(
        ruta,
        mode="w",
        encoding=encoding,
        newline=""
    ) as archivo_salida:
        escritor = csv.DictWriter(
            archivo_salida,
            fieldnames=columnas_salida
        )

        escritor.writeheader()

        for registro in registros:
            fila_salida = {
                "id_producto": registro["id_producto"],
                "producto": registro["producto"],
                "cantidad_a_reponer": registro["cantidad_a_reponer"],
                "costo_total_reposicion": (
                    registro["costo_total_reposicion"]
                ),
                "proveedor": registro["proveedor"],
                "dias_estimados_reposicion": (
                    registro["lead_time_dias"]
                )
            }

            escritor.writerow(fila_salida)

    return len(registros)


# =========================================================
# REPORTE
# =========================================================

def contar_motivos_descarte(errores):
    """
    Cuenta cuántas veces aparece cada regla o tipo de error.

    Parámetros:
        errores (list): Lista de mensajes de errores de validación.

    Retorna:
        dict: Diccionario con la cantidad de descartes por regla.
    """
    motivos = {}

    for error in errores:
        partes = error.split(" | ")
        codigo_regla = "SIN_CLASIFICAR"

        for parte in partes:
            if parte.startswith("regla="):
                codigo_regla = parte.replace("regla=", "")
                break

        motivos[codigo_regla] = motivos.get(codigo_regla, 0) + 1

    return motivos


def crear_resumen(
    total_leidos,
    validos,
    descartados,
    urgentes,
    total_unidades_reponer,
    costo_total_reposicion,
    errores
):
    """
    Construye el resumen de resultados de la ejecución.

    Parámetros:
        total_leidos (int): Total de filas leídas desde el archivo.
        validos (list): Registros válidos procesados.
        descartados (list): Registros que no superaron validaciones.
        urgentes (list): Registros clasificados como extrema urgencia.
        total_unidades_reponer (int): Unidades requeridas para reposición.
        costo_total_reposicion (float): Costo de reposición acumulado.
        errores (list): Mensajes de error registrados durante validación.

    Retorna:
        dict: Resumen estructurado de la ejecución.
    """
    motivos = contar_motivos_descarte(errores)

    motivo_principal = "Sin descartes"

    if motivos:
        motivo_principal = max(motivos, key=motivos.get)

    resumen = {
        "total_leidos": total_leidos,
        "total_validos": len(validos),
        "total_descartados": len(descartados),
        "total_urgentes": len(urgentes),
        "total_unidades_reponer": total_unidades_reponer,
        "costo_total_reposicion": costo_total_reposicion,
        "motivo_principal_descarte": motivo_principal,
        "motivos_descarte": motivos
    }

    return resumen


def generar_reporte_consola(resumen):
    """
    Muestra por consola un resumen ejecutivo y una recomendación.

    Parámetros:
        resumen (dict): Diccionario generado por crear_resumen().

    Retorna:
        None: La función imprime información en consola.
    """
    print("")
    print("===== RESUMEN EJECUTIVO DIMAULE SpA =====")
    print(f"Registros leídos: {resumen['total_leidos']}")
    print(f"Registros válidos: {resumen['total_validos']}")
    print(f"Registros descartados: {resumen['total_descartados']}")
    print(f"Órdenes de extrema urgencia: {resumen['total_urgentes']}")
    print(
        "Total de unidades a reponer: "
        f"{resumen['total_unidades_reponer']}"
    )
    print(
        "Costo total de reposición: "
        f"${resumen['costo_total_reposicion']:,.0f}"
    )
    print(
        "Motivo principal de descarte: "
        f"{resumen['motivo_principal_descarte']}"
    )

    if resumen["motivos_descarte"]:
        print("")
        print("===== DESCARTES POR REGLA =====")

        for regla, cantidad in resumen["motivos_descarte"].items():
            print(f"{regla}: {cantidad}")

    print("")
    print("===== RECOMENDACIÓN AL JEFE DEL CD =====")

    if resumen["total_urgentes"] > 0:
        print(
            "Se recomienda priorizar de inmediato las órdenes de "
            "compra urgentes generadas, ya que existen productos bajo "
            "su stock mínimo con plazos de reposición superiores a "
            f"{LEAD_TIME_URGENTE} días."
        )
    else:
        print(
            "No se detectaron productos válidos de extrema urgencia. "
            "Se recomienda mantener el monitoreo diario del inventario "
            "y revisar los registros descartados antes de tomar "
            "decisiones de compra."
        )

    return None


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():
    """
    Orquesta el flujo completo de lectura, validación, cálculo,
    generación de salida y presentación del reporte ejecutivo.

    Parámetros:
        None.

    Retorna:
        dict: Resumen final de la ejecución.
    """
    registros_crudos = leer_csv()

    registros_validos = []
    registros_descartados = []
    registros_urgentes = []
    errores_totales = []

    total_unidades_reponer = 0
    costo_total_reposicion = 0.0

    for registro_crudo in registros_crudos:
        es_valido_tipo, registro_convertido, errores_tipo = (
            validar_tipos(registro_crudo)
        )

        if not es_valido_tipo:
            registros_descartados.append(registro_crudo)
            errores_totales.extend(errores_tipo)
            continue

        es_valido_reglas, errores_reglas = (
            validar_reglas_negocio(registro_convertido)
        )

        if not es_valido_reglas:
            registros_descartados.append(registro_convertido)
            errores_totales.extend(errores_reglas)
            continue

        registro_calculado = calcular_reposicion(registro_convertido)

        registros_validos.append(registro_calculado)

        if registro_calculado["es_bajo_stock"]:
            total_unidades_reponer += (
                registro_calculado["cantidad_a_reponer"]
            )
            costo_total_reposicion += (
                registro_calculado["costo_total_reposicion"]
            )

        if registro_calculado["es_extrema_urgencia"]:
            registros_urgentes.append(registro_calculado)

    cantidad_ordenes = escribir_csv_salida(
        registros=registros_urgentes
    )

    resumen = crear_resumen(
        total_leidos=len(registros_crudos),
        validos=registros_validos,
        descartados=registros_descartados,
        urgentes=registros_urgentes,
        total_unidades_reponer=total_unidades_reponer,
        costo_total_reposicion=costo_total_reposicion,
        errores=errores_totales
    )

    generar_reporte_consola(resumen)

    print("")
    print(
        "Archivo generado: "
        f"{RUTA_SALIDA} "
        f"({cantidad_ordenes} órdenes urgentes)."
    )

    return resumen


if __name__ == "__main__":
    main()