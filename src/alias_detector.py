# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.0 — Alias Detector
# Archivo: alias_detector.py
# ============================================================

from pathlib import Path
from difflib import SequenceMatcher

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

MARCAS_PATH = DATA / "processed" / "estudios_marcas.csv"


# ------------------------------------------------------------
# Normalización
# ------------------------------------------------------------

def normalizar(texto):

    if texto is None:
        return ""

    texto = str(texto).lower().strip()

    reemplazos = {
        "á":"a","é":"e","í":"i","ó":"o","ú":"u","ü":"u","ñ":"n"
    }

    for a,b in reemplazos.items():
        texto = texto.replace(a,b)

    texto = texto.replace("®","")
    texto = texto.replace("•"," ")
    texto = " ".join(texto.split())

    return texto


# ------------------------------------------------------------
# Cargar catálogo oficial
# ------------------------------------------------------------

def cargar_marcas():

    if not MARCAS_PATH.exists():
        raise FileNotFoundError(MARCAS_PATH)

    df = pd.read_csv(MARCAS_PATH)

    marcas = sorted(
        df["nombre_marca"].dropna().unique().tolist()
    )

    return marcas


# ------------------------------------------------------------
# Similaridad
# ------------------------------------------------------------

def similitud(a,b):

    return SequenceMatcher(
        None,
        normalizar(a),
        normalizar(b)
    ).ratio()


# ------------------------------------------------------------
# Buscar mejor candidato
# ------------------------------------------------------------

def detectar_alias(nombre, umbral=0.90):

    catalogo = cargar_marcas()

    mejor = None
    mejor_score = 0

    for marca in catalogo:

        score = similitud(nombre,marca)

        if score > mejor_score:

            mejor_score = score
            mejor = marca

    if mejor_score >= umbral:

        return {
            "encontrado":True,
            "marca":mejor,
            "score":round(mejor_score,3)
        }

    return {
        "encontrado":False,
        "marca":None,
        "score":round(mejor_score,3)
    }


# ------------------------------------------------------------
# Top candidatos
# ------------------------------------------------------------

def top_candidatos(nombre,n=5):

    catalogo = cargar_marcas()

    ranking=[]

    for marca in catalogo:

        ranking.append((
            marca,
            similitud(nombre,marca)
        ))

    ranking=sorted(
        ranking,
        key=lambda x:x[1],
        reverse=True
    )

    return [
        {
            "marca":m,
            "score":round(s,3)
        }
        for m,s in ranking[:n]
    ]


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------

if __name__=="__main__":

    print("="*60)
    print("ALIAS DETECTOR")
    print("="*60)

    pruebas=[

        "Almha Pilates",
        "Haus Casa de Pilates®",
        "Mr Pilates Reformer",
        "Tu mundo pilates"

    ]

    for p in pruebas:

        print(f"\nEntrada: {p}")

        r=detectar_alias(p)

        print("Resultado:",r)

        print("Top candidatos:")

        for c in top_candidatos(p,3):

            print("  ",c)