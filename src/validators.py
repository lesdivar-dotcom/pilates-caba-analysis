# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.0 — Validadores Editoriales
# Archivo: validators.py
# ============================================================

from pathlib import Path
import json
import re

import pandas as pd

from city_config import get_city

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# ------------------------------------------------------------
# Normalización
# ------------------------------------------------------------

def normalizar(texto):

    if texto is None:
        return ""

    texto = str(texto).strip().lower()

    reemplazos = {
        "á":"a","é":"e","í":"i","ó":"o","ú":"u","ü":"u","ñ":"n"
    }

    for a,b in reemplazos.items():
        texto = texto.replace(a,b)

    alias = {
        "la boca":"boca",
        "san nicolas":"san nicolas",
        "villa gral mitre":"villa general mitre"
    }

    return alias.get(texto,texto)

# ------------------------------------------------------------
# Barrios válidos
# ------------------------------------------------------------

def cargar_barrios(city):

    geo = get_city(city)["geojson"]

    if not geo.exists():
        return set()

    data = json.loads(geo.read_text(encoding="utf-8"))

    props = data["features"][0]["properties"]

    campo = next(
        (c for c in ["BARRIO","barrio","nombre"] if c in props),
        list(props.keys())[0]
    )

    return {
        normalizar(f["properties"][campo])
        for f in data["features"]
    }

# ------------------------------------------------------------
# Instagram
# ------------------------------------------------------------

def validar_instagram(valor):

    if not valor:
        return True, ""

    valor = valor.strip()

    if valor.startswith("@"):
        valor = valor[1:]

    patron = r"^[A-Za-z0-9._]{1,30}$"

    if re.match(patron, valor):
        return True, "@"+valor

    return False, valor

# ------------------------------------------------------------
# Email
# ------------------------------------------------------------

def validar_email(valor):

    if not valor:
        return True

    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(patron, valor) is not None

# ------------------------------------------------------------
# Teléfono
# ------------------------------------------------------------

def normalizar_telefono(valor):

    if not valor:
        return ""

    digitos = re.sub(r"\D","",str(valor))

    if len(digitos) < 8:
        return ""

    return digitos

# ------------------------------------------------------------
# Duplicados
# ------------------------------------------------------------

def detectar_duplicado(city,nombre,direccion):

    ruta = DATA/"processed"/"estudios_features.csv"

    if not ruta.exists():
        return None

    df = pd.read_csv(ruta)

    nombre_n = normalizar(nombre)
    dir_n = normalizar(direccion)

    for _,fila in df.iterrows():

        n = normalizar(fila["nombre_del_estudio"])
        d = normalizar(fila["direccion"])

        if n == nombre_n and d == dir_n:

            return fila["id_estudio"]

    return None

# ------------------------------------------------------------
# Validador principal
# ------------------------------------------------------------

def validar_draft(city,payload):

    resultado = {

        "ok":True,

        "errores":[],

        "advertencias":[],

        "normalizado":payload.copy()

    }

    # nombre

    if not payload.get("nombre"):

        resultado["ok"]=False
        resultado["errores"].append("Falta nombre.")

    # dirección

    if not payload.get("direccion"):

        resultado["ok"]=False
        resultado["errores"].append("Falta dirección.")

    # barrio

    barrios = cargar_barrios(city)

    barrio = normalizar(payload.get("barrio",""))

    if barrio not in barrios:

        resultado["ok"]=False

        resultado["errores"].append(
            f"Barrio no reconocido: {payload.get('barrio')}"
        )

    # instagram

    ok,insta = validar_instagram(
        payload.get("instagram","")
    )

    resultado["normalizado"]["instagram"]=insta

    if not ok:

        resultado["advertencias"].append(
            "Instagram con formato dudoso."
        )

    # email

    if not validar_email(payload.get("email","")):

        resultado["advertencias"].append(
            "Email inválido."
        )

    # teléfono

    resultado["normalizado"]["telefono"]=normalizar_telefono(
        payload.get("telefono","")
    )

    # duplicado

    dup = detectar_duplicado(

        city,

        payload.get("nombre",""),

        payload.get("direccion","")

    )

    if dup:

        resultado["advertencias"].append(
            f"Posible duplicado de {dup}"
        )

    return resultado

# ------------------------------------------------------------
# Test
# ------------------------------------------------------------

if __name__=="__main__":

    ejemplo = {

        "nombre":"Pilates Demo",

        "direccion":"Av. Corrientes 1234",

        "barrio":"Balvanera",

        "instagram":"pilates.demo",

        "email":"demo@pilates.com",

        "telefono":"11-5555-4444"

    }

    r = validar_draft("caba",ejemplo)

    print("="*60)
    print("VALIDADOR EDITORIAL")
    print("="*60)
    print(r)