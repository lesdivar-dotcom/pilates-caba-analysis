# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 8.3 — Report Templates
# Archivo: report_templates.py
#
# Maquetación editorial del Intelligence Report.
# ============================================================

from datetime import datetime
from pathlib import Path

from reportlab.platypus import (
    Spacer,
    Image,
    PageBreak
)
from reportlab.lib.units import mm

from report_assets import (
    portada,
    fila_kpis,
    panel,
    tabla_editorial,
    divisor,
    footer,
    CONTENT_WIDTH
)

from report_charts import (
    obtener_kpis,
    top_barrios,
    generar_todos
)

ROOT = Path(__file__).resolve().parent.parent
REPORT_ASSETS = ROOT / "data" / "reports" / "assets"


# ============================================================
# PORTADA
# ============================================================

def seccion_portada(version):

    fecha = datetime.now().strftime("%d/%m/%Y")

    return portada(fecha, version)


# ============================================================
# RESUMEN EJECUTIVO
# ============================================================

def seccion_resumen():

    k = obtener_kpis()

    return panel(
        "Resumen Ejecutivo",
        (
            f"El Observatorio registra actualmente "
            f"<b>{k['estudios']} estudios</b>, "
            f"<b>{k['marcas']} marcas</b> y "
            f"<b>{k['cadenas']} cadenas multisede</b> "
            "distribuidas en los 48 barrios oficiales de la Ciudad Autónoma de Buenos Aires."
        )
    )


# ============================================================
# KPIs
# ============================================================

def seccion_kpis():

    k = obtener_kpis()

    elementos = []

    elementos.append(Spacer(1, 6))

    elementos.append(

        fila_kpis([

            (k["estudios"], "Estudios", "vino"),
            (k["marcas"], "Marcas", "rojo"),
            (k["cadenas"], "Cadenas", "terracota"),
            ("48", "Barrios", "verde")

        ])

    )

    elementos.append(Spacer(1, 12))

    return elementos


# ============================================================
# MAPA
# ============================================================

def seccion_mapa():

    elementos = []

    elementos += panel(
        "Mapa Territorial",
        "La distribución territorial constituye la fotografía oficial utilizada por el Observatorio."
    )

    elementos.append(

        Image(
            str(REPORT_ASSETS / "distribucion_barrios.png"),
            width=CONTENT_WIDTH,
            height=72 * mm
        )

    )

    elementos.append(Spacer(1, 8))

    return elementos


# ============================================================
# TOP BARRIOS
# ============================================================

def seccion_top_barrios():

    elementos = []

    elementos += panel(
        "Ranking Territorial",
        "Los barrios con mayor concentración actual permiten visualizar el equilibrio entre saturación y oportunidad."
    )

    elementos.append(

        Image(
            str(REPORT_ASSETS / "top_barrios.png"),
            width=CONTENT_WIDTH,
            height=70 * mm
        )

    )

    elementos.append(Spacer(1, 8))

    datos = top_barrios()

    filas = [

        [i + 1, d[0], d[1]]

        for i, d in enumerate(datos)

    ]

    elementos.append(

        tabla_editorial(
            ["#", "Barrio", "Estudios"],
            filas,
            anchos=[14 * mm, 92 * mm, 26 * mm]
        )

    )

    return elementos


# ============================================================
# MARCAS
# ============================================================

def seccion_marcas():

    elementos = []

    elementos += panel(
        "Concentración de Marcas",
        "La estructura competitiva del mercado combina una amplia base de operadores independientes con cadenas multisede."
    )

    elementos.append(

        Image(
            str(REPORT_ASSETS / "concentracion_marcas.png"),
            width=82 * mm,
            height=82 * mm
        )

    )

    elementos.append(Spacer(1, 6))

    return elementos


# ============================================================
# CADENAS
# ============================================================

def seccion_cadenas():

    elementos = []

    elementos += panel(
        "Cadenas Multisede",
        "Las cadenas representan un fenómeno todavía contenido, pero con capacidad de expansión sobre nuevos territorios."
    )

    elementos.append(

        Image(
            str(REPORT_ASSETS / "cadenas_multisede.png"),
            width=CONTENT_WIDTH,
            height=72 * mm
        )

    )

    elementos.append(Spacer(1, 8))

    return elementos


# ============================================================
# HALLAZGOS
# ============================================================

def seccion_hallazgos():

    return panel(
        "Hallazgos Editoriales",
        (
            "• Flores continúa consolidándose como uno de los territorios más relevantes del mercado.<br/><br/>"
            "• La coexistencia de operadores independientes y cadenas sugiere una estructura todavía fragmentada.<br/><br/>"
            "• El sistema editorial permite incorporar nuevos estudios sin comprometer la consistencia histórica del Observatorio."
        )
    )


# ============================================================
# METODOLOGÍA
# ============================================================

def seccion_metodologia():

    return panel(
        "Metodología",
        (
            "El Intelligence Report se genera exclusivamente desde SQLite (DM-014) "
            "e incorpora las decisiones metodológicas DM-001 a DM-014 congeladas durante el desarrollo del Observatorio Transverso."
        )
    )


# ============================================================
# DOCUMENTO COMPLETO
# ============================================================

def construir_documento(version="v1.0"):

    # Garantiza que los gráficos existan
    generar_todos()

    story = []

    # Portada
    story += seccion_portada(version)

    story.append(PageBreak())

    # Resumen
    story += seccion_resumen()

    story += seccion_kpis()

    story.append(divisor())

    # Mapa
    story += seccion_mapa()

    story.append(divisor())

    # Ranking
    story += seccion_top_barrios()

    story.append(PageBreak())

    # Marcas
    story += seccion_marcas()

    story.append(divisor())

    # Cadenas
    story += seccion_cadenas()

    story.append(divisor())

    # Hallazgos
    story += seccion_hallazgos()

    story.append(divisor())

    # Metodología
    story += seccion_metodologia()

    # ESTE RETURN ES EL CRÍTICO
    return story


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "construir_documento",
    "footer"
]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("REPORT TEMPLATES")
    print("=" * 60)

    story = construir_documento("v1.0-caba-rc1")

    print(f"Story construida: {len(story)} elementos")
    print("Componentes ensamblados correctamente.")