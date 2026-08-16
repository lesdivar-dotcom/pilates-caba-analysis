# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.3 — Duplicate Guard
# Archivo: duplicate_guard.py
#
# Detecta sedes duplicadas antes de crear un Draft.
# ============================================================

from pathlib import Path
import pandas as pd
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parent.parent

FEATURES_PATH = ROOT / "data" / "processed" / "estudios_features.csv"


# ============================================================
# NORMALIZACIÓN
# ============================================================

from address_normalizer import normalizar

# ============================================================
# CARGA BASE
# ============================================================

def cargar_base():

    if not FEATURES_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(FEATURES_PATH)

    df["direccion_norm"] = df["direccion"].apply(normalizar)
    df["barrio_norm"] = df["barrio"].apply(normalizar)
    df["nombre_norm"] = df["nombre_del_estudio"].apply(normalizar)

    return df


# ============================================================
# BÚSQUEDA
# ============================================================

def buscar(nombre, direccion, barrio):

    df = cargar_base()

    if df.empty:
        return {
            "duplicado": False,
            "coincidencias": []
        }

    nombre_n = normalizar(nombre)
    direccion_n = normalizar(direccion)
    barrio_n = normalizar(barrio)

    coincidencias = []

    for _, fila in df.iterrows():

        score_dir = fuzz.ratio(
            direccion_n,
            fila["direccion_norm"]
        )

        score_nombre = fuzz.ratio(
            nombre_n,
            fila["nombre_norm"]
        )

        mismo_barrio = barrio_n == fila["barrio_norm"]

        # Caso 1: dirección prácticamente idéntica
        if score_dir >= 97:

            coincidencias.append({

                "tipo": "direccion",
                "id_estudio": fila["id_estudio"],
                "nombre": fila["nombre_del_estudio"],
                "barrio": fila["barrio"],
                "direccion": fila["direccion"],
                "score": score_dir

            })

            continue

        # Caso 2: misma marca + dirección muy parecida
        if score_nombre >= 95 and score_dir >= 90:

            coincidencias.append({

                "tipo": "marca_direccion",
                "id_estudio": fila["id_estudio"],
                "nombre": fila["nombre_del_estudio"],
                "barrio": fila["barrio"],
                "direccion": fila["direccion"],
                "score": score_dir

            })

            continue

        # Caso 3: misma marca y mismo barrio
        if score_nombre >= 95 and mismo_barrio:

            coincidencias.append({

                "tipo": "marca_barrio",
                "id_estudio": fila["id_estudio"],
                "nombre": fila["nombre_del_estudio"],
                "barrio": fila["barrio"],
                "direccion": fila["direccion"],
                "score": score_nombre

            })

    coincidencias.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {

        "duplicado": len(coincidencias) > 0,
        "coincidencias": coincidencias

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("="*60)
    print("DUPLICATE GUARD")
    print("="*60)

    prueba = buscar(

        nombre="Naos Pilates Studio",
        direccion="Coronel Diaz 2733",
        barrio="Palermo"

    )

    print(prueba)