# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.0 — Intake Manager
# Archivo: intake_manager.py
# ============================================================

import argparse
import json

from draft_store import (
    create_draft,
    list_drafts
)

from validators import (
    validar_draft
)

from alias_detector import (
    detectar_alias,
    top_candidatos
)

from city_config import (
    available_cities
)

# ------------------------------------------------------------
# Alta interactiva
# ------------------------------------------------------------

def wizard_alta(city):

    print("\n" + "="*60)
    print("NUEVO ESTUDIO")
    print("="*60)

    payload = {

        "nombre": input("\nNombre del estudio:\n> ").strip(),

        "direccion": input("\nDirección:\n> ").strip(),

        "barrio": input("\nBarrio:\n> ").strip(),

        "telefono": input("\nTeléfono:\n> ").strip(),

        "email": input("\nEmail:\n> ").strip(),

        "instagram": input("\nInstagram:\n> ").strip(),

        "web": input("\nWeb:\n> ").strip(),

        "fabricantes": input("\nFabricantes:\n> ").strip(),

        "observaciones": input("\nObservaciones:\n> ").strip()

    }

    return payload

# ------------------------------------------------------------
# Mostrar validación
# ------------------------------------------------------------

def mostrar_validacion(resultado):

    print("\n" + "="*60)
    print("VALIDACIÓN")
    print("="*60)

    if resultado["ok"]:

        print("\n✔ Validación general: OK")

    else:

        print("\n✖ Validación general: ERROR")

    if resultado["errores"]:

        print("\nErrores:")

        for e in resultado["errores"]:

            print(" -", e)

    if resultado["advertencias"]:

        print("\nAdvertencias:")

        for a in resultado["advertencias"]:

            print(" -", a)

# ------------------------------------------------------------
# Alias
# ------------------------------------------------------------

def mostrar_alias(nombre):

    print("\n" + "="*60)
    print("DETECTOR DE MARCA")
    print("="*60)

    alias = detectar_alias(nombre)

    if alias["encontrado"]:

        print(
            f"\nPosible marca existente:\n"
            f"{alias['marca']} "
            f"(score {alias['score']})"
        )

    else:

        print("\nNo se encontró coincidencia fuerte.")

    print("\nTop candidatos:")

    for c in top_candidatos(nombre, 5):

        print(
            f" - {c['marca']} "
            f"({c['score']})"
        )

# ------------------------------------------------------------
# Comando ADD
# ------------------------------------------------------------

def cmd_add(city):

    payload = wizard_alta(city)

    resultado = validar_draft(city, payload)

    mostrar_validacion(resultado)

    mostrar_alias(payload["nombre"])

    if not resultado["ok"]:

        print(
            "\nNo puede guardarse "
            "hasta corregir errores."
        )

        return

    guardar = input(
        "\nGuardar draft? (S/N)\n> "
    ).strip().lower()

    if guardar != "s":

        print("\nOperación cancelada.")
        return

    draft = create_draft(

        city,

        resultado["normalizado"]

    )

    print("\n" + "="*60)
    print("DRAFT CREADO")
    print("="*60)

    print(
        f"\nID: {draft['draft_id']}"
    )

# ------------------------------------------------------------
# Comando LIST
# ------------------------------------------------------------

def cmd_list(city):

    drafts = list_drafts(city)

    print("\n" + "="*60)
    print("DRAFTS")
    print("="*60)

    if not drafts:

        print("\nSin registros.")
        return

    for d in drafts:

        print(
            f"{d['draft_id']} | "
            f"{d['estado']} | "
            f"{d['nombre']}"
        )

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(

        "accion",

        choices=["add", "list"]

    )

    parser.add_argument(

        "--city",

        default="caba"

    )

    args = parser.parse_args()

    if args.city not in available_cities():

        raise ValueError(
            f"Ciudad inválida: {args.city}"
        )

    if args.accion == "add":

        cmd_add(args.city)

    elif args.accion == "list":

        cmd_list(args.city)

# ------------------------------------------------------------

if __name__ == "__main__":

    main()