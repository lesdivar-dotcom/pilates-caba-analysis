# =====================================
# OBSERVATORIO PILATES TRANSVERSO
# MOTOR 5.4 — ÍNDICE DE OPORTUNIDAD
# =====================================

"""
Motor 5.4

Genera el Índice de Oportunidad del Observatorio.

Salida principal:

    data/intelligence/oportunidad_barrios.csv
"""

from pathlib import Path
import sqlite3
import unicodedata

import pandas as pd


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

POBLACION_PATH = (
    ROOT
    / "data"
    / "reference"
    / "caba"
    / "barrios_poblacion.csv"
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


# =====================================
# UTILIDADES
# =====================================

def conectar():

    if not DB_PATH.exists():

        raise FileNotFoundError(
            f"No existe SQLite:\n{DB_PATH}"
        )

    return sqlite3.connect(DB_PATH)


def normalizar(texto):

    if pd.isna(texto):
        return texto

    texto = str(texto).strip()

    texto = "".join(
        c
        for c in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(c)
    )

    texto = texto.title()

    equivalencias = {

        "Villa Gral. Mitre":
        "Villa General Mitre",

        "Villa Gral Mitre":
        "Villa General Mitre",

        "San Nicolas":
        "San Nicolas",

        "Velez Sarsfield":
        "Velez Sarsfield",

        "Nunez":
        "Nunez"

    }

    return equivalencias.get(
        texto,
        texto
    )


def minmax(serie):

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


# =====================================
# CARGA
# =====================================

def cargar_estudios(con):

    estudios = pd.read_sql(
        "SELECT * FROM estudios",
        con
    )

    estudios["barrio_norm"] = (
        estudios["barrio"]
        .apply(normalizar)
    )

    return estudios


def cargar_relaciones(con):

    return pd.read_sql(
        "SELECT * FROM estudio_marca",
        con
    )


def cargar_poblacion():

    poblacion = pd.read_csv(
        POBLACION_PATH,
        encoding="utf-8-sig"
    )

    poblacion["barrio_norm"] = (
        poblacion["barrio"]
        .apply(normalizar)
    )

    return poblacion


# =====================================
# SATURACIÓN BASE
# =====================================
def calcular_saturacion(
    estudios,
    poblacion
):
    """
    Calcula la saturación territorial tomando como base
    los 48 barrios oficiales del catálogo territorial.
    """

    # ---------------------------------
    # Base territorial (48 barrios)
    # ---------------------------------

    tabla = poblacion[
        [
            "barrio_norm",
            "barrio",
            "poblacion"
        ]
    ].copy()

    # ---------------------------------
    # Estadísticas de los estudios
    # ---------------------------------

    estadisticas = (
        estudios
        .groupby("barrio_norm")
        .agg(
            estudios=("id_estudio", "count"),
            seguidores=("seguidores_instagram", "sum"),
            resenas=("cantidad_resenas", "sum"),
        )
        .reset_index()
    )

    # ---------------------------------
    # Merge
    # ---------------------------------

    tabla = tabla.merge(
        estadisticas,
        on="barrio_norm",
        how="left"
    )

    # ---------------------------------
    # Barrios sin estudios
    # ---------------------------------

    tabla["estudios"] = (
        tabla["estudios"]
        .fillna(0)
        .astype(int)
    )

    tabla["seguidores"] = (
        tabla["seguidores"]
        .fillna(0)
    )

    tabla["resenas"] = (
        tabla["resenas"]
        .fillna(0)
    )

    # ---------------------------------
    # Estudios cada 10.000 habitantes
    # ---------------------------------

    tabla["estudios_por_10000"] = (
        tabla["estudios"]
        / tabla["poblacion"]
        * 10000
    )

    # ---------------------------------
    # Índice de saturación normalizado
    # ---------------------------------

    tabla["saturacion"] = minmax(
        tabla["estudios_por_10000"]
    )

    return tabla
# =====================================
# ÍNDICE DE OPORTUNIDAD
# =====================================

def calcular_oportunidad(
    estudios,
    relaciones,
    poblacion
):

    sat = calcular_saturacion(
        estudios,
        poblacion
    )

    # ---------------------------------
    # Concentración de marcas
    # ---------------------------------

    marcas = relaciones.merge(

        estudios[
            [
                "id_estudio",
                "barrio_norm"
            ]
        ],

        on="id_estudio"

    )

    concentracion = (
        marcas
        .groupby("barrio_norm")["id_marca"]
        .nunique()
        .reset_index(name="marcas")
    )

    sat = sat.merge(
        concentracion,
        on="barrio_norm",
        how="left"
    )

    # Un barrio sin estudios tiene cero marcas.
    sat["marcas"] = (
       sat["marcas"]
       .fillna(0)
       .astype(int)
    )
    
    sat["poblacion_norm"] = minmax(
        sat["poblacion"]
    )

    sat["digital_norm"] = minmax(
        sat["seguidores"]
    )

    sat["marcas_norm"] = minmax(
        sat["marcas"]
    )

    sat["oportunidad"] = (

        0.50 * (1 - sat["saturacion"])
        + 0.20 * sat["poblacion_norm"]
        + 0.15 * (1 - sat["digital_norm"])
        + 0.15 * (1 - sat["marcas_norm"])

    )

    sat["oportunidad"] = (
        sat["oportunidad"]
        * 100
    ).round(1)

    def categoria(valor):

        if valor >= 75:
            return "Alta"

        elif valor >= 50:
            return "Media"

        elif valor >= 25:
            return "Maduro"

        else:
            return "Alta competencia"

    sat["categoria"] = (
        sat["oportunidad"]
        .apply(categoria)
    )

    sat = sat.sort_values(
        "oportunidad",
        ascending=False
    ).reset_index(drop=True)

    sat["ranking"] = sat.index + 1

    sat["explicacion"] = sat.apply(

        lambda x:
        (
            "Baja saturación y buena población."
            if x["categoria"] == "Alta"
            else
            "Mercado competitivo."
        ),

        axis=1

    )

    return sat[
        [
            "ranking",
            "barrio",
            "oportunidad",
            "categoria",
            "estudios",
            "poblacion",
            "estudios_por_10000",
            "marcas",
            "explicacion"
        ]
    ]


# =====================================
# MAIN
# =====================================

def main():

    print("=" * 70)
    print("MOTOR 5.4 — ÍNDICE DE OPORTUNIDAD")
    print("=" * 70)

    con = conectar()

    estudios = cargar_estudios(con)
    relaciones = cargar_relaciones(con)
    poblacion = cargar_poblacion()

    oportunidad = calcular_oportunidad(

        estudios,
        relaciones,
        poblacion

    )

    salida = (
        OUTPUT
        / "oportunidad_barrios.csv"
    )

    oportunidad.to_csv(

        salida,
        index=False,
        encoding="utf-8-sig"

    )

    print("\nTOP 10 BARRIOS CON MAYOR OPORTUNIDAD\n")

    print(

        oportunidad[
            [
                "ranking",
                "barrio",
                "oportunidad",
                "categoria"
            ]
        ]
        .head(10)
        .to_string(index=False)

    )

    print(f"\nArchivo generado:\n{salida}")

    con.close()

    print("\nMOTOR 5.4 COMPLETADO")


if __name__ == "__main__":
    main()