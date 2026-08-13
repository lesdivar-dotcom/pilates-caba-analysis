# =====================================
# OBSERVATORIO PILATES TRANSVERSO
# MOTOR 4 — CARGADOR SQLITE
# =====================================

"""
load_database.py

Orquestador de Motor 4.

Su responsabilidad es ejecutar la construcción
de la base SQLite utilizando la API definida
en database.py.

Dataset canónico:

    data/processed/estudios_features.csv

Dataset auxiliar:

    data/processed/estudios_marcas.csv

Salida:

    data/database/observatorio_pilates.db

IMPORTANTE
----------
No utiliza estudios_limpios.csv.

El id_estudio válido proviene de
estudios_features.csv, generado por features.py.
"""

from pathlib import Path
import sys

import pandas as pd

from database import (
    FEATURES_PATH,
    MARCAS_PATH,
    DATABASE_PATH,
    validate_features,
    initialize_database,
    load_estudios,
    load_marcas_file,
    print_database_status,
)


# =====================================
# CONFIGURACIÓN
# =====================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# =====================================
# VALIDACIÓN DE ARCHIVOS
# =====================================

def validate_input_files():
    """
    Verifica los archivos necesarios.
    """

    print()
    print(
        "1. Validando archivos de entrada..."
    )

    if not FEATURES_PATH.exists():

        raise FileNotFoundError(
            "No existe el dataset de features:\n"
            f"{FEATURES_PATH}"
        )

    print(
        "   OK"
    )

    print(
        f"   Features: "
        f"{FEATURES_PATH}"
    )

    if MARCAS_PATH.exists():

        print(
            f"   Marcas: "
            f"{MARCAS_PATH}"
        )

    else:

        print(
            "   Aviso: no existe "
            "estudios_marcas.csv."
        )

        print(
            "   La carga de marcas "
            "será omitida."
        )


# =====================================
# CARGA DATASET
# =====================================

def load_features_dataset():
    """
    Lee estudios_features.csv.
    """

    df = pd.read_csv(
        FEATURES_PATH,
        encoding="utf-8-sig",
    )

    return df


# =====================================
# MAIN
# =====================================

def main():

    print()
    print(
        "=" * 60
    )
    print(
        "OBSERVATORIO PILATES TRANSVERSO"
    )
    print(
        "MOTOR 4 — SQLITE / BASE DE DATOS"
    )
    print(
        "=" * 60
    )

    try:

        # ---------------------------------
        # 1. Archivos
        # ---------------------------------

        validate_input_files()

        # ---------------------------------
        # 2. Dataset
        # ---------------------------------

        print()
        print(
            "2. Leyendo datasets..."
        )

        df = load_features_dataset()

        print(
            f"   Features: "
            f"{len(df)}"
        )

        # ---------------------------------
        # 3. Validación
        # ---------------------------------

        print()
        print(
            "3. Validando estructura..."
        )

        validate_features(
            df
        )

        print(
            "   OK"
        )

        # ---------------------------------
        # 4. SQLite
        # ---------------------------------

        print()
        print(
            "4. Inicializando SQLite..."
        )

        connection = initialize_database()

        try:

            print(
                f"   Base: "
                f"{DATABASE_PATH}"
            )

            # ---------------------------------
            # 5. Estudios
            # ---------------------------------

            print()
            print(
                "5. Cargando estudios..."
            )

            estudios_count = load_estudios(
                connection,
                df,
            )

            print(
                f"   Estudios cargados: "
                f"{estudios_count}"
            )

            # ---------------------------------
            # 6. Marcas
            # ---------------------------------

            print()
            print(
                "6. Cargando marcas..."
            )

            marcas_count, relation_count = (
                load_marcas_file(
                    connection
                )
            )

            print(
                f"   Marcas cargadas: "
                f"{marcas_count}"
            )

            print(
                f"   Relaciones "
                f"estudio-marca: "
                f"{relation_count}"
            )

            # ---------------------------------
            # 7. Commit
            # ---------------------------------

            connection.commit()

            # ---------------------------------
            # 8. Validación final
            # ---------------------------------

            print()
            print(
                "7. Validando base..."
            )

            print_database_status(
                connection
            )

            print()
            print(
                "=" * 60
            )
            print(
                "MOTOR 4 COMPLETADO CORRECTAMENTE"
            )
            print(
                "=" * 60
            )

            print()
            print(
                "Base SQLite:"
            )

            print(
                DATABASE_PATH
            )

        except Exception:

            connection.rollback()

            raise

        finally:

            connection.close()

    except Exception as error:

        print()
        print(
            "=" * 60
        )
        print(
            "ERROR EN MOTOR 4"
        )
        print(
            "=" * 60
        )

        print()
        print(
            error
        )

        print()

        sys.exit(1)


if __name__ == "__main__":
    main()