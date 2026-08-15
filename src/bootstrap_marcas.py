from pathlib import Path
import unicodedata
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "estudios_features.csv"

MASTER_DIR = ROOT / "data" / "master"
MASTER_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = MASTER_DIR / "marcas_maestra.csv"


def normalizar(texto):

    texto = unicodedata.normalize(
        "NFKD",
        str(texto)
    )

    texto = texto.encode(
        "ascii",
        "ignore"
    ).decode("utf-8")

    return " ".join(
        texto.lower().strip().split()
    )
def auditar_multisedes(estudios):

    cadenas = (
        estudios.groupby("nombre_del_estudio")
        .size()
        .reset_index(name="sedes")
        .sort_values("sedes", ascending=False)
    )

    multisede = cadenas[cadenas["sedes"] > 1]

    print("\n" + "=" * 50)
    print("AUDITORÍA INICIAL DE MULTISEDES")
    print("=" * 50)
    print(f"Cadenas detectadas automáticamente: {len(multisede)}")
    print(f"Sedes pertenecientes a cadenas: {int(multisede['sedes'].sum())}")

    print("\nTOP 15 CADENAS\n")
    print(multisede.head(15).to_string(index=False))

    return multisede


def main():

    estudios = pd.read_csv(
        INPUT,
        encoding="utf-8-sig"
    )

    nombres = (
        estudios["nombre_del_estudio"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    tabla = pd.DataFrame({

        "id_marca": range(
            1,
            len(nombres) + 1
        ),

        "marca_canonica": nombres,

        "alias": nombres,

        "instagram": "",

        "sitio_web": "",

        "estado": "activa"

    })

    tabla.to_csv(
        OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    print("=" * 50)
    auditar_multisedes(estudios)
    print("BASE MAESTRA GENERADA")
    print("=" * 50)
    print(f"Marcas creadas: {len(tabla)}")
    print(OUTPUT)


if __name__ == "__main__":
    main()