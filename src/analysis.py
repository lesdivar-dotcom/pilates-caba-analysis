# =====================================
# OBSERVATORIO PILATES
# =====================================
#
# Módulo: analysis.py
#
# Analiza las variables derivadas por features.py.
#
# Entrada:
#   data/processed/estudios_features.csv
#
# Salidas:
#   data/analysis/
#
# Principios:
# - No modifica los datos originales.
# - No crea nuevas variables permanentes en el dataset.
# - Todos los análisis son reproducibles.
# - Los porcentajes se calculan sobre el total de estudios.
# - Los rankings permiten identificar casos destacados.
# - Los cruces permiten estudiar relaciones entre territorio,
#   presencia digital, visibilidad y desarrollo digital.
#
# =====================================

import os
import pandas as pd
import numpy as np


# =====================================
# CONFIGURACIÓN
# =====================================

RUTA_ENTRADA = (
    "data/processed/estudios_features.csv"
)

RUTA_SALIDA = (
    "data/analysis"
)


# =====================================
# CARGA
# =====================================

def cargar_datos():

    df = pd.read_csv(
        RUTA_ENTRADA
    )

    print("\n=====================================")
    print(" DATOS CARGADOS")
    print("=====================================\n")

    print(
        f"Registros: {len(df)}"
    )

    print(
        f"Columnas: {len(df.columns)}"
    )

    return df


# =====================================
# PREPARACIÓN
# =====================================

def preparar_datos(df):

    df = df.copy()

    columnas_numericas = [
        "seguidores_instagram",
        "puntaje_google",
        "cantidad_resenas",
        "presencia_digital",
        "n_canales_contacto",
        "n_fabricantes",
        "indice_visibilidad",
        "indice_desarrollo_digital",
    ]

    for columna in columnas_numericas:

        if columna in df.columns:

            df[columna] = pd.to_numeric(
                df[columna],
                errors="coerce"
            )

    return df


# =====================================
# CREAR DIRECTORIO DE SALIDA
# =====================================

def crear_directorio_salida():

    os.makedirs(
        RUTA_SALIDA,
        exist_ok=True
    )


# =====================================
# UTILIDAD:
# PORCENTAJES
# =====================================

def agregar_porcentaje(tabla, columna="estudios"):

    tabla = tabla.copy()

    total = tabla[columna].sum()

    if total == 0:

        tabla["porcentaje"] = 0.0

    else:

        tabla["porcentaje"] = (
            tabla[columna] / total * 100
        ).round(2)

    return tabla


# =====================================
# UTILIDAD:
# GUARDAR TABLA
# =====================================

def guardar_tabla(
    tabla,
    nombre_archivo
):

    ruta = os.path.join(
        RUTA_SALIDA,
        nombre_archivo
    )

    tabla.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\nArchivo guardado:\n{ruta}"
    )


# =====================================
# RESUMEN GENERAL
# =====================================

def analizar_resumen_general(df):

    cantidad_estudios = len(df)

    con_puntaje = (
        df["puntaje_google"]
        .notna()
        .sum()
    )

    sin_puntaje = (
        df["puntaje_google"]
        .isna()
        .sum()
    )

    puntaje_promedio = (
        df["puntaje_google"]
        .mean()
    )

    puntaje_minimo = (
        df["puntaje_google"]
        .min()
    )

    puntaje_maximo = (
        df["puntaje_google"]
        .max()
    )

    con_resenas = (
        df["cantidad_resenas"]
        .notna()
        .sum()
    )

    promedio_resenas = (
        df["cantidad_resenas"]
        .mean()
    )

    mediana_resenas = (
        df["cantidad_resenas"]
        .median()
    )

    maximo_resenas = (
        df["cantidad_resenas"]
        .max()
    )

    con_instagram = (
        df["seguidores_instagram"]
        .notna()
        .sum()
    )

    promedio_seguidores = (
        df["seguidores_instagram"]
        .mean()
    )

    mediana_seguidores = (
        df["seguidores_instagram"]
        .median()
    )

    maximo_seguidores = (
        df["seguidores_instagram"]
        .max()
    )

    resumen = pd.DataFrame({

        "indicador": [

            "Cantidad de estudios",

            "Con puntaje",

            "Sin puntaje",

            "Puntaje promedio",

            "Puntaje mínimo",

            "Puntaje máximo",

            "Estudios con reseñas",

            "Reseñas promedio",

            "Mediana de reseñas",

            "Máximo de reseñas",

            "Con Instagram",

            "Seguidores promedio",

            "Mediana de seguidores",

            "Máximo de seguidores",

        ],

        "valor": [

            cantidad_estudios,

            con_puntaje,

            sin_puntaje,

            puntaje_promedio,

            puntaje_minimo,

            puntaje_maximo,

            con_resenas,

            promedio_resenas,

            mediana_resenas,

            maximo_resenas,

            con_instagram,

            promedio_seguidores,

            mediana_seguidores,

            maximo_seguidores,

        ]

    })

    resumen["valor"] = (
        resumen["valor"]
        .round(2)
    )

    print("\n=====================================")
    print(" RESUMEN GENERAL")
    print("=====================================\n")

    print(
        resumen.to_string(
            index=False
        )
    )

    guardar_tabla(
        resumen,
        "resumen_general.csv"
    )

    return resumen


# =====================================
# DISTRIBUCIÓN POR BARRIO
# =====================================

def analizar_barrios(df):

    tabla = (

        df["barrio"]

        .fillna("Sin dato")

        .value_counts()

        .rename_axis("barrio")

        .reset_index(
            name="estudios"
        )

    )

    tabla = agregar_porcentaje(
        tabla
    )

    print("\n=====================================")
    print(" DISTRIBUCIÓN POR BARRIO")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "distribucion_barrios.csv"
    )

    return tabla


# =====================================
# DISTRIBUCIÓN POR COMUNA
# =====================================

def analizar_comunas(df):

    tabla = (

        df["comuna"]

        .fillna(-1)

        .value_counts()

        .sort_index()

        .rename_axis("comuna")

        .reset_index(
            name="estudios"
        )

    )

    tabla["comuna"] = (
        tabla["comuna"]
        .replace(
            -1,
            np.nan
        )
    )

    tabla = agregar_porcentaje(
        tabla
    )

    print("\n=====================================")
    print(" DISTRIBUCIÓN POR COMUNA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "distribucion_comunas.csv"
    )

    return tabla


# =====================================
# DISTRIBUCIÓN POR ZONA
# =====================================

def analizar_zonas(df):

    tabla = (

        df["zona"]

        .fillna("Sin dato")

        .value_counts()

        .rename_axis("zona")

        .reset_index(
            name="estudios"
        )

    )

    tabla = agregar_porcentaje(
        tabla
    )

    print("\n=====================================")
    print(" DISTRIBUCIÓN POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "distribucion_zonas.csv"
    )

    return tabla


# =====================================
# PERFIL TERRITORIAL POR ZONA
# =====================================

def analizar_perfil_zonal(df):

    columnas = [
        "zona",
        "seguidores_instagram",
        "puntaje_google",
        "cantidad_resenas",
        "presencia_digital",
        "n_canales_contacto",
    ]

    disponibles = [
        c for c in columnas
        if c in df.columns
    ]

    tabla = (

        df.groupby(
            "zona",
            dropna=False
        )[

            disponibles[1:]

        ]

        .agg(
            [
                "mean"
            ]
        )

    )

    tabla.columns = [
        "_".join(col).strip("_")
        for col in tabla.columns
    ]

    tabla = (
        tabla
        .reset_index()
    )

    conteos = (
        df.groupby(
            "zona",
            dropna=False
        )
        .size()
        .reset_index(
            name="estudios"
        )
    )

    tabla = conteos.merge(
        tabla,
        on="zona",
        how="left"
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / len(df)
        * 100
    ).round(2)

    tabla = tabla.rename(
        columns={

            "seguidores_instagram_mean":
                "seguidores_instagram_promedio",

            "puntaje_google_mean":
                "puntaje_promedio",

            "cantidad_resenas_mean":
                "resenas_promedio",

            "presencia_digital_mean":
                "presencia_digital_media",

            "n_canales_contacto_mean":
                "canales_contacto_medios",

        }
    )

    tabla = tabla.sort_values(
        "estudios",
        ascending=False
    )

    print("\n=====================================")
    print(" PERFIL POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "perfil_zonal.csv"
    )

    return tabla


# =====================================
# PRESENCIA DIGITAL
# =====================================

def analizar_presencia_digital(df):

    tabla = (

        df["presencia_digital"]

        .value_counts()

        .sort_index()

        .rename_axis(
            "presencia_digital"
        )

        .reset_index(
            name="estudios"
        )

    )

    tabla = agregar_porcentaje(
        tabla
    )

    print("\n=====================================")
    print(" PRESENCIA DIGITAL")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    print(
        f"\nPromedio: "
        f"{df['presencia_digital'].mean():.2f}"
    )

    print(
        f"Máximo: "
        f"{df['presencia_digital'].max()}"
    )

    print(
        "Estudios con presencia completa: "
        f"{(df['presencia_digital'] == 4).sum()}"
    )

    guardar_tabla(
        tabla,
        "presencia_digital.csv"
    )

    return tabla


# =====================================
# CANALES DE CONTACTO
# =====================================

def analizar_canales_contacto(df):

    tabla = (

        df["n_canales_contacto"]

        .value_counts()

        .sort_index()

        .rename_axis(
            "n_canales_contacto"
        )

        .reset_index(
            name="estudios"
        )

    )

    tabla = agregar_porcentaje(
        tabla
    )

    print("\n=====================================")
    print(" CANALES DE CONTACTO")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    print(
        f"\nPromedio: "
        f"{df['n_canales_contacto'].mean():.2f}"
    )

    print(
        f"Máximo: "
        f"{df['n_canales_contacto'].max()}"
    )

    guardar_tabla(
        tabla,
        "canales_contacto.csv"
    )

    return tabla


# =====================================
# FABRICANTES
# =====================================

def analizar_fabricantes(df):

    tabla = (

        df["n_fabricantes"]

        .value_counts()

        .sort_index()

        .rename_axis(
            "n_fabricantes"
        )

        .reset_index(
            name="estudios"
        )

    )

    tabla = agregar_porcentaje(
        tabla
    )

    print("\n=====================================")
    print(" FABRICANTES")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "fabricantes.csv"
    )

    return tabla


# =====================================
# FABRICANTE MÚLTIPLE
# =====================================

def analizar_fabricante_multiple(df):

    tabla = (

        df["fabricante_multiple"]

        .value_counts()

        .rename_axis(
            "fabricante_multiple"
        )

        .reset_index(
            name="estudios"
        )

    )

    tabla = agregar_porcentaje(
        tabla
    )

    print("\n=====================================")
    print(" FABRICANTE MÚLTIPLE")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "fabricante_multiple.csv"
    )

    return tabla


# =====================================
# FABRICANTES POR ZONA
# =====================================

def analizar_fabricantes_por_zona(df):

    tabla = (

        df.groupby(
            "zona",
            dropna=False
        )

        .agg(

            estudios=(
                "id_estudio",
                "count"
            ),

            fabricantes_promedio=(
                "n_fabricantes",
                "mean"
            ),

            porcentaje_fabricante_multiple=(
                "fabricante_multiple",
                lambda x:
                x.mean() * 100
            )

        )

        .reset_index()

    )

    tabla["fabricantes_promedio"] = (
        tabla["fabricantes_promedio"]
        .round(2)
    )

    tabla[
        "porcentaje_fabricante_multiple"
    ] = (
        tabla[
            "porcentaje_fabricante_multiple"
        ]
        .round(2)
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / len(df)
        * 100
    ).round(2)

    print("\n=====================================")
    print(" FABRICANTES POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "fabricantes_por_zona.csv"
    )

    return tabla


# =====================================
# PERFIL DIGITAL POR ZONA
# =====================================

def analizar_digital_por_zona(df):

    tabla = (

        df.groupby(
            "zona",
            dropna=False
        )

        .agg(

            estudios=(
                "id_estudio",
                "count"
            ),

            presencia_digital_media=(
                "presencia_digital",
                "mean"
            ),

            seguidores_instagram_promedio=(
                "seguidores_instagram",
                "mean"
            ),

        )

        .reset_index()

    )

    tabla["presencia_digital_media"] = (
        tabla["presencia_digital_media"]
        .round(2)
    )

    tabla[
        "seguidores_instagram_promedio"
    ] = (
        tabla[
            "seguidores_instagram_promedio"
        ]
        .round(2)
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / len(df)
        * 100
    ).round(2)

    print("\n=====================================")
    print(" PERFIL DIGITAL POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "digital_por_zona.csv"
    )

    return tabla


# =====================================
# CONTACTO Y DIGITAL POR ZONA
# =====================================

def analizar_contacto_digital_por_zona(df):

    tabla = (

        df.groupby(
            "zona",
            dropna=False
        )

        .agg(

            estudios=(
                "id_estudio",
                "count"
            ),

            canales_contacto_medios=(
                "n_canales_contacto",
                "mean"
            ),

            presencia_digital_media=(
                "presencia_digital",
                "mean"
            ),

        )

        .reset_index()

    )

    tabla[
        "canales_contacto_medios"
    ] = (
        tabla[
            "canales_contacto_medios"
        ]
        .round(2)
    )

    tabla[
        "presencia_digital_media"
    ] = (
        tabla[
            "presencia_digital_media"
        ]
        .round(2)
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / len(df)
        * 100
    ).round(2)

    print("\n=====================================")
    print(" CONTACTO Y DIGITAL POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "contacto_digital_por_zona.csv"
    )

    return tabla


# =====================================
# ÍNDICE DE VISIBILIDAD
# =====================================

def analizar_visibilidad(df):

    columna = "indice_visibilidad"

    if columna not in df.columns:

        print(
            "\nNo existe "
            f"'{columna}'. "
            "Se omite el análisis."
        )

        return None

    valores = df[columna].dropna()

    resumen = pd.DataFrame({

        "indicador": [

            "Promedio",

            "Desvío estándar",

            "Mediana",

            "Percentil 25",

            "Percentil 75",

        ],

        "valor": [

            valores.mean(),

            valores.std(),

            valores.median(),

            valores.quantile(0.25),

            valores.quantile(0.75),

        ]

    })

    resumen["valor"] = (
        resumen["valor"]
        .round(3)
    )

    niveles = (

        df["nivel_visibilidad"]

        .value_counts()

        .rename_axis("nivel")

        .reset_index(
            name="estudios"
        )

    )

    niveles = agregar_porcentaje(
        niveles
    )

    print("\n=====================================")
    print(" ÍNDICE DE VISIBILIDAD")
    print("=====================================\n")

    print(
        resumen.to_string(
            index=False
        )
    )

    print("\nNiveles:")

    print(
        niveles.to_string(
            index=False
        )
    )

    guardar_tabla(
        resumen,
        "visibilidad_resumen.csv"
    )

    guardar_tabla(
        niveles,
        "visibilidad_niveles.csv"
    )

    return resumen


# =====================================
# DESARROLLO DIGITAL
# =====================================

def analizar_desarrollo_digital(df):

    columna = (
        "indice_desarrollo_digital"
    )

    if columna not in df.columns:

        print(
            "\nNo existe "
            f"'{columna}'. "
            "Se omite el análisis."
        )

        return None

    valores = df[columna].dropna()

    resumen = pd.DataFrame({

        "indicador": [

            "Promedio",

            "Desvío estándar",

            "Mediana",

            "Percentil 25",

            "Percentil 75",

        ],

        "valor": [

            valores.mean(),

            valores.std(),

            valores.median(),

            valores.quantile(0.25),

            valores.quantile(0.75),

        ]

    })

    resumen["valor"] = (
        resumen["valor"]
        .round(3)
    )

    niveles = (

        df["nivel_desarrollo_digital"]

        .value_counts()

        .rename_axis("nivel")

        .reset_index(
            name="estudios"
        )

    )

    niveles = agregar_porcentaje(
        niveles
    )

    print("\n=====================================")
    print(" DESARROLLO DIGITAL")
    print("=====================================\n")

    print(
        resumen.to_string(
            index=False
        )
    )

    print("\nNiveles:")

    print(
        niveles.to_string(
            index=False
        )
    )

    guardar_tabla(
        resumen,
        "desarrollo_digital_resumen.csv"
    )

    guardar_tabla(
        niveles,
        "desarrollo_digital_niveles.csv"
    )

    return resumen


# =====================================
# VISIBILIDAD POR ZONA
# =====================================

def analizar_visibilidad_por_zona(df):

    if "indice_visibilidad" not in df.columns:

        return None

    tabla = (

        df.groupby(
            "zona",
            dropna=False
        )

        .agg(

            estudios=(
                "id_estudio",
                "count"
            ),

            visibilidad_promedio=(
                "indice_visibilidad",
                "mean"
            )

        )

        .reset_index()

    )

    tabla[
        "visibilidad_promedio"
    ] = (
        tabla[
            "visibilidad_promedio"
        ]
        .round(3)
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / len(df)
        * 100
    ).round(2)

    print("\n=====================================")
    print(" VISIBILIDAD POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "visibilidad_por_zona.csv"
    )

    return tabla


# =====================================
# DESARROLLO DIGITAL POR ZONA
# =====================================

def analizar_desarrollo_por_zona(df):

    if (
        "indice_desarrollo_digital"
        not in df.columns
    ):

        return None

    tabla = (

        df.groupby(
            "zona",
            dropna=False
        )

        .agg(

            estudios=(
                "id_estudio",
                "count"
            ),

            desarrollo_digital_promedio=(
                "indice_desarrollo_digital",
                "mean"
            )

        )

        .reset_index()

    )

    tabla[
        "desarrollo_digital_promedio"
    ] = (
        tabla[
            "desarrollo_digital_promedio"
        ]
        .round(3)
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / len(df)
        * 100
    ).round(2)

    print("\n=====================================")
    print(" DESARROLLO DIGITAL POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "desarrollo_digital_por_zona.csv"
    )

    return tabla


# =====================================
# PERFIL COMPLETO POR ZONA
# =====================================

def analizar_zona_completa(df):

    columnas = [

        "seguidores_instagram",

        "puntaje_google",

        "cantidad_resenas",

        "presencia_digital",

        "n_canales_contacto",

        "n_fabricantes",

        "indice_visibilidad",

        "indice_desarrollo_digital",

    ]

    columnas = [
        c for c in columnas
        if c in df.columns
    ]

    agregaciones = {

        "estudios": (
            "id_estudio",
            "count"
        )

    }

    for columna in columnas:

        agregaciones[
            f"{columna}_promedio"
        ] = (
            columna,
            "mean"
        )

    tabla = (

        df.groupby(
            "zona",
            dropna=False
        )

        .agg(
            **agregaciones
        )

        .reset_index()

    )

    for columna in tabla.columns:

        if (
            columna.endswith(
                "_promedio"
            )
        ):

            tabla[columna] = (
                tabla[columna]
                .round(3)
            )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / len(df)
        * 100
    ).round(2)

    tabla = tabla.sort_values(
        "estudios",
        ascending=False
    )

    print("\n=====================================")
    print(" PERFIL COMPLETO POR ZONA")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "perfil_completo_zona.csv"
    )

    return tabla


# =====================================
# RANKING DE INSTAGRAM
# =====================================

def ranking_instagram(
    df,
    n=20
):

    columnas = [
        "id_estudio",
        "nombre_del_estudio",
        "seguidores_instagram",
        "barrio",
        "zona",
    ]

    columnas = [
        c for c in columnas
        if c in df.columns
    ]

    tabla = (

        df[
            df["seguidores_instagram"]
            .notna()
        ][columnas]

        .sort_values(
            "seguidores_instagram",
            ascending=False
        )

        .head(n)

        .copy()

    )

    print("\n=====================================")
    print(
        f" TOP {n} INSTAGRAM"
    )
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "ranking_instagram.csv"
    )

    return tabla


# =====================================
# RANKING DE RESEÑAS
# =====================================

def ranking_resenas(
    df,
    n=20
):

    columnas = [
        "id_estudio",
        "nombre_del_estudio",
        "puntaje_google",
        "cantidad_resenas",
        "barrio",
        "zona",
    ]

    columnas = [
        c for c in columnas
        if c in df.columns
    ]

    tabla = (

        df[
            df["cantidad_resenas"]
            .notna()
        ][columnas]

        .sort_values(
            "cantidad_resenas",
            ascending=False
        )

        .head(n)

        .copy()

    )

    print("\n=====================================")
    print(
        f" TOP {n} RESEÑAS"
    )
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "ranking_resenas.csv"
    )

    return tabla


# =====================================
# RANKING DE PUNTAJE
# =====================================

def ranking_puntaje(
    df,
    n=20
):

    columnas = [
        "id_estudio",
        "nombre_del_estudio",
        "puntaje_google",
        "cantidad_resenas",
        "barrio",
        "zona",
    ]

    columnas = [
        c for c in columnas
        if c in df.columns
    ]

    tabla = (

        df[
            df["puntaje_google"]
            .notna()
        ][columnas]

        .sort_values(
            [
                "puntaje_google",
                "cantidad_resenas",
            ],
            ascending=[
                False,
                False,
            ]
        )

        .head(n)

        .copy()

    )

    print("\n=====================================")
    print(
        f" TOP {n} PUNTAJE"
    )
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "ranking_puntaje.csv"
    )

    return tabla


# =====================================
# RANKING VISIBILIDAD
# =====================================

def ranking_visibilidad(
    df,
    n=20
):

    if "indice_visibilidad" not in df.columns:

        return None

    columnas = [
        "id_estudio",
        "nombre_del_estudio",
        "barrio",
        "zona",
        "indice_visibilidad",
        "nivel_visibilidad",
    ]

    columnas = [
        c for c in columnas
        if c in df.columns
    ]

    tabla = (

        df[
            df["indice_visibilidad"]
            .notna()
        ][columnas]

        .sort_values(
            "indice_visibilidad",
            ascending=False
        )

        .head(n)

        .copy()

    )

    print("\n=====================================")
    print(
        f" TOP {n} VISIBILIDAD"
    )
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "ranking_visibilidad.csv"
    )

    return tabla


# =====================================
# RANKING DESARROLLO DIGITAL
# =====================================

def ranking_desarrollo_digital(
    df,
    n=20
):

    if (
        "indice_desarrollo_digital"
        not in df.columns
    ):

        return None

    columnas = [
        "id_estudio",
        "nombre_del_estudio",
        "barrio",
        "zona",
        "indice_desarrollo_digital",
        "nivel_desarrollo_digital",
    ]

    columnas = [
        c for c in columnas
        if c in df.columns
    ]

    tabla = (

        df[
            df[
                "indice_desarrollo_digital"
            ].notna()
        ][columnas]

        .sort_values(
            "indice_desarrollo_digital",
            ascending=False
        )

        .head(n)

        .copy()

    )

    print("\n=====================================")
    print(
        f" TOP {n} DESARROLLO DIGITAL"
    )
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "ranking_desarrollo_digital.csv"
    )

    return tabla


# =====================================
# CRUCE:
# VISIBILIDAD × DESARROLLO DIGITAL
# =====================================

def analizar_visibilidad_desarrollo(df):

    columnas = [
        "indice_visibilidad",
        "indice_desarrollo_digital",
    ]

    if not all(
        c in df.columns
        for c in columnas
    ):

        return None

    datos = df[
        columnas
    ].dropna()

    if len(datos) < 2:

        return None

    correlacion = (
        datos[
            "indice_visibilidad"
        ]
        .corr(
            datos[
                "indice_desarrollo_digital"
            ]
        )
    )

    resumen = pd.DataFrame({

        "indicador": [
            "Estudios comparables",
            "Correlación Pearson",
        ],

        "valor": [
            len(datos),
            round(
                correlacion,
                3
            ),
        ]

    })

    print("\n=====================================")
    print(
        " VISIBILIDAD × DESARROLLO DIGITAL"
    )
    print("=====================================\n")

    print(
        resumen.to_string(
            index=False
        )
    )

    guardar_tabla(
        resumen,
        "visibilidad_desarrollo_correlacion.csv"
    )

    return resumen


# =====================================
# MATRIZ DE NIVELES
# =====================================

def analizar_matriz_niveles(df):

    columnas = [
        "nivel_visibilidad",
        "nivel_desarrollo_digital",
    ]

    if not all(
        c in df.columns
        for c in columnas
    ):

        return None

    matriz = pd.crosstab(
        df[
            "nivel_visibilidad"
        ].fillna("Sin dato"),

        df[
            "nivel_desarrollo_digital"
        ].fillna("Sin dato")
    )

    print("\n=====================================")
    print(
        " MATRIZ VISIBILIDAD × DESARROLLO"
    )
    print("=====================================\n")

    print(matriz)

    ruta = os.path.join(
        RUTA_SALIDA,
        "matriz_visibilidad_desarrollo.csv"
    )

    matriz.to_csv(
        ruta,
        encoding="utf-8-sig"
    )

    print(
        f"\nArchivo guardado:\n{ruta}"
    )

    return matriz


# =====================================
# ESTUDIOS CON ALTA VISIBILIDAD
# =====================================

def analizar_casos_destacados(df):

    if (
        "indice_visibilidad"
        not in df.columns
    ):

        return None

    columnas = [
        "id_estudio",
        "nombre_del_estudio",
        "barrio",
        "zona",
        "indice_visibilidad",
        "nivel_visibilidad",
        "indice_desarrollo_digital",
        "nivel_desarrollo_digital",
        "seguidores_instagram",
        "puntaje_google",
        "cantidad_resenas",
    ]

    columnas = [
        c for c in columnas
        if c in df.columns
    ]

    tabla = (

        df[
            df[
                "indice_visibilidad"
            ].notna()
        ][columnas]

        .sort_values(
            "indice_visibilidad",
            ascending=False
        )

        .head(20)

        .copy()

    )

    print("\n=====================================")
    print(" CASOS DESTACADOS")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "casos_destacados.csv"
    )

    return tabla


# =====================================
# DETECTAR DATOS FALTANTES
# =====================================

def analizar_datos_faltantes(df):

    tabla = pd.DataFrame({

        "columna": df.columns,

        "faltantes": [
            df[c].isna().sum()
            for c in df.columns
        ]

    })

    tabla["porcentaje_faltante"] = (
        tabla["faltantes"]
        / len(df)
        * 100
    ).round(2)

    tabla = tabla.sort_values(
        "faltantes",
        ascending=False
    )

    print("\n=====================================")
    print(" DATOS FALTANTES")
    print("=====================================\n")

    print(
        tabla.to_string(
            index=False
        )
    )

    guardar_tabla(
        tabla,
        "datos_faltantes.csv"
    )

    return tabla


# =====================================
# EJECUCIÓN PRINCIPAL
# =====================================

def main():

    crear_directorio_salida()

    df = cargar_datos()

    df = preparar_datos(
        df
    )

    # =================================
    # GENERAL
    # =================================

    analizar_resumen_general(
        df
    )

    analizar_datos_faltantes(
        df
    )

    # =================================
    # TERRITORIO
    # =================================

    analizar_barrios(
        df
    )

    analizar_comunas(
        df
    )

    analizar_zonas(
        df
    )

    analizar_perfil_zonal(
        df
    )

    analizar_zona_completa(
        df
    )

    # =================================
    # DIGITAL
    # =================================

    analizar_presencia_digital(
        df
    )

    analizar_digital_por_zona(
        df
    )

    # =================================
    # CONTACTO
    # =================================

    analizar_canales_contacto(
        df
    )

    analizar_contacto_digital_por_zona(
        df
    )

    # =================================
    # EQUIPAMIENTO
    # =================================

    analizar_fabricantes(
        df
    )

    analizar_fabricante_multiple(
        df
    )

    analizar_fabricantes_por_zona(
        df
    )

    # =================================
    # VISIBILIDAD
    # =================================

    analizar_visibilidad(
        df
    )

    analizar_visibilidad_por_zona(
        df
    )

    ranking_visibilidad(
        df
    )

    # =================================
    # DESARROLLO DIGITAL
    # =================================

    analizar_desarrollo_digital(
        df
    )

    analizar_desarrollo_por_zona(
        df
    )

    ranking_desarrollo_digital(
        df
    )

    # =================================
    # RANKINGS GENERALES
    # =================================

    ranking_instagram(
        df
    )

    ranking_resenas(
        df
    )

    ranking_puntaje(
        df
    )

    # =================================
    # CRUCES
    # =================================

    analizar_visibilidad_desarrollo(
        df
    )

    analizar_matriz_niveles(
        df
    )

    analizar_casos_destacados(
        df
    )

    # =================================
    # FINAL
    # =================================

    print("\n=====================================")
    print(" ANÁLISIS COMPLETADO")
    print("=====================================\n")

    print(
        f"Total de estudios analizados: "
        f"{len(df)}"
    )

    print(
        f"Resultados disponibles en:\n"
        f"{RUTA_SALIDA}"
    )


# =====================================
# EJECUTAR
# =====================================

if __name__ == "__main__":

    main()