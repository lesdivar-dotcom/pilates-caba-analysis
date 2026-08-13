#import_poblacion_caba.py
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

OUTPUT = ROOT / "data" / "reference" / "caba" / "barrios_poblacion.csv"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Nombre esperado del archivo original
NOMBRE_ARCHIVO = "caba_pob_barrios_2010.csv"

# Lugares donde buscar
lugares = [
    ROOT,
    ROOT / "data",
    ROOT / "data" / "reference",
    HOME / "Downloads",
    HOME / "Descargas",
    HOME / "Desktop",
    HOME / "Escritorio",
    HOME / "OneDrive" / "Desktop",
    HOME / "OneDrive" / "Escritorio",
]

INPUT = None

for carpeta in lugares:
    if carpeta.exists():
        encontrado = list(carpeta.rglob(NOMBRE_ARCHIVO))
        if encontrado:
            INPUT = encontrado[0]
            break

if INPUT is None:
    raise FileNotFoundError(
        f"No encontré '{NOMBRE_ARCHIVO}'.\n\n"
        "Copialo al proyecto o indicame dónde está."
    )

print(f"Archivo encontrado:\n{INPUT}\n")

# Leer CSV oficial
df = pd.read_csv(INPUT, encoding="utf-8-sig")

# Normalizar columnas
df = df.rename(columns={
    "BARRIO": "barrio",
    "POBLACION": "poblacion"
})

# Normalizar nombres
df["barrio"] = (
    df["barrio"]
    .astype(str)
    .str.strip()
    .str.title()
    .replace({"Núñez": "Nuñez"})
)

# Metadatos
df["fuente"] = "Censo Nacional"
df["anio"] = 2010

# Validación
if len(df) != 48:
    raise ValueError(f"Se esperaban 48 barrios y llegaron {len(df)}")

# Guardar catálogo oficial
df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("Catálogo territorial creado correctamente.")
print(OUTPUT)
print(f"Barrios: {len(df)}")