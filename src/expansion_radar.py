# =====================================
# OBSERVATORIO PILATES TRANSVERSO
# MOTOR 5.5 — RADAR DE EXPANSIÓN
# =====================================

"""
Genera fichas estratégicas por barrio.

Entrada:
    data/intelligence/oportunidad_barrios.csv

Salida:
    data/intelligence/radar_expansion/
        ├── index.md
        ├── Palermo.md
        ├── Flores.md
        └── ...
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT
    / "data"
    / "intelligence"
    / "oportunidad_barrios.csv"
)

OUTPUT = (
    ROOT
    / "data"
    / "intelligence"
    / "radar_expansion"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)


# =====================================
# RECOMENDACIONES
# =====================================

def recomendacion(categoria):

    recomendaciones = {

        "Alta":
            "Barrio prioritario para evaluar apertura de una nueva sede.",

        "Media":
            "Mercado interesante, aunque requiere una propuesta diferenciada.",

        "Maduro":
            "Mercado competitivo; conviene estudiar posicionamiento.",

        "Alta competencia":
            "Entrada compleja; recomendable solo con ventajas claras."

    }

    return recomendaciones.get(
        categoria,
        "Sin recomendación."
    )


# =====================================
# PERFIL COMERCIAL
# =====================================

def perfil(estudios_por_10000):

    if estudios_por_10000 < 1:
        return "Mercado en desarrollo"

    elif estudios_por_10000 < 2:
        return "Mercado equilibrado"

    elif estudios_por_10000 < 3:
        return "Mercado competitivo"

    else:
        return "Mercado altamente competitivo"


# =====================================
# GENERAR FICHA
# =====================================

def generar_ficha(row):

    archivo = OUTPUT / f"{row['barrio']}.md"

    contenido = f"""# Radar de Expansión — {row['barrio']}

## Resumen

| Indicador | Valor |
|-----------|------:|
| Ranking | {row['ranking']} |
| Oportunidad | {row['oportunidad']} |
| Categoría | {row['categoria']} |
| Estudios | {row['estudios']} |
| Población | {int(row['poblacion']):,} |
| Estudios por 10.000 hab. | {row['estudios_por_10000']:.2f} |
| Marcas presentes | {row['marcas']} |

## Perfil comercial

**{perfil(row['estudios_por_10000'])}**

## Lectura estratégica

{row['explicacion']}

## Recomendación del Observatorio

{recomendacion(row['categoria'])}

---

*Generado automáticamente por el Observatorio Pilates Transverso.*
"""

    archivo.write_text(
        contenido,
        encoding="utf-8"
    )


# =====================================
# ÍNDICE
# =====================================

def generar_indice(df):

    archivo = OUTPUT / "index.md"

    lineas = [
        "# Radar de Expansión CABA",
        "",
        "## Ranking completo",
        ""
    ]

    for _, row in df.iterrows():

        lineas.append(
            f"{row['ranking']:>2}. "
            f"[{row['barrio']}]({row['barrio']}.md) "
            f"— {row['oportunidad']} puntos "
            f"({row['categoria']})"
        )

    archivo.write_text(
        "\n".join(lineas),
        encoding="utf-8"
    )


# =====================================
# MAIN
# =====================================

def main():

    print("=" * 70)
    print("MOTOR 5.5 — RADAR DE EXPANSIÓN")
    print("=" * 70)

    if not INPUT.exists():

        raise FileNotFoundError(
            f"No existe:\n{INPUT}"
        )

    df = pd.read_csv(
        INPUT,
        encoding="utf-8-sig"
    )

    print(f"\nBarrios procesados: {len(df)}")

    for _, row in df.iterrows():

        generar_ficha(row)

    generar_indice(df)

    print(
        f"\nFichas generadas en:\n{OUTPUT}"
    )

    print("\nMOTOR 5.5 COMPLETADO")


if __name__ == "__main__":
    main()