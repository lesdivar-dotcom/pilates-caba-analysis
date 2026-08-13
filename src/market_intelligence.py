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

# =====================================
# SQLITE
# =====================================

def conectar():

    if not DB_PATH.exists():

        raise FileNotFoundError(
            f"No existe la base SQLite:\n{DB_PATH}"
        )

    return sqlite3.connect(DB_PATH)

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

    print(f"   Sedes: {len(estudios)}")
    print(f"   Relaciones: {len(relaciones)}")

    print("\n3. Generando resumen ejecutivo...")

    resumen = resumen_mercado(
        estudios,
        relaciones
    )

    exportar(
        "resumen_mercado",
        resumen
    )

    print("\n4. Calculando densidad territorial...")

    densidad = densidad_barrios(
        estudios
    )

    exportar(
        "densidad_barrios",
        densidad
    )

    imprimir_resumen(resumen)
    imprimir_top_barrios(densidad)

    con.close()

    print("\n" + "=" * 70)
    print("MOTOR 5 COMPLETADO")
    print("=" * 70)

if __name__ == "__main__":
    main()