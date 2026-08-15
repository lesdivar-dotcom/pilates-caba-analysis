from pathlib import Path
import unicodedata
import pandas as pd
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]

MASTER = ROOT / "data" / "master" / "marcas_maestra.csv"


def limpiar(texto):

    texto = str(texto)

    # Corrige errores comunes de codificación
    try:
        texto = texto.encode("latin1").decode("utf-8")
    except Exception:
        pass

    texto = " ".join(texto.split())

    return texto


def normalizar(texto):

    texto = limpiar(texto)

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")

    return texto.lower()


def similares(lista):

    pares = []

    for i in range(len(lista)):

        for j in range(i + 1, len(lista)):

            s = SequenceMatcher(
                None,
                normalizar(lista[i]),
                normalizar(lista[j])
            ).ratio()

            if s >= 0.90 and lista[i] != lista[j]:

                pares.append((lista[i], lista[j], round(s, 2)))

    return pares
def aplicar_decisiones_editoriales(df):

    reemplazos = {

        "Almha Pilates": "Alma Pilates",

        "Armonía'S Pilates": "Armonia Pilates",

        "Art Pilates": "Arte Pilates",

        "Danez Pilates & Funciónal":
            "Danez Pilates & Funcional",

        "Haus, Casa De Pilates®":
            "Haus, Casa De Pilates",

        "Mr Pilates Reformer @Mrpilatesreforme":
            "Mr Pilates Reformer @Mrpilatesreformer",

        "Seruno Pilates Reforme":
            "Seruno • Pilates Reformer",

        "Teseo.Pilates Funcional":
            "Teseo | Pilates Funcional"

    }

    df["marca_canonica"] = (
        df["marca_canonica"]
        .replace(reemplazos)
    )

    df["alias"] = (
        df["alias"]
        .replace(reemplazos)
    )

    return df


def main():

    df = pd.read_csv(
        MASTER,
        encoding="utf-8-sig"
    )

    df["marca_canonica"] = (
        df["marca_canonica"]
        .apply(limpiar)
        .str.title()
    )

    df["alias"] = (
        df["alias"]
        .apply(limpiar)
    )
    df = aplicar_decisiones_editoriales(df)

    df.to_csv(
        MASTER,
        index=False,
        encoding="utf-8-sig"
    )

    posibles = similares(df["marca_canonica"].tolist())

    print("=" * 50)
    print("CONSOLIDACIÓN EDITORIAL")
    print("=" * 50)

    print(f"Marcas: {len(df)}")

    print(f"Posibles alias: {len(posibles)}")

    print("\nPrimeros 20 candidatos\n")

    for a, b, s in posibles[:20]:

        print(f"{a}  ↔  {b} ({s})")


if __name__ == "__main__":
    main()