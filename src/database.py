# =====================================
# OBSERVATORIO PILATES TRANSVERSO
# MOTOR 4 — SQLITE / BASE DE DATOS
# =====================================

"""
Motor 4 — SQLite / Base de datos

Construye una base SQLite reproducible a partir de:

    data/processed/estudios_features.csv
    data/processed/estudios_marcas.csv

Salida:

    data/database/observatorio_pilates.db

Principios
----------
- estudios_features.csv es el dataset canónico.
- id_estudio proviene de features.py.
- Este módulo NO genera ni modifica id_estudio.
- No modifica los CSV de entrada.
- La base se reconstruye desde cero en cada ejecución.
- Las relaciones estudio-marca utilizan claves explícitas.
- Se activa integridad referencial mediante claves foráneas.
- El módulo expone una API estable para load_database.py.
"""

from pathlib import Path
import sqlite3

import pandas as pd


# =====================================
# RUTAS
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURES_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "estudios_features.csv"
)

MARCAS_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "estudios_marcas.csv"
)

DATABASE_DIR = (
    BASE_DIR
    / "data"
    / "database"
)

DATABASE_PATH = (
    DATABASE_DIR
    / "observatorio_pilates.db"
)


# =====================================
# COLUMNAS
# =====================================

COLUMNAS_ESTUDIOS = [
    "id_estudio",
    "nombre_del_estudio",
    "direccion",
    "barrio",
    "comuna",
    "zona",
    "telefono",
    "email",
    "instagram",
    "seguidores_instagram",
    "puntaje_google",
    "web",
    "fabricantes_ref",
    "diseno",
    "app",
    "resena_destacada",
    "presentacion",
    "servicios_adicionales",
    "horario",
    "codigo_plus",
    "fuente_de_datos",
    "fecha_recoleccion",
    "observaciones",
    "cantidad_resenas",
    "tiene_instagram",
    "tiene_web",
    "tiene_email",
    "tiene_app",
    "presencia_digital",
    "tiene_telefono",
    "n_canales_contacto",
    "n_fabricantes",
    "fabricante_multiple",
]

COLUMNAS_FEATURES = [
    "id_estudio",
    "presencia_digital",
    "n_canales_contacto",
    "n_fabricantes",
    "fabricante_multiple",
]

COLUMNAS_MARCAS = [
    "id_marca",
    "nombre_marca",
    "observaciones",
]

COLUMNAS_RELACION = [
    "id_estudio",
    "id_marca",
]


# =====================================
# UTILIDADES
# =====================================

def normalize_null(value):
    """
    Convierte valores faltantes de Pandas en None.
    """

    if pd.isna(value):
        return None

    return value


def to_int_bool(value):
    """
    Convierte valores booleanos a 0/1.
    """

    if pd.isna(value):
        return 0

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, str):
        value = value.strip().lower()

        if value in {
            "true",
            "1",
            "si",
            "sí",
            "yes",
            "verdadero",
        }:
            return 1

        return 0

    try:
        return int(bool(value))
    except Exception:
        return 0


def get_value(row, column, default=None):
    """
    Obtiene una columna de un registro de forma segura.
    """

    if column not in row.index:
        return default

    value = row[column]

    if pd.isna(value):
        return default

    return value


def convertir_nan_a_none(df):
    """
    Convierte NaN / NaT / pd.NA a None
    para poder almacenarlos como NULL en SQLite.
    """

    result = df.copy()

    result = result.astype(object)

    return result.where(
        pd.notna(result),
        None,
    )


# =====================================
# CONEXIÓN SQLITE
# =====================================

def get_connection():
    """
    Devuelve una conexión SQLite.

    Esta es la función pública principal utilizada
    por load_database.py.
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.execute(
        "PRAGMA foreign_keys = ON;"
    )

    return connection


# =====================================
# INICIALIZACIÓN
# =====================================

def initialize_database():
    """
    Elimina la base anterior, crea una nueva
    y construye el esquema completo.

    La reconstrucción desde cero hace que
    Motor 4 sea reproducible.
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    connection = get_connection()

    try:
        create_schema(connection)
        connection.commit()

    except Exception:
        connection.rollback()
        connection.close()
        raise

    return connection


# =====================================
# ESQUEMA
# =====================================

def create_schema(connection):
    """
    Crea todas las tablas e índices del Observatorio.
    """

    cursor = connection.cursor()

    # ---------------------------------
    # ESTUDIOS
    # ---------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS estudios (

            id_estudio TEXT PRIMARY KEY,

            nombre_del_estudio TEXT NOT NULL,

            direccion TEXT,

            barrio TEXT,

            comuna INTEGER,

            zona TEXT,

            telefono TEXT,

            email TEXT,

            instagram TEXT,

            seguidores_instagram REAL,

            puntaje_google REAL,

            web TEXT,

            fabricantes_ref TEXT,

            diseno TEXT,

            app TEXT,

            resena_destacada TEXT,

            presentacion TEXT,

            servicios_adicionales TEXT,

            horario TEXT,

            codigo_plus TEXT,

            fuente_de_datos TEXT,

            fecha_recoleccion TEXT,

            observaciones TEXT,

            cantidad_resenas REAL,

            tiene_instagram INTEGER NOT NULL DEFAULT 0,

            tiene_web INTEGER NOT NULL DEFAULT 0,

            tiene_email INTEGER NOT NULL DEFAULT 0,

            tiene_app INTEGER NOT NULL DEFAULT 0,

            presencia_digital INTEGER NOT NULL DEFAULT 0,

            tiene_telefono INTEGER NOT NULL DEFAULT 0,

            n_canales_contacto INTEGER NOT NULL DEFAULT 0,

            n_fabricantes INTEGER NOT NULL DEFAULT 0,

            fabricante_multiple INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    # ---------------------------------
    # MARCAS
    # ---------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS marcas (

            id_marca TEXT PRIMARY KEY,

            nombre_marca TEXT NOT NULL,

            observaciones TEXT
        );
        """
    )

    # ---------------------------------
    # RELACIÓN ESTUDIO - MARCA
    # ---------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS estudio_marca (

            id_estudio TEXT NOT NULL,

            id_marca TEXT NOT NULL,

            PRIMARY KEY (
                id_estudio,
                id_marca
            ),

            FOREIGN KEY (
                id_estudio
            )
            REFERENCES estudios (
                id_estudio
            )
            ON DELETE CASCADE,

            FOREIGN KEY (
                id_marca
            )
            REFERENCES marcas (
                id_marca
            )
            ON DELETE CASCADE
        );
        """
    )

    # ---------------------------------
    # ÍNDICES
    # ---------------------------------

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudios_barrio
        ON estudios(barrio);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudios_comuna
        ON estudios(comuna);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudios_zona
        ON estudios(zona);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudios_presencia_digital
        ON estudios(presencia_digital);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudios_puntaje
        ON estudios(puntaje_google);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudios_resenas
        ON estudios(cantidad_resenas);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudios_seguidores
        ON estudios(seguidores_instagram);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudio_marca_estudio
        ON estudio_marca(id_estudio);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_estudio_marca_marca
        ON estudio_marca(id_marca);
        """
    )


# =====================================
# VALIDACIÓN DE FEATURES
# =====================================

def validate_features(df):
    """
    Valida que estudios_features.csv tenga
    la estructura mínima necesaria.
    """

    missing = [
        column
        for column in COLUMNAS_FEATURES
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Faltan columnas obligatorias en "
            "estudios_features.csv:\n"
            + "\n".join(
                f"   - {column}"
                for column in missing
            )
        )

    if df.empty:
        raise ValueError(
            "estudios_features.csv está vacío."
        )

    if df["id_estudio"].isna().any():
        raise ValueError(
            "Existen registros sin id_estudio."
        )

    if (
        df["id_estudio"]
        .astype(str)
        .str.strip()
        .eq("")
        .any()
    ):
        raise ValueError(
            "Existen registros con id_estudio vacío."
        )

    if df["id_estudio"].duplicated().any():

        duplicated = (
            df.loc[
                df["id_estudio"].duplicated(
                    keep=False
                ),
                "id_estudio",
            ]
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            "Existen id_estudio duplicados:\n"
            + "\n".join(
                duplicated
            )
        )

    if df["nombre_del_estudio"].isna().any():
        raise ValueError(
            "Existen registros sin "
            "nombre_del_estudio."
        )

    print(
        f"   Registros validados: {len(df)}"
    )

    print(
        "   id_estudio: OK"
    )

    print(
        "   IDs únicos: OK"
    )


# =====================================
# CARGA DE ESTUDIOS
# =====================================

def load_estudios(connection, df):
    """
    Carga los estudios desde estudios_features.csv.

    IMPORTANTE:
    id_estudio proviene directamente de features.py.
    No se genera ningún ID nuevo.
    """

    missing = [
        column
        for column in COLUMNAS_ESTUDIOS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Faltan columnas para cargar "
            "la tabla estudios:\n"
            + "\n".join(
                f"   - {column}"
                for column in missing
            )
        )

    data = df[
        COLUMNAS_ESTUDIOS
    ].copy()

    data = convertir_nan_a_none(
        data
    )

    placeholders = ", ".join(
        ["?"] * len(COLUMNAS_ESTUDIOS)
    )

    columns_sql = ", ".join(
        COLUMNAS_ESTUDIOS
    )

    sql = f"""
        INSERT INTO estudios (
            {columns_sql}
        )
        VALUES (
            {placeholders}
        );
    """

    rows = list(
        data.itertuples(
            index=False,
            name=None,
        )
    )

    connection.executemany(
        sql,
        rows,
    )

    return len(rows)


# =====================================
# CARGA DE MARCAS
# =====================================

def load_marcas(connection, marcas):
    """
    Carga el maestro de marcas.
    """

    if marcas.empty:
        return 0

    missing = [
        column
        for column in COLUMNAS_MARCAS
        if column not in marcas.columns
    ]

    if missing:
        raise ValueError(
            "Faltan columnas en el maestro "
            "de marcas:\n"
            + "\n".join(
                f"   - {column}"
                for column in missing
            )
        )

    data = marcas[
        COLUMNAS_MARCAS
    ].copy()

    data = convertir_nan_a_none(
        data
    )

    sql = """
        INSERT INTO marcas (
            id_marca,
            nombre_marca,
            observaciones
        )
        VALUES (?, ?, ?);
    """

    rows = list(
        data.itertuples(
            index=False,
            name=None,
        )
    )

    connection.executemany(
        sql,
        rows,
    )

    return len(rows)


# =====================================
# CARGA RELACIÓN ESTUDIO-MARCA
# =====================================

def load_estudio_marca(
    connection,
    relacion,
):
    """
    Carga las relaciones entre estudios y marcas.
    """

    if relacion.empty:
        return 0

    missing = [
        column
        for column in COLUMNAS_RELACION
        if column not in relacion.columns
    ]

    if missing:
        raise ValueError(
            "Faltan columnas en la relación "
            "estudio-marca:\n"
            + "\n".join(
                f"   - {column}"
                for column in missing
            )
        )

    data = relacion[
        COLUMNAS_RELACION
    ].copy()

    data = convertir_nan_a_none(
        data
    )

    # ---------------------------------
    # Validar estudios existentes
    # ---------------------------------

    ids_estudios = {
        row[0]
        for row in connection.execute(
            """
            SELECT id_estudio
            FROM estudios;
            """
        ).fetchall()
    }

    ids_relacion = set(
        data["id_estudio"]
        .dropna()
    )

    missing_estudios = (
        ids_relacion - ids_estudios
    )

    if missing_estudios:
        raise ValueError(
            "Existen relaciones con "
            "id_estudio inexistente:\n"
            + "\n".join(
                sorted(
                    map(
                        str,
                        missing_estudios,
                    )
                )
            )
        )

    # ---------------------------------
    # Validar marcas existentes
    # ---------------------------------

    ids_marcas = {
        row[0]
        for row in connection.execute(
            """
            SELECT id_marca
            FROM marcas;
            """
        ).fetchall()
    }

    ids_relacion_marcas = set(
        data["id_marca"]
        .dropna()
    )

    missing_marcas = (
        ids_relacion_marcas - ids_marcas
    )

    if missing_marcas:
        raise ValueError(
            "Existen relaciones con "
            "id_marca inexistente:\n"
            + "\n".join(
                sorted(
                    map(
                        str,
                        missing_marcas,
                    )
                )
            )
        )

    # ---------------------------------
    # Cargar
    # ---------------------------------

    sql = """
        INSERT INTO estudio_marca (
            id_estudio,
            id_marca
        )
        VALUES (?, ?);
    """

    rows = list(
        data.itertuples(
            index=False,
            name=None,
        )
    )

    connection.executemany(
        sql,
        rows,
    )

    return len(rows)


# =====================================
# CARGA DEL ARCHIVO DE MARCAS
# =====================================

def load_marcas_file(connection):
    """
    Carga automáticamente las marcas y la relación estudio-marca.

    Fuente oficial:
        data/processed/estudios_marcas.csv

    El maestro de marcas se reconstruye uniendo
    id_estudio con estudios_features.csv.
    """

    if not MARCAS_PATH.exists():
        return 0, 0

    df = pd.read_csv(
        MARCAS_PATH,
        encoding="utf-8-sig",
        dtype=str,
    )

    if df.empty:
        return 0, 0

    # -----------------------------
    # Validar relación
    # -----------------------------

    required_relation = [
        "id_estudio",
        "id_marca",
    ]

    missing = [
        c
        for c in required_relation
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            "Faltan columnas obligatorias en estudios_marcas.csv:\n"
            + "\n".join(f"   - {c}" for c in missing)
        )

    relacion = (
        df[required_relation]
        .drop_duplicates()
        .copy()
    )

    # -----------------------------
    # Reconstruir maestro de marcas
    # -----------------------------

    features = pd.read_csv(
        FEATURES_PATH,
        encoding="utf-8-sig",
        dtype=str,
    )

    marcas = (
        relacion
        .merge(
            features[
                [
                    "id_estudio",
                    "nombre_del_estudio",
                ]
            ],
            on="id_estudio",
            how="left",
        )
        .groupby("id_marca", as_index=False)
        .first()
    )

    marcas = marcas.rename(
        columns={
            "nombre_del_estudio": "nombre_marca",
        }
    )

    marcas["observaciones"] = ""

    marcas = marcas[
        COLUMNAS_MARCAS
    ]

    # -----------------------------
    # Limpiar tablas antes de cargar
    # -----------------------------

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM estudio_marca;"
    )

    cursor.execute(
        "DELETE FROM marcas;"
    )

    connection.commit()

    # -----------------------------
    # Cargar
    # -----------------------------

    marcas_count = load_marcas(
        connection,
        marcas,
    )

    relation_count = load_estudio_marca(
        connection,
        relacion,
    )

    connection.commit()

    return (
        marcas_count,
        relation_count,
    )

# =====================================
# ESTADO DE LA BASE
# =====================================

def print_database_status(
    connection=None,
):
    """
    Imprime y valida el estado de la base.

    Puede recibir una conexión existente.
    Si no recibe una, abre una nueva.
    """

    own_connection = False

    if connection is None:
        connection = get_connection()
        own_connection = True

    try:

        print()
        print(
            "8. Verificando base..."
        )

        # ---------------------------------
        # Conteos
        # ---------------------------------

        estudios = connection.execute(
            """
            SELECT COUNT(*)
            FROM estudios;
            """
        ).fetchone()[0]

        marcas = connection.execute(
            """
            SELECT COUNT(*)
            FROM marcas;
            """
        ).fetchone()[0]

        relaciones = connection.execute(
            """
            SELECT COUNT(*)
            FROM estudio_marca;
            """
        ).fetchone()[0]

        print(
            f"   Estudios: {estudios}"
        )

        print(
            f"   Marcas: {marcas}"
        )

        print(
            f"   Relaciones estudio-marca: "
            f"{relaciones}"
        )

        # ---------------------------------
        # IDs
        # ---------------------------------

        duplicated = connection.execute(
            """
            SELECT
                id_estudio,
                COUNT(*) AS cantidad
            FROM estudios
            GROUP BY id_estudio
            HAVING COUNT(*) > 1;
            """
        ).fetchall()

        if duplicated:
            raise ValueError(
                "Existen id_estudio duplicados "
                "en SQLite."
            )

        print(
            "   IDs únicos: OK"
        )

        # ---------------------------------
        # Foreign keys
        # ---------------------------------

        foreign_errors = connection.execute(
            """
            PRAGMA foreign_key_check;
            """
        ).fetchall()

        if foreign_errors:
            raise ValueError(
                "La base presenta errores "
                "de integridad referencial."
            )

        print(
            "   Integridad referencial: OK"
        )

        # ---------------------------------
        # Integrity check
        # ---------------------------------

        integrity = connection.execute(
            """
            PRAGMA integrity_check;
            """
        ).fetchone()[0]

        if integrity != "ok":
            raise ValueError(
                f"SQLite integrity_check: "
                f"{integrity}"
            )

        print(
            "   SQLite integrity_check: OK"
        )

        # ---------------------------------
        # Tablas
        # ---------------------------------

        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
            """
        ).fetchall()

        print(
            "   Tablas:"
        )

        for table in tables:
            print(
                f"      - {table[0]}"
            )

        return {
            "estudios": estudios,
            "marcas": marcas,
            "relaciones": relaciones,
        }

    finally:

        if own_connection:
            connection.close()


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
        "MOTOR 4 — SQLITE"
    )
    print(
        "=" * 60
    )

    print()
    print(
        "Base:"
    )
    print(
        DATABASE_PATH
    )

    print()
    print(
        "Dataset canónico:"
    )
    print(
        FEATURES_PATH
    )

    # ---------------------------------
    # Validar archivos
    # ---------------------------------

    if not FEATURES_PATH.exists():
        raise FileNotFoundError(
            "No existe estudios_features.csv:\n"
            f"{FEATURES_PATH}"
        )

    # ---------------------------------
    # Leer features
    # ---------------------------------

    print()
    print(
        "Leyendo estudios_features.csv..."
    )

    df = pd.read_csv(
        FEATURES_PATH,
        encoding="utf-8-sig",
    )

    print(
        f"   Registros: {len(df)}"
    )

    # ---------------------------------
    # Validar
    # ---------------------------------

    validate_features(
        df
    )

    # ---------------------------------
    # Inicializar
    # ---------------------------------

    print()
    print(
        "Inicializando SQLite..."
    )

    connection = initialize_database()

    try:

        # ---------------------------------
        # Estudios
        # ---------------------------------

        print()
        print(
            "Cargando estudios..."
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
        # Marcas
        # ---------------------------------

        print()
        print(
            "Cargando marcas..."
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
            f"   Relaciones cargadas: "
            f"{relation_count}"
        )

        # ---------------------------------
        # Commit
        # ---------------------------------

        connection.commit()

        # ---------------------------------
        # Validación final
        # ---------------------------------

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
            "Base creada en:"
        )
        print(
            DATABASE_PATH
        )

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()