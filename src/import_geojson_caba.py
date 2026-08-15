# =====================================
# OBSERVATORIO PILATES TRANSVERSO
# IMPORTADOR DE GEOJSON CABA
# =====================================

from pathlib import Path
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

DESTINO = ROOT / "data" / "reference" / "caba" / "barrios.geojson"
DESTINO.parent.mkdir(parents=True, exist_ok=True)

NOMBRE_ARCHIVO = "barrios.geojson"

lugares = [
    ROOT,
    ROOT / "data",
    ROOT / "data" / "reference",
    HOME / "Downloads",
    HOME / "Descargas",
    HOME / "Desktop",
    HOME / "Escritorio",
    HOME / "OneDrive" / "Downloads",
    HOME / "OneDrive" / "Descargas",
    HOME / "OneDrive" / "Desktop",
    HOME / "OneDrive" / "Escritorio",
]

origen = None

for carpeta in lugares:

    if carpeta.exists():

        encontrados = list(carpeta.rglob(NOMBRE_ARCHIVO))

        if encontrados:

            origen = encontrados[0]
            break

if origen is None:

    raise FileNotFoundError(
        f"No encontré '{NOMBRE_ARCHIVO}'.\n\n"
        "Descargalo y dejalo en Descargas o Escritorio."
    )

print(f"Archivo encontrado:\n{origen}\n")

# Validación básica del GeoJSON
with open(origen, encoding="utf-8") as f:

    geo = json.load(f)

if geo.get("type") != "FeatureCollection":

    raise ValueError("El archivo no es un GeoJSON válido.")

cantidad = len(geo.get("features", []))

print(f"Features detectadas: {cantidad}")

if cantidad != 48:

    print(
        "\nAviso: no tiene exactamente 48 features."
        "\nVerificá que sean los barrios de CABA."
    )

shutil.copy2(origen, DESTINO)

print("\nGeoJSON importado correctamente.")
print(DESTINO)