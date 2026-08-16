# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 8.1 — Report Assets
# Archivo: report_assets.py
#
# Design System oficial para los informes ejecutivos PDF.
# No genera el PDF: provee paleta, tipografía, estilos y
# componentes reutilizables para report_templates.py.
# ============================================================

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer

# ============================================================
# PALETA OFICIAL TRANSVERSO (congelada)
# ============================================================

COLORS = {

    "negro": HexColor("#000000"),
    "vino": HexColor("#220000"),
    "rojo": HexColor("#7A0000"),
    "rojo_intenso": HexColor("#A30000"),

    "verde": HexColor("#5C7A3A"),
    "arena": HexColor("#A88A4A"),
    "terracota": HexColor("#8A5A3A"),
    "borgona": HexColor("#6A2E2E"),

    "texto": HexColor("#23313D"),
    "texto_suave": HexColor("#6B7A86"),

    "fondo": HexColor("#F7F9FB"),
    "panel": HexColor("#FFFFFF"),

    "gris": HexColor("#D9D9D9")

}

# ============================================================
# MÁRGENES
# ============================================================

PAGE_MARGIN = 18 * mm
CONTENT_WIDTH = 174 * mm

# ============================================================
# TIPOGRAFÍA
# ============================================================

styles = getSampleStyleSheet()

TITLE_STYLE = styles["Title"].clone("TransversoTitle")
TITLE_STYLE.fontName = "Helvetica-Bold"
TITLE_STYLE.fontSize = 28
TITLE_STYLE.leading = 34
TITLE_STYLE.textColor = COLORS["vino"]
TITLE_STYLE.alignment = TA_LEFT
TITLE_STYLE.spaceAfter = 8

SUBTITLE_STYLE = styles["Heading2"].clone("TransversoSubtitle")
SUBTITLE_STYLE.fontName = "Helvetica"
SUBTITLE_STYLE.fontSize = 15
SUBTITLE_STYLE.leading = 20
SUBTITLE_STYLE.textColor = COLORS["texto_suave"]
SUBTITLE_STYLE.spaceAfter = 10

SECTION_STYLE = styles["Heading1"].clone("TransversoSection")
SECTION_STYLE.fontName = "Helvetica-Bold"
SECTION_STYLE.fontSize = 18
SECTION_STYLE.leading = 22
SECTION_STYLE.textColor = COLORS["vino"]
SECTION_STYLE.spaceBefore = 10
SECTION_STYLE.spaceAfter = 8

BODY_STYLE = styles["BodyText"].clone("TransversoBody")
BODY_STYLE.fontName = "Helvetica"
BODY_STYLE.fontSize = 10.5
BODY_STYLE.leading = 16
BODY_STYLE.textColor = COLORS["texto"]
BODY_STYLE.alignment = TA_LEFT

CAPTION_STYLE = styles["Italic"].clone("TransversoCaption")
CAPTION_STYLE.fontName = "Helvetica-Oblique"
CAPTION_STYLE.fontSize = 8.5
CAPTION_STYLE.leading = 11
CAPTION_STYLE.textColor = COLORS["texto_suave"]
CAPTION_STYLE.alignment = TA_CENTER

# ============================================================
# PORTADA
# ============================================================

def portada(fecha, version):

    elementos = []

    elementos.append(Spacer(1, 35 * mm))

    logo = Paragraph(
        "<font color='#220000' size=34><b>TRANSVERSO</b></font>",
        TITLE_STYLE
    )

    elementos.append(logo)

    elementos.append(
        Paragraph(
            "Observatorio Pilates",
            SUBTITLE_STYLE
        )
    )

    elementos.append(Spacer(1, 8 * mm))

    elementos.append(

        Paragraph(
            "<font size=20><b>Ciudad Autónoma de Buenos Aires</b></font>",
            SECTION_STYLE
        )

    )

    elementos.append(Spacer(1, 10 * mm))

    texto = (
        "Radiografía editorial del mercado de Pilates en la Ciudad Autónoma "
        "de Buenos Aires."
    )

    elementos.append(
        Paragraph(texto, BODY_STYLE)
    )

    elementos.append(Spacer(1, 22 * mm))

    meta = (
        f"<b>Versión:</b> {version}<br/>"
        f"<b>Fecha:</b> {fecha}<br/>"
        "<b>Serie:</b> Intelligence Report"
    )

    elementos.append(
        Paragraph(meta, BODY_STYLE)
    )

    return elementos

# ============================================================
# TARJETAS KPI
# ============================================================

def tarjeta_kpi(valor, titulo, color="vino"):

    tabla = Table(

        [

            [Paragraph(
                f"<font color='white' size=20><b>{valor}</b></font>",
                CAPTION_STYLE
            )],

            [Paragraph(
                f"<font color='white' size=10>{titulo}</font>",
                CAPTION_STYLE
            )]

        ],

        colWidths=[40 * mm]

    )

    tabla.setStyle(

        TableStyle([

            ("BACKGROUND", (0,0), (-1,-1), COLORS[color]),

            ("BOX", (0,0), (-1,-1), 0, COLORS[color]),

            ("TOPPADDING", (0,0), (-1,-1), 12),

            ("BOTTOMPADDING", (0,0), (-1,-1), 12),

            ("ALIGN", (0,0), (-1,-1), "CENTER"),

            ("VALIGN", (0,0), (-1,-1), "MIDDLE")

        ])

    )

    return tabla

def fila_kpis(kpis):

    tablas = []

    for valor, titulo, color in kpis:

        tablas.append(
            tarjeta_kpi(valor, titulo, color)
        )

    fila = Table(

        [tablas],

        colWidths=[42*mm]*len(tablas)

    )

    fila.setStyle(

        TableStyle([

            ("BOTTOMPADDING",(0,0),(-1,-1),6)

        ])

    )

    return fila

# ============================================================
# PANEL EDITORIAL
# ============================================================

def panel(titulo, contenido):

    elementos = []

    elementos.append(
        Paragraph(titulo, SECTION_STYLE)
    )

    elementos.append(
        Paragraph(contenido, BODY_STYLE)
    )

    elementos.append(
        Spacer(1, 4 * mm)
    )

    return elementos

# ============================================================
# TABLAS EJECUTIVAS
# ============================================================

def tabla_editorial(encabezados, filas, anchos=None):

    data = [encabezados] + filas

    tabla = Table(
        data,
        colWidths=anchos
    )

    tabla.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),COLORS["vino"]),
            ("TEXTCOLOR",(0,0),(-1,0),COLORS["panel"]),

            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

            ("FONTNAME",(0,1),(-1,-1),"Helvetica"),

            ("FONTSIZE",(0,0),(-1,-1),9),

            ("ROWBACKGROUNDS",(0,1),(-1,-1),
                [COLORS["panel"], COLORS["fondo"]]),

            ("GRID",(0,0),(-1,-1),0.25,COLORS["gris"]),

            ("BOTTOMPADDING",(0,0),(-1,0),8),
            ("TOPPADDING",(0,1),(-1,-1),7),
            ("BOTTOMPADDING",(0,1),(-1,-1),7),

            ("ALIGN",(0,0),(-1,-1),"LEFT")

        ])

    )

    return tabla

# ============================================================
# DIVISOR
# ============================================================

def divisor():

    t = Table([[""]], colWidths=[CONTENT_WIDTH])

    t.setStyle(

        TableStyle([

            ("LINEABOVE",(0,0),(-1,0),0.8,COLORS["gris"])

        ])

    )

    return t

# ============================================================
# PIE DE PÁGINA
# ============================================================

def footer(canvas, doc, version="v1.0"):

    canvas.saveState()

    canvas.setFont("Helvetica",8)
    canvas.setFillColor(COLORS["texto_suave"])

    canvas.drawString(
        PAGE_MARGIN,
        10*mm,
        f"Observatorio Pilates Transverso · {version}"
    )

    canvas.drawRightString(
        210*mm - PAGE_MARGIN,
        10*mm,
        str(doc.page)
    )

    canvas.restoreState()

# ============================================================
# TEST VISUAL
# ============================================================

if __name__ == "__main__":

    print("="*60)
    print("REPORT ASSETS")
    print("="*60)
    print("Paleta oficial:", len(COLORS), "colores")
    print("Márgenes:", PAGE_MARGIN/mm, "mm")
    print("Componentes disponibles:")
    print(" • portada()")
    print(" • tarjeta_kpi()")
    print(" • fila_kpis()")
    print(" • panel()")
    print(" • tabla_editorial()")
    print(" • divisor()")
    print(" • footer()")