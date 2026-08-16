# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.1 — Publish Manager
# Archivo: publish_manager.py
# ============================================================

from pathlib import Path
from datetime import datetime
import argparse
import subprocess
from draft_store import (
    load_draft,
    save_draft,
    append_history,
    list_drafts
)

import pandas as pd

from draft_store import load_draft, save_draft, append_history
from city_config import get_city

ROOT = Path(__file__).resolve().parent.parent

PROCESSED = ROOT / "data" / "processed"

FEATURES_PATH = PROCESSED / "estudios_features.csv"
REPORT_SCRIPT = ROOT / "src" / "report_builder.py"


# ------------------------------------------------------------
# IDs definitivos
# ------------------------------------------------------------

def siguiente_id_estudio():

    if not FEATURES_PATH.exists():
        return "EST-0001"

    df = pd.read_csv(FEATURES_PATH)

    ids = df["id_estudio"].dropna().tolist()

    if not ids:
        return "EST-0001"

    ultimo = max(
        int(i.split("-")[1])
        for i in ids
    )

    return f"EST-{ultimo+1:04d}"


# ------------------------------------------------------------
# Construir fila oficial (esquema Motor 2)
# ------------------------------------------------------------

def construir_fila(draft):

    datos = draft["datos"]

    instagram = datos.get("instagram", "").strip()
    web = datos.get("web", "").strip()
    email = datos.get("email", "").strip()
    telefono = datos.get("telefono", "").strip()

    fabricantes = datos.get("fabricantes", "").strip()

    lista_fabricantes = [
        f.strip()
        for f in fabricantes.split(",")
        if f.strip()
    ]

    fila = {

        # ---------- Identidad ----------
        "id_estudio": siguiente_id_estudio(),
        "nombre_del_estudio": datos.get("nombre", ""),
        "direccion": datos.get("direccion", ""),
        "barrio": datos.get("barrio", ""),

        # ---------- Contacto ----------
        "telefono": telefono,
        "email": email,
        "instagram": instagram,
        "web": web,

        # ---------- Google ----------
        "puntaje_google": None,
        "cantidad_resenas": None,

        # ---------- Instagram ----------
        "seguidores_instagram": None,

        # ---------- Equipamiento ----------
        "fabricantes_ref": fabricantes,

        # ---------- Campos editoriales ----------
        "diseno": "",
        "app": "",
        "resena_destacada": "",
        "presentacion": "",
        "servicios_adicionales": "",
        "horario": "",
        "codigo_plus": "",

        # ---------- Metadatos ----------
        "fuente_de_datos": "Motor7",
        "fecha_recoleccion": datetime.now().strftime("%Y-%m-%d"),
        "observaciones": datos.get("observaciones", ""),

        # ---------- Territorio ----------
        "comuna": "",
        "zona": "",

        # ---------- Features derivadas ----------
        "tiene_instagram": bool(instagram),
        "tiene_web": bool(web),
        "tiene_email": bool(email),
        "tiene_app": False,
        "tiene_telefono": bool(telefono),

        "presencia_digital": (
            int(bool(instagram))
            + int(bool(web))
            + int(bool(email))
        ),

        "n_canales_contacto": (
            int(bool(telefono))
            + int(bool(email))
            + int(bool(web))
            + int(bool(instagram))
        ),

        "n_fabricantes": len(lista_fabricantes),

        "fabricante_multiple": len(lista_fabricantes) > 1

    }

    return fila


# ------------------------------------------------------------
# Insertar en Features
# ------------------------------------------------------------

def insertar_estudio(fila):

    if FEATURES_PATH.exists():

        df = pd.read_csv(FEATURES_PATH)

    else:

        df = pd.DataFrame()

    df = pd.concat(

        [df, pd.DataFrame([fila])],

        ignore_index=True

    )

    df.to_csv(

        FEATURES_PATH,

        index=False,

        encoding="utf-8-sig"

    )

    return fila["id_estudio"]


# ------------------------------------------------------------
# Ejecutar pipeline
# ------------------------------------------------------------

def ejecutar(script):

    ruta = ROOT / "src" / script

    print(f"\n→ Ejecutando {script}")

    subprocess.run(

        ["python", str(ruta)],

        check=True

    )


# ------------------------------------------------------------
# Publicar Draft
# ------------------------------------------------------------
# ------------------------------------------------------------
# Publicación transaccional (DM-013)
# ------------------------------------------------------------

def publicar(city, draft_id):

    draft = load_draft(city, draft_id)

    if draft["estado"] == "published":
        print("\nEste draft ya fue publicado.")
        return

    # Construir fila oficial
    fila = construir_fila(draft)

    # Insertar temporalmente en Features
    est_id = insertar_estudio(fila)

    try:

        # Pipeline oficial
        ejecutar("rebuild_marcas.py")
        ejecutar("load_database.py")
        ejecutar("dashboard_builder.py")
        ejecutar("report_builder.py")

    except Exception as e:

        print("\n❌ Error durante la publicación.")
        print("Revirtiendo cambios...")

        # Rollback del CSV
        df = pd.read_csv(FEATURES_PATH)

        df = df[df["id_estudio"] != est_id]

        df.to_csv(
            FEATURES_PATH,
            index=False,
            encoding="utf-8-sig"
        )

        append_history(
            draft,
            "rollback_publicacion"
        )

        save_draft(city, draft)

        raise e

    # Solo aquí cambia a published
    draft["estado"] = "published"
    draft["id_estudio"] = est_id

    append_history(
        draft,
        "published"
    )

    save_draft(city, draft)

    print("\n" + "="*60)
    print("PUBLICACIÓN COMPLETADA")
    print("="*60)

    print(f"\nDraft............. {draft_id}")
    print(f"Estudio.......... {est_id}")
    print("Estado........... published")

    print("\nProductos actualizados:")
    print("   ✓ Base Maestra")
    print("   ✓ SQLite")
    print("   ✓ Dashboard Editorial")
    print("   ✓ Intelligence Report (PDF)")
# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "accion",
        choices=["approve"]
    )

    parser.add_argument("draft_id")

    parser.add_argument(
        "--city",
        default="caba"
    )

    args = parser.parse_args()

    get_city(args.city)

    if args.accion == "approve":

        try:

            publicar(
                args.city,
                args.draft_id
            )

        except FileNotFoundError:

            print("\n" + "="*60)
            print("PUBLICACIÓN")
            print("="*60)

            print(f"\nNo existe el draft: {args.draft_id}")

            print("\nDrafts disponibles:\n")

            drafts = list_drafts(args.city)

            if not drafts:

                print("   (sin drafts)")

            else:

                for d in drafts:

                    print(
                        f"   {d['draft_id']} | "
                        f"{d['estado']} | "
                        f"{d['nombre']}"
                    )

            return


if __name__ == "__main__":
    main()      