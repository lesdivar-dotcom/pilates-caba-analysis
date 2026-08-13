#market_intelligence.py
# =====================================
# OBSERVATORIO PILATES
# MOTOR 5 — MARKET INTELLIGENCE
# =====================================

"""
Motor 5 — Inteligencia del Mercado

Bloques implementados:

✔ 5.1 Resumen Ejecutivo
✔ 5.2 Densidad Territorial

Fuente principal:
    data/database/observatorio_pilates.db

Salidas:
    data/intelligence/
"""

from pathlib import Path
import sqlite3
import pandas as pd
import unicodedata

# =====================================
# RUTAS
# =====================================

ROOT = Path(__file__).resolve().parents[1]

DB_PATH = (
    ROOT
    / "data"
    / "database"
    / "observatorio_pilates.db"
)

OUTPUT = (
    ROOT
    / "data"
    / "intelligence"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)
REFERENCE = (
    ROOT
    / "data"
    / "reference"
    / "caba"
)

POBLACION_PATH = (
    REFERENCE
    / "barrios_poblacion.csv"
)
# =====================================
# SQLITE
# =====================================

def conectar():

    if not DB_PATH.exists():

        raise FileNotFoundError(
            f"No existe la base SQLite:\n{DB_PATH}"
        )

    return sqlite3.connect(DB_PATH)

def normalizar_barrio(nombre):
    """
    Normaliza nombres de barrios para realizar joins seguros.
    Elimina tildes, espacios sobrantes y unifica variantes.
    """

    if pd.isna(nombre):
        return nombre

    nombre = str(nombre).strip()

    # Eliminar tildes
    nombre = "".join(
        c
        for c in unicodedata.normalize("NFKD", nombre)
        if not unicodedata.combining(c)
    )

    nombre = nombre.title()

    # Equivalencias oficiales
    equivalencias = {
        "Villa Gral. Mitre": "Villa General Mitre",
        "Villa Gral Mitre": "Villa General Mitre",
        "Villa General Mitre": "Villa General Mitre",
        "San Nicolas": "San Nicolas",
        "Velez Sarsfield": "Velez Sarsfield",
        "Nunez": "Nunez",
    }

    return equivalencias.get(nombre, nombre)

# =====================================
# EXPORTACIÓN
# =====================================

def exportar(nombre, tabla):

    ruta = OUTPUT / f"{nombre}.csv"

    tabla.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Archivo guardado: {ruta}")
REFERENCE = (
    ROOT
    / "data"
    / "reference"
    / "caba"
)

POBLACION_PATH = (
    REFERENCE
    / "barrios_poblacion.csv"
)

# =====================================
# CARGA
# =====================================

def cargar_estudios(con):

    return pd.read_sql(
        "SELECT * FROM estudios",
        con
    )

def cargar_marcas(con):

    return pd.read_sql(
        "SELECT * FROM estudio_marca",
        con
    )
def cargar_poblacion():
    """
    Carga el Catálogo Territorial CABA v1.
    """

    if not POBLACION_PATH.exists():
        raise FileNotFoundError(
            f"No existe el catálogo territorial:\n{POBLACION_PATH}"
        )

    # Leer catálogo
    poblacion = pd.read_csv(
        POBLACION_PATH,
        encoding="utf-8-sig"
    )

    requeridas = [
        "barrio",
        "poblacion"
    ]

    faltantes = [
        c
        for c in requeridas
        if c not in poblacion.columns
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas en barrios_poblacion.csv:\n"
            + "\n".join(
                f" - {c}"
                for c in faltantes
            )
        )

    poblacion["barrio"] = (
        poblacion["barrio"]
        .astype(str)
        .str.strip()
    )

    poblacion["barrio_normalizado"] = (
        poblacion["barrio"]
        .apply(normalizar_barrio)
    )

    return poblacion
# =====================================
# BLOQUE 5.1
# RESUMEN EJECUTIVO
# =====================================

def resumen_mercado(estudios, relaciones):

    sedes = len(estudios)

    marcas = relaciones["id_marca"].nunique()

    sedes_por_marca = (
        relaciones
        .groupby("id_marca")
        .size()
    )

    marcas_multisede = (
        sedes_por_marca > 1
    ).sum()

    marcas_individuales = (
        sedes_por_marca == 1
    ).sum()

    sedes_multisede = (
        sedes_por_marca[
            sedes_por_marca > 1
        ].sum()
    )

    top_barrios = (
        estudios["barrio"]
        .value_counts()
        .head(3)
        .index
        .tolist()
    )

    tabla = pd.DataFrame({

        "indicador": [

            "Sedes relevadas",
            "Marcas identificadas",
            "Marcas multisede",
            "Marcas individuales",
            "Sedes pertenecientes a marcas multisede",
            "Seguidores promedio",
            "Puntaje Google promedio",
            "Reseñas promedio",
            "Barrios con mayor oferta"

        ],

        "valor": [

            sedes,
            marcas,
            marcas_multisede,
            marcas_individuales,
            sedes_multisede,
            round(
                estudios["seguidores_instagram"]
                .mean(),
                2
            ),
            round(
                estudios["puntaje_google"]
                .mean(),
                2
            ),
            round(
                estudios["cantidad_resenas"]
                .mean(),
                2
            ),
            ", ".join(top_barrios)

        ]

    })

    return tabla

# =====================================
# BLOQUE 5.2
# DENSIDAD TERRITORIAL
# =====================================

def densidad_barrios(estudios):

    tabla = (
        estudios["barrio"]
        .value_counts()
        .rename_axis("barrio")
        .reset_index(name="estudios")
    )

    total = tabla["estudios"].sum()

    tabla["porcentaje"] = (
        tabla["estudios"]
        / total
        * 100
    ).round(2)

    tabla["acumulado"] = (
        tabla["porcentaje"]
        .cumsum()
        .round(2)
    )

    tabla["ranking"] = (
        tabla.index + 1
    )

    tabla = tabla[
        [
            "ranking",
            "barrio",
            "estudios",
            "porcentaje",
            "acumulado"
        ]
    ]

    return tabla

# =====================================
# BLOQUE 5.3
# ÍNDICE DE SATURACIÓN (DM-002)
# =====================================

def normalizar_minmax(serie):
    """
    Normalización Min-Max entre 0 y 1.
    """

    minimo = serie.min()
    maximo = serie.max()

    if minimo == maximo:
        return pd.Series(
            [0] * len(serie),
            index=serie.index
        )

    return (
        (serie - minimo)
        / (maximo - minimo)
    )

def calcular_saturacion_barrios(
    estudios,
    poblacion
):
    """
    Calcula la presión competitiva relativa por barrio.

    DM-002:
    La saturación se mide principalmente por
    estudios cada 10.000 habitantes.
    """

    estudios = estudios.copy()
    poblacion = poblacion.copy()

    # ---------------------------------
    # Normalización para joins seguros
    # ---------------------------------

    estudios["barrio_normalizado"] = (
        estudios["barrio"]
        .apply(normalizar_barrio)
    )

    poblacion["barrio_normalizado"] = (
        poblacion["barrio"]
        .apply(normalizar_barrio)
    )

    # ---------------------------------
    # Agregación por barrio
    # ---------------------------------

    tabla = (
        estudios
        .groupby("barrio_normalizado")
        .agg(
            estudios=("id_estudio", "count"),
            seguidores_totales=("seguidores_instagram", "sum"),
            puntaje_promedio=("puntaje_google", "mean"),
            resenas_totales=("cantidad_resenas", "sum"),
        )
        .reset_index()
    )

    # ---------------------------------
    # Merge con catálogo territorial
    # ---------------------------------

    tabla = tabla.merge(
        poblacion[
            [
                "barrio_normalizado",
                "barrio",
                "poblacion"
            ]
        ],
        on="barrio_normalizado",
        how="left"
    )

    # ---------------------------------
    # Validación
    # ---------------------------------

    faltantes = (
        tabla[
            tabla["poblacion"].isna()
        ]["barrio_normalizado"]
        .tolist()
    )

    if faltantes:

        raise ValueError(
            "Barrios sin población asignada:\n"
            + "\n".join(
                f" - {b}"
                for b in sorted(faltantes)
            )
        )

    # ---------------------------------
    # Indicador territorial principal
    # ---------------------------------

    tabla["estudios_por_10000"] = (
        tabla["estudios"]
        / tabla["poblacion"]
        * 10000
    ).round(2)

    # ---------------------------------
    # Normalización
    # ---------------------------------

    tabla["densidad_norm"] = normalizar_minmax(
        tabla["estudios_por_10000"]
    )

    tabla["seguidores_norm"] = normalizar_minmax(
        tabla["seguidores_totales"]
    )

    tabla["resenas_norm"] = normalizar_minmax(
        tabla["resenas_totales"]
    )

    # ---------------------------------
    # Índice compuesto (DM-002)
    # ---------------------------------

    tabla["indice_saturacion"] = (
        tabla["densidad_norm"] * 0.70
        + tabla["seguidores_norm"] * 0.20
        + tabla["resenas_norm"] * 0.10
    ).round(3)

    # ---------------------------------
    # Clasificación
    # ---------------------------------

    def clasificar(valor):

        if valor >= 0.75:
            return "Muy alta"

        elif valor >= 0.50:
            return "Alta"

        elif valor >= 0.25:
            return "Baja"

        else:
            return "Muy baja"

    tabla["nivel_saturacion"] = (
        tabla["indice_saturacion"]
        .apply(clasificar)
    )

    tabla = (
        tabla
        .sort_values(
            "indice_saturacion",
            ascending=False
        )
        .reset_index(drop=True)
    )

    tabla["ranking"] = tabla.index + 1

    return tabla[
        [
            "ranking",
            "barrio",
            "estudios",
            "poblacion",
            "estudios_por_10000",
            "seguidores_totales",
            "resenas_totales",
            "puntaje_promedio",
            "indice_saturacion",
            "nivel_saturacion",
        ]
    ]
def calcular_saturacion_zonas(
    estudios,
    poblacion
):
    """
    Agrega el índice de saturación por zona.
    """

    barrios = calcular_saturacion_barrios(
        estudios,
        poblacion
    )

    zonas = (
        estudios[
            [
                "barrio",
                "zona"
            ]
        ]
        .drop_duplicates()
        .merge(
            barrios[
                [
                    "barrio",
                    "indice_saturacion",
                    "estudios_por_10000"
                ]
            ],
            on="barrio",
            how="left"
        )
        .groupby(
            "zona",
            dropna=False
        )
        .agg(
            barrios=("barrio", "count"),
            densidad_media=("estudios_por_10000", "mean"),
            saturacion_media=("indice_saturacion", "mean")
        )
        .reset_index()
    )

    zonas["zona"] = zonas["zona"].fillna("Sin dato")

    zonas["densidad_media"] = zonas[
        "densidad_media"
    ].round(2)

    zonas["saturacion_media"] = zonas[
        "saturacion_media"
    ].round(3)

    return (
        zonas
        .sort_values(
            "saturacion_media",
            ascending=False
        )
        .reset_index(drop=True)
    )
# =====================================
# CONSOLA
# =====================================

def imprimir_resumen(tabla):

    print("\n" + "=" * 60)
    print("RESUMEN EJECUTIVO DEL MERCADO")
    print("=" * 60 + "\n")

    print(tabla.to_string(index=False))

def imprimir_top_barrios(tabla, n=10):

    print("\n" + "=" * 60)
    print("TOP BARRIOS POR DENSIDAD")
    print("=" * 60 + "\n")

    print(
        tabla.head(n).to_string(index=False)
    )
def imprimir_saturacion(tabla, n=10):

    print("\n" + "=" * 60)
    print("TOP BARRIOS POR SATURACIÓN")
    print("=" * 60 + "\n")

    print(
        tabla[
            [
                "ranking",
                "barrio",
                "indice_saturacion",
                "nivel_saturacion"
            ]
        ]
        .head(n)
        .to_string(index=False)
    )

# =====================================
# MAIN
# =====================================

def main():

    print("=" * 70)
    print("MOTOR 5 — INTELIGENCIA DEL MERCADO")
    print("=" * 70)

    print("\n1. Conectando SQLite...")

    con = conectar()

    print("   OK")

    print("\n2. Cargando datos...")

    estudios = cargar_estudios(con)
    relaciones = cargar_marcas(con)
    poblacion = cargar_poblacion()

    print(f"   Sedes: {len(estudios)}")
    print(f"   Relaciones: {len(relaciones)}")
    print(f"   Catálogo territorial: {len(poblacion)} barrios")

    # ---------------------------------
    # 5.1 Resumen Ejecutivo
    # ---------------------------------

    print("\n3. Generando resumen ejecutivo...")

    resumen = resumen_mercado(
        estudios,
        relaciones
    )

    exportar(
        "resumen_mercado",
        resumen
    )

    # ---------------------------------
    # 5.2 Densidad Territorial
    # ---------------------------------

    print("\n4. Calculando densidad territorial...")

    densidad = densidad_barrios(
        estudios
    )

    exportar(
        "densidad_barrios",
        densidad
    )

    # ---------------------------------
    # 5.3 Índice de Saturación
    # ---------------------------------

    print("\n5. Calculando índice de saturación...")

    saturacion_barrios = calcular_saturacion_barrios(
    estudios,
    poblacion
    )

    exportar(
        "saturacion_barrios",
        saturacion_barrios
    )

    saturacion_zonas = calcular_saturacion_zonas(
    estudios,
    poblacion
    )

    exportar(
        "saturacion_zonas",
        saturacion_zonas
    )

    # ---------------------------------
    # Consola
    # ---------------------------------

    imprimir_resumen(resumen)
    imprimir_top_barrios(densidad)
    imprimir_saturacion(saturacion_barrios)

    con.close()

    print("\n" + "=" * 70)
    print("MOTOR 5 COMPLETADO")
    print("=" * 70)


if __name__ == "__main__":
    main()