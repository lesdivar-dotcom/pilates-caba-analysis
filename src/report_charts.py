# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 8.2 — Report Charts
# Archivo: report_charts.py
#
# Genera todas las visualizaciones editoriales del
# Intelligence Report utilizando exclusivamente SQLite.
# ============================================================

from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt

from report_assets import COLORS

ROOT = Path(__file__).resolve().parent.parent

DB_PATH = ROOT / "data" / "database" / "observatorio_pilates.db"
OUTPUT_DIR = ROOT / "data" / "reports" / "assets"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MATPLOTLIB
# ============================================================

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["figure.facecolor"] = "white"


# ============================================================
# CONEXIÓN SQLITE
# ============================================================

def conectar():

    return sqlite3.connect(DB_PATH)


# ============================================================
# KPIs
# ============================================================

def obtener_kpis():

    conn = conectar()

    estudios = conn.execute(
        "SELECT COUNT(*) FROM estudios"
    ).fetchone()[0]

    marcas = conn.execute(
        "SELECT COUNT(*) FROM marcas"
    ).fetchone()[0]

    cadenas = conn.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT id_marca
            FROM estudio_marca
            GROUP BY id_marca
            HAVING COUNT(*)>1
        )
    """).fetchone()[0]

    conn.close()

    return {

        "estudios": estudios,
        "marcas": marcas,
        "cadenas": cadenas

    }


# ============================================================
# TOP BARRIOS
# ============================================================

def top_barrios():

    conn = conectar()

    df = conn.execute("""
        SELECT barrio,
               COUNT(*) AS estudios
        FROM estudios
        GROUP BY barrio
        ORDER BY estudios DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return df


# ============================================================
# CONCENTRACIÓN DE MARCAS
# ============================================================

def concentracion_marcas():

    conn = conectar()

    independientes = conn.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT id_marca
            FROM estudio_marca
            GROUP BY id_marca
            HAVING COUNT(*)=1
        )
    """).fetchone()[0]

    cadenas = conn.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT id_marca
            FROM estudio_marca
            GROUP BY id_marca
            HAVING COUNT(*)>1
        )
    """).fetchone()[0]

    conn.close()

    return independientes, cadenas


# ============================================================
# DISTRIBUCIÓN POR BARRIO
# ============================================================

def distribucion_barrios():

    conn = conectar()

    datos = conn.execute("""
        SELECT barrio,
               COUNT(*) AS estudios
        FROM estudios
        GROUP BY barrio
        ORDER BY estudios DESC
    """).fetchall()

    conn.close()

    return datos


# ============================================================
# GRÁFICO 1
# Top Barrios
# ============================================================

def chart_top_barrios():

    datos = top_barrios()

    barrios = [d[0] for d in datos][::-1]
    valores = [d[1] for d in datos][::-1]

    fig, ax = plt.subplots(figsize=(7,4))

    ax.barh(

        barrios,
        valores,

        color="#7A0000"

    )

    ax.set_title(
        "Top barrios por cantidad de estudios",
        fontsize=13,
        weight="bold"
    )

    ax.set_xlabel("Estudios")

    plt.tight_layout()

    path = OUTPUT_DIR / "top_barrios.png"

    plt.savefig(path, dpi=220)

    plt.close()

    return path


# ============================================================
# GRÁFICO 2
# Donut Marcas
# ============================================================

def chart_concentracion():

    independientes, cadenas = concentracion_marcas()

    fig, ax = plt.subplots(figsize=(4.8,4.8))

    ax.pie(

        [independientes, cadenas],

        labels=["Independientes", "Cadenas"],

        colors=[

            "#A88A4A",

            "#220000"

        ],

        wedgeprops=dict(width=0.45)

    )

    ax.set_title(
        "Concentración de marcas",
        fontsize=13,
        weight="bold"
    )

    path = OUTPUT_DIR / "concentracion_marcas.png"

    plt.tight_layout()

    plt.savefig(path, dpi=220)

    plt.close()

    return path


# ============================================================
# GRÁFICO 3
# Distribución territorial
# ============================================================

def chart_distribucion():

    datos = distribucion_barrios()

    barrios = [d[0] for d in datos]
    valores = [d[1] for d in datos]

    fig, ax = plt.subplots(figsize=(10,4))

    ax.plot(

        range(len(valores)),

        valores,

        color="#5C7A3A",

        linewidth=2.5

    )

    ax.fill_between(

        range(len(valores)),

        valores,

        color="#5C7A3A",

        alpha=0.18

    )

    ax.set_title(
        "Distribución territorial",
        fontsize=13,
        weight="bold"
    )

    ax.set_ylabel("Estudios")
    ax.set_xticks([])

    path = OUTPUT_DIR / "distribucion_barrios.png"

    plt.tight_layout()

    plt.savefig(path, dpi=220)

    plt.close()

    return path


# ============================================================
# GRÁFICO 4
# Cadenas multisede
# ============================================================

def chart_cadenas():

    conn = conectar()

    datos = conn.execute("""
        SELECT m.nombre_marca,
               COUNT(*) AS sedes
        FROM estudio_marca em
        JOIN marcas m
          ON em.id_marca=m.id_marca
        GROUP BY m.id_marca
        HAVING sedes>1
        ORDER BY sedes DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    nombres = [d[0] for d in datos][::-1]
    sedes = [d[1] for d in datos][::-1]

    fig, ax = plt.subplots(figsize=(7,4))

    ax.barh(

        nombres,
        sedes,

        color="#8A5A3A"

    )

    ax.set_title(
        "Cadenas multisede",
        fontsize=13,
        weight="bold"
    )

    ax.set_xlabel("Sedes")

    path = OUTPUT_DIR / "cadenas_multisede.png"

    plt.tight_layout()

    plt.savefig(path, dpi=220)

    plt.close()

    return path


# ============================================================
# GENERAR TODO
# ============================================================

def generar_todos():

    rutas = {

        "top_barrios": chart_top_barrios(),
        "concentracion": chart_concentracion(),
        "distribucion": chart_distribucion(),
        "cadenas": chart_cadenas()

    }

    return rutas


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("="*60)
    print("REPORT CHARTS")
    print("="*60)

    print("\nKPIs")

    print(obtener_kpis())

    print("\nGenerando gráficos...")

    rutas = generar_todos()

    for nombre, ruta in rutas.items():

        print(f"✔ {nombre}: {ruta}")