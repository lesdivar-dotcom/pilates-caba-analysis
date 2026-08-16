# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 8.4 — Report Builder
# Archivo: report_builder.py
#
# Genera el Intelligence Report oficial del Observatorio
# utilizando exclusivamente SQLite (DM-014).
# ============================================================

from pathlib import Path
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate

from report_templates import construir_documento, footer

ROOT = Path(__file__).resolve().parent.parent

REPORT_DIR = ROOT / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# VERSIONES
# ============================================================

VERSION = "v1.0-caba-rc1"


def nombre_archivo(version):

    return REPORT_DIR / f"Observatorio_Pilates_CABA_{version}.pdf"


# ============================================================
# GENERAR PDF
# ============================================================

def generar_pdf(version=VERSION):

    salida = nombre_archivo(version)

    story = construir_documento(version)

    # Guardamos la cantidad ANTES de que ReportLab consuma la lista
    elementos = len(story)

    doc = SimpleDocTemplate(

        str(salida),

        pagesize=(210*72/25.4, 297*72/25.4),

        leftMargin=18*72/25.4,
        rightMargin=18*72/25.4,
        topMargin=18*72/25.4,
        bottomMargin=18*72/25.4

    )

    doc.build(

        story,

        onFirstPage=lambda c, d: footer(c, d, version),

        onLaterPages=lambda c, d: footer(c, d, version)

    )

    return salida, elementos

# ============================================================
# INFORMACIÓN DEL REPORTE
# ============================================================

def resumen():

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    return {

        "version": VERSION,

        "fecha": fecha,

        "destino": nombre_archivo(VERSION)

    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("="*60)
    print("INTELLIGENCE REPORT")
    print("="*60)

    info = resumen()

    print(f"\nVersión : {info['version']}")
    print(f"Fecha   : {info['fecha']}")

    print("\nConstruyendo documento...")

    salida, elementos = generar_pdf(info["version"])

    print("\n" + "="*60)
    print("REPORTE GENERADO")
    print("="*60)

    print(f"\nElementos ensamblados : {elementos}")
    print(f"Archivo               : {salida}")

    print("\nMotor 8.4 completado.")


if __name__ == "__main__":

    main()