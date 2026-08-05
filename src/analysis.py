#analysis.py
# =====================================
# OBSERVATORIO PILATES
# ANALYSIS
# =====================================

"""
OBSERVATORIO PILATES

Módulo: analysis.py

Este módulo transforma las variables analíticas
generadas por features.py en indicadores,
tablas y resultados interpretables.

Entrada:
    data/processed/estudios_features.csv

Salida:
    Tablas analíticas
    Indicadores
    Reportes

Principios
----------

- Nunca modifica los datos.
- Todos los análisis parten de preguntas.
- Todos los resultados son reproducibles.
- No contiene reglas de limpieza.
- No contiene ingeniería de variables.

Bloques implementados
---------------------

□ Territorio
□ Digitalización
□ Contactabilidad
□ Equipamiento
□ Cruces

Próximas etapas
---------------

□ Visualizaciones
□ Mapas
□ Exportación automática
□ Dashboard
"""
import pandas as pd
# =====================================
# CARGA
# =====================================
import pandas as pd

def cargar_datos():
    """
    Carga el dataset analítico generado por
    features.py.

    Entrada:
        data/processed/estudios_features.csv

    Retorna
    -------
    pandas.DataFrame
    """

    return pd.read_csv(
        "data/processed/estudios_features.csv"
    )
# =====================================
# ANÁLISIS TERRITORIAL
# BARRIOS
# =====================================

def analizar_barrios(df):
    """
    Genera la distribución de estudios
    por barrio.

    Retorna
    -------
    DataFrame

    Columnas:
        barrio
        estudios
        porcentaje
    """

    tabla = (
        df["barrio"]
        .value_counts(dropna=False)
        .rename_axis("barrio")
        .reset_index(name="estudios")
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# COMUNAS
# =====================================

def analizar_comunas(df):
    """
    Genera la distribución de estudios
    por comuna.

    Retorna
    -------
    DataFrame

    Columnas:
        comuna
        estudios
        porcentaje
    """

    tabla = (
        df["comuna"]
        .value_counts(dropna=False)
        .sort_index()
        .rename_axis("comuna")
        .reset_index(name="estudios")
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# ZONAS
# =====================================

def analizar_zonas(df):
    """
    Genera indicadores territoriales por zona.

    Retorna
    -------
    DataFrame

    Columnas:
        zona
        estudios
        seguidores_promedio
        puntaje_promedio
        resenas_promedio
        presencia_digital_media
        canales_contacto_medios
        porcentaje
    """

    tabla = (
        df.groupby("zona", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            seguidores_promedio=("seguidores", "mean"),
            puntaje_promedio=("puntaje_google", "mean"),
            resenas_promedio=("cantidad_resenas", "mean"),
            presencia_digital_media=("presencia_digital", "mean"),
            canales_contacto_medios=("n_canales_contacto", "mean"),
        )
        .round(2)
        .reset_index()
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    tabla = tabla.sort_values(
        "estudios",
        ascending=False
    )

    return tabla
# =====================================
# PRESENCIA DIGITAL
# =====================================

def analizar_presencia_digital(df):
    """
    Genera la distribución de la presencia digital
    de los estudios.

    Retorna
    -------
    DataFrame

    Columnas:
        presencia_digital
        estudios
        porcentaje
    """

    tabla = (
        df.groupby("presencia_digital", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count")
        )
        .reset_index()
        .sort_values("presencia_digital")
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# CANALES DE CONTACTO
# =====================================

def analizar_canales_contacto(df):
    """
    Genera la distribución de los canales
    de contacto disponibles.

    Retorna
    -------
    DataFrame

    Columnas:
        n_canales_contacto
        estudios
        porcentaje
    """

    tabla = (
        df.groupby("n_canales_contacto", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count")
        )
        .reset_index()
        .sort_values("n_canales_contacto")
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# ANÁLISIS DE EQUIPAMIENTO
# =====================================
# =====================================
# NÚMERO DE FABRICANTES
# =====================================

def analizar_n_fabricantes(df):
    """
    Analiza la distribución de estudios
    según la cantidad de fabricantes
    registrados.

    Retorna
    -------
    DataFrame

    Columnas:
        n_fabricantes
        estudios
        porcentaje
    """

    tabla = (
        df.groupby("n_fabricantes", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count")
        )
        .reset_index()
        .sort_values("n_fabricantes")
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# FABRICANTES MÚLTIPLES
# =====================================

def analizar_fabricante_multiple(df):
    """
    Analiza cuántos estudios utilizan
    uno o más fabricantes.

    Retorna
    -------
    DataFrame

    Columnas:
        fabricante_multiple
        estudios
        porcentaje
    """

    tabla = (
        df.groupby("fabricante_multiple", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count")
        )
        .reset_index()
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# ANÁLISIS DEL MERCADO
# =====================================
# =====================================
# PUNTAJES
# =====================================

def analizar_puntajes(df):
    """
    Genera indicadores sobre las
    valoraciones de Google.

    Retorna
    -------
    DataFrame

    Columnas:
        indicador
        valor
    """

    tabla = pd.DataFrame({

        "indicador": [

            "Cantidad de estudios",
            "Con puntaje",
            "Sin puntaje",
            "Puntaje promedio",
            "Puntaje mínimo",
            "Puntaje máximo"

        ],

        "valor": [

            len(df),
            df["puntaje_google"].notna().sum(),
            df["puntaje_google"].isna().sum(),
            round(df["puntaje_google"].mean(), 2),
            df["puntaje_google"].min(),
            df["puntaje_google"].max()

        ]

    })

    return tabla
# =====================================
# RESEÑAS
# =====================================

def analizar_resenas(df):
    """
    Genera indicadores sobre las
    reseñas registradas.

    Retorna
    -------
    DataFrame
    """

    tabla = pd.DataFrame({

        "indicador": [

            "Promedio",
            "Mediana",
            "Máximo",
            "Estudios con reseñas"

        ],

        "valor": [

            round(df["cantidad_resenas"].mean(), 1),
            df["cantidad_resenas"].median(),
            df["cantidad_resenas"].max(),
            (df["cantidad_resenas"] > 0).sum()

        ]

    })

    return tabla
# =====================================
# SEGUIDORES
# =====================================

def analizar_seguidores(df):
    """
    Genera indicadores sobre los
    seguidores de Instagram.

    Retorna
    -------
    DataFrame
    """

    tabla = pd.DataFrame({

        "indicador": [

            "Promedio",
            "Mediana",
            "Máximo",
            "Con Instagram"

        ],

        "valor": [

            round(df["seguidores"].mean(), 1),
            df["seguidores"].median(),
            df["seguidores"].max(),
            df["seguidores"].notna().sum()

        ]

    })

    return tabla
# =====================================
# CRUCES
# =====================================
# =====================================
# ZONA vs PRESENCIA DIGITAL
# =====================================

def analizar_zona_vs_presencia(df):
    """
    Analiza la presencia digital de los
    estudios según la zona.

    Retorna
    -------
    DataFrame

    Columnas:
        zona
        estudios
        presencia_digital_media
        seguidores_promedio
        porcentaje
    """

    tabla = (
        df.groupby("zona", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            presencia_digital_media=("presencia_digital", "mean"),
            seguidores_promedio=("seguidores", "mean"),
        )
        .round(2)
        .reset_index()
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    tabla = tabla.sort_values(
        "presencia_digital_media",
        ascending=False
    )

    return tabla
# =====================================
# ZONA vs CANALES DE CONTACTO
# =====================================

def analizar_zona_vs_contacto(df):
    """
    Analiza los canales de contacto disponibles
    según la zona.

    Retorna
    -------
    DataFrame

    Columnas:
        zona
        estudios
        canales_contacto_medios
        presencia_digital_media
        porcentaje
    """

    tabla = (
        df.groupby("zona", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            canales_contacto_medios=("n_canales_contacto", "mean"),
            presencia_digital_media=("presencia_digital", "mean"),
        )
        .round(2)
        .reset_index()
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    tabla = tabla.sort_values(
        "canales_contacto_medios",
        ascending=False
    )

    return tabla
# =====================================
# ZONA vs FABRICANTES
# =====================================

def analizar_zona_vs_fabricantes(df):
    """
    Analiza el equipamiento utilizado
    según la zona.

    Retorna
    -------
    DataFrame

    Columnas:
        zona
        estudios
        fabricantes_promedio
        porcentaje_fabricante_multiple
        porcentaje
    """

    tabla = (
        df.groupby("zona", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            fabricantes_promedio=("n_fabricantes", "mean"),
            porcentaje_fabricante_multiple=(
                "fabricante_multiple",
                "mean"
            ),
        )
        .round(2)
        .reset_index()
    )

    tabla["porcentaje_fabricante_multiple"] = (
        tabla["porcentaje_fabricante_multiple"] * 100
    ).round(2)

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    tabla = tabla.sort_values(
        "fabricantes_promedio",
        ascending=False
    )

    return tabla
# =====================================
# ZONA vs MERCADO
# =====================================

def analizar_zona_vs_mercado(df):
    """
    Analiza los principales indicadores
    del mercado según la zona.

    Retorna
    -------
    DataFrame

    Columnas:
        zona
        estudios
        seguidores_promedio
        puntaje_promedio
        resenas_promedio
        porcentaje
    """

    tabla = (
        df.groupby("zona", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            seguidores_promedio=("seguidores", "mean"),
            puntaje_promedio=("puntaje_google", "mean"),
            resenas_promedio=("cantidad_resenas", "mean"),
        )
        .round(2)
        .reset_index()
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    tabla = tabla.sort_values(
        "estudios",
        ascending=False
    )

    return tabla
# =====================================
# PRESENCIA DIGITAL vs MERCADO
# =====================================

def analizar_presencia_vs_mercado(df):
    """
    Analiza la relación entre la presencia
    digital y los principales indicadores
    del mercado.

    Retorna
    -------
    DataFrame

    Columnas:
        presencia_digital
        estudios
        seguidores_promedio
        puntaje_promedio
        resenas_promedio
        porcentaje
    """

    tabla = (
        df.groupby("presencia_digital", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            seguidores_promedio=("seguidores", "mean"),
            puntaje_promedio=("puntaje_google", "mean"),
            resenas_promedio=("cantidad_resenas", "mean"),
        )
        .round(2)
        .reset_index()
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    tabla = tabla.sort_values("presencia_digital")

    return tabla
# =====================================
# FABRICANTES vs MERCADO
# =====================================

def analizar_fabricantes_vs_mercado(df):
    """
    Analiza los principales indicadores
    del mercado según el uso de uno o
    varios fabricantes.

    Retorna
    -------
    DataFrame

    Columnas:
        fabricante_multiple
        estudios
        seguidores_promedio
        puntaje_promedio
        resenas_promedio
        porcentaje
    """

    tabla = (
        df.groupby("fabricante_multiple", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            seguidores_promedio=("seguidores", "mean"),
            puntaje_promedio=("puntaje_google", "mean"),
            resenas_promedio=("cantidad_resenas", "mean"),
        )
        .round(2)
        .reset_index()
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# INDICADORES COMPUESTOS
# =====================================
def normalizar_0_1(serie):
    """
    Normaliza una serie numérica
    utilizando Min-Max Scaling.

    Retorna
    -------
    pandas.Series
    """

    minimo = serie.min()
    maximo = serie.max()

    if maximo == minimo:
        return pd.Series(0, index=serie.index)

    return (serie - minimo) / (maximo - minimo)

def calcular_indice_visibilidad(df):
    """
    Calcula el índice de visibilidad
    de cada estudio.

    Componentes
    -----------
    - presencia digital
    - canales de contacto
    - seguidores

    Retorna
    -------
    DataFrame
    """

    df = df.copy()

    df["seguidores_norm"] = normalizar_0_1(
        df["seguidores"].fillna(0)
    )

    presencia = (
        df["presencia_digital"] / 4
    )

    contacto = (
        df["n_canales_contacto"] / 4
    )

    df["indice_visibilidad"] = (

        presencia * 0.40 +

        contacto * 0.30 +

        df["seguidores_norm"] * 0.30

    ).round(3)

    return df

def analizar_indice_visibilidad(df):
    """
    Resume el índice de visibilidad.

    Retorna
    -------
    DataFrame
    """

    tabla = pd.DataFrame({

        "indicador": [

            "Promedio",
            "Mediana",
            "Mínimo",
            "Máximo"

        ],

        "valor": [

            round(df["indice_visibilidad"].mean(), 3),

            round(df["indice_visibilidad"].median(), 3),

            round(df["indice_visibilidad"].min(), 3),

            round(df["indice_visibilidad"].max(), 3)

        ]

    })

    return tabla

def ranking_visibilidad(df, top=20):
    """
    Ranking de estudios según
    índice de visibilidad.
    """

    columnas = [

        "nombre_del_estudio",

        "barrio",

        "indice_visibilidad",

        "seguidores",

        "presencia_digital",

        "n_canales_contacto"

    ]

    return (
        df[columnas]
        .sort_values(
            "indice_visibilidad",
            ascending=False
        )
        .head(top)
    )
    
# -----------------------------
# Indicadores compuestos
# -----------------------------

    df = calcular_indice_visibilidad(df)

    resultados["indice_visibilidad"] = (
        analizar_indice_visibilidad(df)
    )

    resultados["ranking_visibilidad"] = (
        ranking_visibilidad(df)
    )
# =====================================
# CLASIFICACIÓN DEL ÍNDICE
# =====================================
def clasificar_visibilidad(indice):
    """
    Clasifica el índice de visibilidad.

    Retorna
    -------
    str
    """

    if indice < 0.25:
        return "Muy baja"

    elif indice < 0.50:
        return "Baja"

    elif indice < 0.75:
        return "Alta"

    return "Muy alta"

    df["nivel_visibilidad"] = (
        df["indice_visibilidad"]
        .apply(clasificar_visibilidad)
)

def analizar_nivel_visibilidad(df):
    """
    Distribución de estudios según
    el nivel de visibilidad.
    """

    tabla = (
        df["nivel_visibilidad"]
        .value_counts()
        .rename_axis("nivel")
        .reset_index(name="estudios")
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
def resumen_indice_visibilidad(df):

    return pd.DataFrame({

        "indicador": [

            "Promedio",
            "Desvío estándar",
            "Mediana",
            "Percentil 25",
            "Percentil 75"

        ],

        "valor": [

            round(df["indice_visibilidad"].mean(), 3),

            round(df["indice_visibilidad"].std(), 3),

            round(df["indice_visibilidad"].median(), 3),

            round(df["indice_visibilidad"].quantile(.25), 3),

            round(df["indice_visibilidad"].quantile(.75), 3)

        ]

    })
    
# =====================================
# ÍNDICE DE VISIBILIDAD
# =====================================

def calcular_indice_visibilidad(df):
    """
    Calcula el índice de visibilidad.
    """

    seguidores = (
        df["seguidores"]
        .fillna(0)
        .rank(pct=True)
    )

    presencia = (
        df["presencia_digital"]
        .fillna(0) / 4
    )

    contacto = (
        df["n_canales_contacto"]
        .fillna(0) / 4
    )

    web = (
        df["tiene_web"]
        .fillna(0)
    )

    df["indice_visibilidad"] = (
        seguidores * 0.45 +
        presencia * 0.30 +
        contacto * 0.15 +
        web * 0.10
    ).round(3)

    df["nivel_visibilidad"] = (
        df["indice_visibilidad"]
        .apply(clasificar_visibilidad)
    )

    return df

# =====================================
# RESUMEN ÍNDICE DE VISIBILIDAD
# =====================================

def analizar_indice_visibilidad(df):
    """
    Resume el índice de visibilidad.

    Retorna
    -------
    DataFrame
    """

    tabla = pd.DataFrame({

        "indicador": [

            "Promedio",
            "Mediana",
            "Mínimo",
            "Máximo"

        ],

        "valor": [

            round(df["indice_visibilidad"].mean(), 3),

            round(df["indice_visibilidad"].median(), 3),

            round(df["indice_visibilidad"].min(), 3),

            round(df["indice_visibilidad"].max(), 3)

        ]

    })

    return tabla
# =====================================
# RANKING VISIBILIDAD
# =====================================

def ranking_visibilidad(df, top=20):
    """
    Ranking de estudios con mayor
    índice de visibilidad.
    """

    tabla = (

        df[
            [
                "nombre_del_estudio",
                "barrio",
                "indice_visibilidad"
            ]
        ]

        .sort_values(
            "indice_visibilidad",
            ascending=False
        )

        .head(top)

        .reset_index(drop=True)

    )

    return tabla

# =====================================
# MENOR VISIBILIDAD
# =====================================

def ranking_baja_visibilidad(df, top=20):
    """
    Estudios con menor visibilidad.
    """

    tabla = (

        df[
            [
                "nombre_del_estudio",
                "barrio",
                "indice_visibilidad"
            ]
        ]

        .sort_values(
            "indice_visibilidad"
        )

        .head(top)

        .reset_index(drop=True)

    )

    return tabla

# =====================================
# NIVELES DE VISIBILIDAD
# =====================================

def clasificar_visibilidad(indice):

    if indice < 0.25:
        return "Muy baja"

    elif indice < 0.50:
        return "Baja"

    elif indice < 0.75:
        return "Alta"

    return "Muy alta"
# =====================================
# DISTRIBUCIÓN VISIBILIDAD
# =====================================

def distribucion_visibilidad(df):
    """
    Distribución de niveles
    de visibilidad.
    """

    tabla = (

        df["nivel_visibilidad"]

        .value_counts()

        .rename_axis("nivel")

        .reset_index(name="estudios")

    )

    tabla["porcentaje"] = (

        tabla["estudios"]

        / tabla["estudios"].sum()

        * 100

    ).round(2)

    return tabla

# =====================================
# ÍNDICE DE DESARROLLO DIGITAL
# =====================================

def calcular_indice_desarrollo_digital(df):
    """
    Calcula el índice de desarrollo digital.

    El índice combina:

    - presencia digital
    - canales de contacto
    - sitio web
    - app

    Retorna
    -------
    DataFrame
    """

    presencia = (
        df["presencia_digital"]
        .fillna(0) / 4
    )

    contacto = (
        df["n_canales_contacto"]
        .fillna(0) / 4
    )

    web = (
        df["tiene_web"]
        .fillna(0)
    )

    app = (
        df["tiene_app"]
        .fillna(0)
    )

    df["indice_desarrollo_digital"] = (

        presencia * 0.40 +

        contacto * 0.30 +

        web * 0.20 +

        app * 0.10

    ).round(3)

    return df

# =====================================
# CLASIFICACIÓN DEL DESARROLLO DIGITAL
# =====================================

def clasificar_desarrollo(indice):
    """
    Clasifica el índice de desarrollo digital.

    Retorna
    -------
    str
    """

    if indice < 0.25:
        return "Muy bajo"

    elif indice < 0.50:
        return "Bajo"

    elif indice < 0.75:
        return "Alto"

    return "Muy alto"

# =====================================
# DISTRIBUCIÓN DEL DESARROLLO DIGITAL
# =====================================

def analizar_desarrollo_digital(df):
    """
    Distribución de estudios según
    el nivel de desarrollo digital.

    Retorna
    -------
    DataFrame
    """

    df["nivel_desarrollo_digital"] = (
        df["indice_desarrollo_digital"]
        .apply(clasificar_desarrollo)
    )

    tabla = (
        df["nivel_desarrollo_digital"]
        .value_counts()
        .rename_axis("nivel")
        .reset_index(name="estudios")
    )

    tabla["porcentaje"] = (
        tabla["estudios"]
        / tabla["estudios"].sum()
        * 100
    ).round(2)

    return tabla
# =====================================
# RESUMEN DEL DESARROLLO DIGITAL
# =====================================

def resumen_desarrollo_digital(df):
    """
    Resumen estadístico del índice
    de desarrollo digital.

    Retorna
    -------
    DataFrame
    """

    return pd.DataFrame({

        "indicador": [

            "Promedio",
            "Desvío estándar",
            "Mediana",
            "Percentil 25",
            "Percentil 75"

        ],

        "valor": [

            round(df["indice_desarrollo_digital"].mean(), 3),

            round(df["indice_desarrollo_digital"].std(), 3),

            round(df["indice_desarrollo_digital"].median(), 3),

            round(df["indice_desarrollo_digital"].quantile(0.25), 3),

            round(df["indice_desarrollo_digital"].quantile(0.75), 3)

        ]

    })
    


# =====================================
# MAIN
# =====================================
def main():

    df = cargar_datos()

    df = calcular_indice_visibilidad(df)

    df = calcular_indice_desarrollo_digital(df)

    resultados = {

        # Territorio
        "barrios": analizar_barrios(df),
        "comunas": analizar_comunas(df),
        "zonas": analizar_zonas(df),

        # Digital
        "presencia_digital": analizar_presencia_digital(df),
        "canales_contacto": analizar_canales_contacto(df),

        # Equipamiento
        "n_fabricantes": analizar_n_fabricantes(df),
        "fabricante_multiple": analizar_fabricante_multiple(df),

        # Mercado
        "puntajes": analizar_puntajes(df),
        "resenas": analizar_resenas(df),
        "seguidores": analizar_seguidores(df),

        # Cruces
        "zona_vs_presencia": analizar_zona_vs_presencia(df),
        "zona_vs_contacto": analizar_zona_vs_contacto(df),
        "zona_vs_fabricantes": analizar_zona_vs_fabricantes(df),
        "zona_vs_mercado": analizar_zona_vs_mercado(df),
        "presencia_vs_mercado": analizar_presencia_vs_mercado(df),
        "fabricantes_vs_mercado": analizar_fabricantes_vs_mercado(df),

        # Índices
        "indice_visibilidad": analizar_nivel_visibilidad(df),
        "resumen_visibilidad": resumen_indice_visibilidad(df),

        "desarrollo_digital": analizar_desarrollo_digital(df),
        "resumen_desarrollo_digital": resumen_desarrollo_digital(df),
    }

    for nombre, tabla in resultados.items():

        print(f"\n{'=' * 50}")
        print(nombre.upper())
        print(f"{'=' * 50}\n")

        print(tabla)


if __name__ == "__main__":
    main()