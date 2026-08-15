# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.0 — Configuración Multi-Ciudad
# Archivo: city_config.py
# ============================================================

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"

CITY = {

    "caba":{

        "nombre":"Ciudad Autónoma de Buenos Aires",

        "unidad":"barrio",

        "geojson": DATA / "reference" / "caba" / "barrios.geojson",

        "drafts": DATA / "drafts" / "caba",

        "processed": DATA / "processed",

        "database": DATA / "database" / "observatorio_pilates.db"

    },

    "cordoba":{

        "nombre":"Córdoba",

        "unidad":"barrio",

        "geojson": DATA / "reference" / "cordoba" / "barrios.geojson",

        "drafts": DATA / "drafts" / "cordoba",

        "processed": DATA / "processed",

        "database": DATA / "database" / "observatorio_pilates.db"

    },

    "rosario":{

        "nombre":"Rosario",

        "unidad":"barrio",

        "geojson": DATA / "reference" / "rosario" / "barrios.geojson",

        "drafts": DATA / "drafts" / "rosario",

        "processed": DATA / "processed",

        "database": DATA / "database" / "observatorio_pilates.db"

    },

    "mar_del_plata":{

        "nombre":"Mar del Plata",

        "unidad":"barrio",

        "geojson": DATA / "reference" / "mar_del_plata" / "barrios.geojson",

        "drafts": DATA / "drafts" / "mar_del_plata",

        "processed": DATA / "processed",

        "database": DATA / "database" / "observatorio_pilates.db"

    },

    "la_plata":{

        "nombre":"La Plata",

        "unidad":"barrio",

        "geojson": DATA / "reference" / "la_plata" / "barrios.geojson",

        "drafts": DATA / "drafts" / "la_plata",

        "processed": DATA / "processed",

        "database": DATA / "database" / "observatorio_pilates.db"

    },

    "montevideo":{

        "nombre":"Montevideo",

        "unidad":"barrio",

        "geojson": DATA / "reference" / "montevideo" / "barrios.geojson",

        "drafts": DATA / "drafts" / "montevideo",

        "processed": DATA / "processed",

        "database": DATA / "database" / "observatorio_pilates.db"

    },

    "madrid":{

        "nombre":"Madrid",

        "unidad":"barrio",

        "geojson": DATA / "reference" / "madrid" / "barrios.geojson",

        "drafts": DATA / "drafts" / "madrid",

        "processed": DATA / "processed",

        "database": DATA / "database" / "observatorio_pilates.db"

    }

}

# ------------------------------------------------------------
# API
# ------------------------------------------------------------

def get_city(slug: str):

    slug = slug.lower()

    if slug not in CITY:

        disponibles = ", ".join(CITY.keys())

        raise ValueError(
            f"Ciudad '{slug}' no configurada. Disponibles: {disponibles}"
        )

    cfg = CITY[slug]

    cfg["drafts"].mkdir(parents=True, exist_ok=True)

    return cfg


def available_cities():

    return sorted(CITY.keys())


# ------------------------------------------------------------
# Test rápido
# ------------------------------------------------------------

if __name__ == "__main__":

    print("="*60)
    print("CONFIGURACIÓN MULTI-CIUDAD")
    print("="*60)

    for ciudad in available_cities():

        cfg = get_city(ciudad)

        print(f"\n{ciudad.upper()}")
        print(f"Nombre: {cfg['nombre']}")
        print(f"Unidad: {cfg['unidad']}")
        print(f"GeoJSON: {cfg['geojson']}")
        print(f"Drafts: {cfg['drafts']}")