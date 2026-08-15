# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.0 — Draft Store
# Archivo: draft_store.py
# ============================================================

from pathlib import Path
from datetime import datetime
import json

from city_config import get_city

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _draft_path(city):

    return get_city(city)["drafts"]


def _next_id(city):

    carpeta = _draft_path(city)

    existentes = sorted(carpeta.glob("DRF-*.json"))

    if not existentes:
        return "DRF-000001"

    ultimo = existentes[-1].stem

    numero = int(ultimo.split("-")[1]) + 1

    return f"DRF-{numero:06d}"

# ------------------------------------------------------------
# API
# ------------------------------------------------------------

def create_draft(city, payload):

    draft_id = _next_id(city)

    registro = {

        "draft_id": draft_id,

        "city": city,

        "estado": "draft",

        "created_at": datetime.now().isoformat(timespec="seconds"),

        "updated_at": datetime.now().isoformat(timespec="seconds"),

        "historial": [

            {

                "fecha": datetime.now().isoformat(timespec="seconds"),

                "evento": "draft_creado"

            }

        ],

        "datos": payload

    }

    archivo = _draft_path(city) / f"{draft_id}.json"

    archivo.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return registro


def load_draft(city, draft_id):

    archivo = _draft_path(city) / f"{draft_id}.json"

    if not archivo.exists():
        raise FileNotFoundError(draft_id)

    return json.loads(
        archivo.read_text(encoding="utf-8")
    )


def save_draft(city, registro):

    registro["updated_at"] = datetime.now().isoformat(timespec="seconds")

    archivo = _draft_path(city) / f"{registro['draft_id']}.json"

    archivo.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def append_history(registro, evento):

    registro["historial"].append({

        "fecha": datetime.now().isoformat(timespec="seconds"),

        "evento": evento

    })

    return registro


def list_drafts(city):

    carpeta = _draft_path(city)

    registros = []

    for archivo in sorted(carpeta.glob("DRF-*.json")):

        data = json.loads(
            archivo.read_text(encoding="utf-8")
        )

        registros.append({

            "draft_id": data["draft_id"],

            "estado": data["estado"],

            "nombre": data["datos"].get("nombre", "(sin nombre)"),

            "updated_at": data["updated_at"]

        })

    return registros

# ------------------------------------------------------------
# CLI de prueba
# ------------------------------------------------------------

if __name__ == "__main__":

    print("="*60)
    print("DRAFT STORE")
    print("="*60)

    ejemplo = {

        "nombre": "Pilates Demo",

        "direccion": "Av. Corrientes 1234",

        "barrio": "Balvanera",

        "instagram": "@pilatesdemo"

    }

    draft = create_draft("caba", ejemplo)

    print("\nDraft creado:\n")

    print(draft["draft_id"])

    print("\nListado actual:\n")

    for d in list_drafts("caba"):

        print(d)