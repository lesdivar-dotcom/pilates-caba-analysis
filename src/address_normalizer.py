# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.3.2 — Address Normalizer
# ============================================================

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DICT_PATH = ROOT / "data" / "reference" / "address_dictionary.json"


# ------------------------------------------------------------
# Cargar diccionario
# ------------------------------------------------------------

def cargar_diccionario():

    with open(DICT_PATH, encoding="utf-8") as f:

        return json.load(f)


DICCIONARIO = cargar_diccionario()


# ------------------------------------------------------------
# Quitar tildes
# ------------------------------------------------------------

def quitar_tildes(texto):

    return "".join(

        c for c in unicodedata.normalize("NFD", texto)

        if unicodedata.category(c) != "Mn"

    )


# ------------------------------------------------------------
# Normalización
# ------------------------------------------------------------

def normalizar(direccion):

    if not direccion:

        return ""

    t = direccion.lower()

    t = quitar_tildes(t)

    t = t.replace(".", " ")
    t = t.replace(",", " ")

    # eliminar símbolos

    for s in DICCIONARIO["eliminar"]:

        t = t.replace(s, " ")

    # abreviaturas

    palabras = []

    for p in t.split():

        palabras.append(

            DICCIONARIO["prefijos"].get(p, p)

        )

    t = " ".join(palabras)

    # calles conocidas

    for origen, destino in DICCIONARIO["calles"].items():

        t = re.sub(

            rf"\b{re.escape(origen)}\b",

            destino,

            t

        )

    # compactar espacios

    t = re.sub(r"\s+", " ", t)

    return t.strip()


# ------------------------------------------------------------
# TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    ejemplos = [

        "Av. Cnel. Díaz 2733",
        "Coronel Diaz, 2733",
        "José E. Uriburu Nº1617",
        "Av Cabildo 2450"

    ]

    print("=" * 60)
    print("ADDRESS NORMALIZER")
    print("=" * 60)

    for e in ejemplos:

        print(f"{e} -> {normalizar(e)}")