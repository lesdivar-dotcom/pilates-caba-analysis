from pathlib import Path
import pandas as pd
import unicodedata

ROOT = Path(__file__).resolve().parents[1]

ESTUDIOS_PATH = (
    ROOT / "data" / "processed" / "estudios_features.csv"
)

MASTER_PATH = (
    ROOT / "data" / "master" / "marcas_maestra.csv"
)

OUTPUT_PATH = (
    ROOT / "data" / "processed" / "estudios_marcas.csv"
)


def normalizar(texto):

    if pd.isna(texto):
        return ""

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


def cargar_estudios():

    if not ESTUDIOS_PATH.exists():

        raise FileNotFoundError(
            f"No existe:\n{ESTUDIOS_PATH}"
        )

    return pd.read_csv(
        ESTUDIOS_PATH,
        encoding="utf-8-sig"
    )


def cargar_maestra():

    if not MASTER_PATH.exists():

        raise FileNotFoundError(
            f"No existe:\n{MASTER_PATH}"
        )

    return pd.read_csv(
        MASTER_PATH,
        encoding="utf-8-sig"
    )


def resolver_marcas(estudios, maestra):

    estudios = estudios.copy()
    maestra = maestra.copy()

    estudios["nombre_norm"] = (
        estudios["nombre_del_estudio"]
        .apply(normalizar)
    )

    maestra["alias_norm"] = (
        maestra["alias"]
        .apply(normalizar)
    )

    # Evitar alias repetidos que duplican estudios
    maestra = (
        maestra
        .drop_duplicates(subset="alias_norm", keep="first")
    )

    tabla = estudios.merge(
        maestra,
        left_on="nombre_norm",
        right_on="alias_norm",
        how="left"
    )

    tabla["nombre_marca"] = (
        tabla["marca_canonica"]
        .fillna(tabla["nombre_del_estudio"])
    )

    return tabla

def guardar(tabla):

    tabla = tabla.copy()

    # Eliminar cualquier id_marca previo para evitar colisiones
    columnas_id = [c for c in tabla.columns if c.startswith("id_marca")]
    if columnas_id:
        tabla = tabla.drop(columns=columnas_id)

    # Catálogo único de marcas
    marcas = (
        tabla[["nombre_marca"]]
        .drop_duplicates()
        .sort_values("nombre_marca")
        .reset_index(drop=True)
    )

    marcas["id_marca"] = range(1, len(marcas) + 1)

    # Merge
    merged = tabla.merge(
        marcas,
        on="nombre_marca",
        how="left",
        suffixes=("", "_catalogo")
    )

    # Localizar la columna correcta de id_marca
    if "id_marca" in merged.columns:
        columna_id = "id_marca"
    elif "id_marca_catalogo" in merged.columns:
        columna_id = "id_marca_catalogo"
    elif "id_marca_y" in merged.columns:
        columna_id = "id_marca_y"
    elif "id_marca_x" in merged.columns:
        columna_id = "id_marca_x"
    else:
        raise RuntimeError(
            "No se pudo generar id_marca.\n"
            f"Columnas disponibles:\n{merged.columns.tolist()}"
        )

    salida = (
        merged[
            [
                "id_estudio",
                columna_id,
                "nombre_marca"
            ]
        ]
        .rename(columns={columna_id: "id_marca"})
        .drop_duplicates(subset="id_estudio")
        .sort_values("id_estudio")
        .reset_index(drop=True)
    )

    salida.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    return salida
def auditoria(tabla):

    cadenas = (
        tabla.groupby("nombre_marca")
        .size()
        .reset_index(name="sedes")
        .sort_values("sedes", ascending=False)
    )

    multisede = cadenas[cadenas["sedes"] > 1]

    print("=" * 50)
    print("AUDITORÍA DE MARCAS")
    print("=" * 50)
    print(f"Sedes..................... {len(tabla)}")
    print(f"Marcas.................... {tabla['nombre_marca'].nunique()}")
    print(f"Cadenas multisede......... {len(multisede)}")
    print(f"Sedes de cadenas.......... {int(multisede['sedes'].sum())}")

    print("\nTOP 15 CADENAS\n")
    print(
        multisede.head(15).to_string(index=False)
    )


def main():

    estudios = cargar_estudios()
    maestra = cargar_maestra()

    tabla = resolver_marcas(
        estudios,
        maestra
    )

    guardar(tabla)
    
    auditoria(tabla)

    print("\nArchivo generado:")
    print(OUTPUT_PATH)

    print("\nSiguiente paso:")
    print("python src\\load_database.py")


if __name__ == "__main__":
    main()