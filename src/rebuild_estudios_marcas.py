#rebuild_estudios_marcas.py
# =====================================
# OBSERVATORIO PILATES
# REBUILD ESTUDIOS-MARCAS
# =====================================

"""
Reconstruye el archivo maestro estudios_marcas.csv.

Principios:
- 399 estudios = 399 relaciones estudio→marca.
- Se respetan las relaciones verificadas manualmente.
- No se agrupan nombres automáticamente.
- Todo estudio sin agrupación verificada recibe una marca individual.
"""

from pathlib import Path
import pandas as pd
import sys

# =====================================
# CONFIGURACIÓN
# =====================================

ROOT = Path(__file__).resolve().parents[1]

FEATURES_PATH = ROOT / "data" / "processed" / "estudios_features.csv"

VERIFICADO_PATH = (
    ROOT
    / "data"
    / "processed"
    / "estudios_marcas_verificado.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "estudios_marcas.csv"
)

# =====================================
# UTILIDADES
# =====================================

def cargar_csv(path):

    if not path.exists():
        raise FileNotFoundError(f"No existe:\n{path}")

    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )


def validar_columnas(df, columnas, nombre):

    faltantes = [
        c
        for c in columnas
        if c not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"{nombre}: faltan columnas {faltantes}"
        )

# =====================================
# RELACIONES VERIFICADAS
# =====================================

def cargar_relaciones_verificadas():
    """
    Carga únicamente las relaciones verificadas manualmente.

    Formato esperado:

        id_estudio,id_marca
    """

    df = cargar_csv(VERIFICADO_PATH)

    validar_columnas(
        df,
        ["id_estudio", "id_marca"],
        "estudios_marcas_verificado.csv"
    )

    df = df[
        ["id_estudio", "id_marca"]
    ].copy()

    df["id_estudio"] = (
        df["id_estudio"]
        .astype(str)
        .str.strip()
    )

    df["id_marca"] = (
        df["id_marca"]
        .astype(str)
        .str.strip()
    )

    duplicados = df[
        df["id_estudio"]
        .duplicated(keep=False)
    ]

    if not duplicados.empty:

        conflictos = (
            duplicados
            .groupby("id_estudio")["id_marca"]
            .nunique()
        )

        conflictos = conflictos[
            conflictos > 1
        ]

        if not conflictos.empty:

            print("\nERROR: estudios asociados a más de una marca:")

            for id_estudio in conflictos.index:

                marcas = sorted(
                    duplicados.loc[
                        duplicados["id_estudio"] == id_estudio,
                        "id_marca"
                    ].unique().tolist()
                )

                print(f"   {id_estudio}: {marcas}")

            raise ValueError(
                "Conflicto estudio-marca."
            )

        df = df.drop_duplicates()

    return df

# =====================================
# CONSTRUCCIÓN
# =====================================

def construir_estudios_marcas():

    print("=" * 70)
    print("RECONSTRUCCIÓN DE estudios_marcas.csv")
    print("=" * 70)

    # ---------------------------------

    print("\n1. Leyendo dataset de estudios...")

    features = cargar_csv(FEATURES_PATH)

    validar_columnas(
        features,
        [
            "id_estudio",
            "nombre_del_estudio"
        ],
        "estudios_features.csv"
    )

    print(f"   Estudios encontrados: {len(features)}")

    # ---------------------------------

    print("\n2. Validando estudios...")

    if features["id_estudio"].duplicated().any():
        raise ValueError("Hay id_estudio duplicados.")

    print("   IDs únicos: OK")

    # ---------------------------------

    print("\n3. Cargando relaciones verificadas...")

    verificadas = cargar_relaciones_verificadas()

    print(f"   Relaciones verificadas: {len(verificadas)}")
    print(f"   Marcas verificadas: {verificadas['id_marca'].nunique()}")

    ids_features = set(features["id_estudio"])
    ids_verificados = set(verificadas["id_estudio"])

    huerfanos = ids_verificados - ids_features

    if huerfanos:
        raise ValueError(
            f"Relaciones huérfanas: {sorted(huerfanos)}"
        )

    print("   Estudios verificados existentes: OK")

    # ---------------------------------

    nombres_estudio = dict(
        zip(
            features["id_estudio"],
            features["nombre_del_estudio"]
        )
    )

    # ---------------------------------

    numeros = []

    for valor in verificadas["id_marca"]:

        if str(valor).startswith("M-"):

            try:
                numeros.append(int(str(valor)[2:]))

            except ValueError:
                pass

    siguiente = max(numeros) + 1 if numeros else 1

    # ---------------------------------

    print("\n4. Construyendo relaciones...")

    filas = []

    for _, row in features.iterrows():

        id_estudio = str(row["id_estudio"]).strip()
        nombre = str(row["nombre_del_estudio"]).strip()

        relacion = verificadas[
            verificadas["id_estudio"] == id_estudio
        ]

        if not relacion.empty:

            filas.append({
                "id_estudio": id_estudio,
                "id_marca": relacion.iloc[0]["id_marca"],
                "nombre_marca": None,
                "observaciones": "Relación verificada manualmente."
            })

        else:

            id_marca = f"M-{siguiente:04d}"
            siguiente += 1

            filas.append({
                "id_estudio": id_estudio,
                "id_marca": id_marca,
                "nombre_marca": nombre,
                "observaciones": "Marca individual."
            })

    resultado = pd.DataFrame(filas)

    # ---------------------------------

    print("\n5. Asignando nombres de marca...")

    nombres_marca = {}

    for id_marca, grupo in resultado.groupby("id_marca"):

        primer_estudio = grupo.iloc[0]["id_estudio"]

        nombres_marca[id_marca] = nombres_estudio[primer_estudio]

    resultado["nombre_marca"] = (
        resultado["id_marca"]
        .map(nombres_marca)
    )

    resultado = resultado[
        [
            "id_estudio",
            "id_marca",
            "nombre_marca",
            "observaciones"
        ]
    ]

    resultado = resultado.sort_values(
        "id_estudio"
    ).reset_index(drop=True)

    # ---------------------------------

    print("\n6. Validando resultado...")

    if len(resultado) != len(features):
        raise ValueError("Cantidad incorrecta de relaciones.")

    print(f"   Relaciones: {len(resultado)} OK")

    if resultado["id_estudio"].duplicated().any():
        raise ValueError("Hay estudios duplicados.")

    print("   Estudios únicos: OK")

    ids_resultado = set(resultado["id_estudio"])

    faltantes = ids_features - ids_resultado

    if faltantes:
        raise ValueError(f"Faltan estudios: {sorted(faltantes)}")

    print("   Cobertura completa: OK")

    # ---------------------------------

    print("\n7. Resumen de marcas...")

    tamanos = resultado.groupby("id_marca").size()

    total_estudios = len(resultado)
    total_marcas = resultado["id_marca"].nunique()

    multisede = tamanos[tamanos > 1]
    individuales = tamanos[tamanos == 1]

    print(f"   Estudios: {total_estudios}")
    print(f"   Marcas: {total_marcas}")
    print(f"   Marcas multisede: {len(multisede)}")
    print(f"   Marcas individuales: {len(individuales)}")
    print(f"   Estudios en marcas multisede: {multisede.sum()}")

    # ---------------------------------

    print("\n8. Marcas multisede:")

    if multisede.empty:

        print("   Ninguna.")

    else:

        ranking = (
            resultado
            .groupby(
                ["id_marca", "nombre_marca"]
            )
            .agg(
                sedes=("id_estudio", "count")
            )
            .reset_index()
        )

        ranking = ranking[
            ranking["sedes"] > 1
        ].sort_values(
            "sedes",
            ascending=False
        )

        print(ranking.to_string(index=False))

    # ---------------------------------

    print("\n9. Guardando resultado...")

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    resultado.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nArchivo generado:\n{OUTPUT_PATH}")

    print("\nRECONSTRUCCIÓN COMPLETADA OK")
    print("=" * 70)

    return resultado

# =====================================
# MAIN
# =====================================

def main():

    try:

        construir_estudios_marcas()

    except Exception as e:

        print("\nERROR:")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()