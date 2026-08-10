# =====================================
# OBSERVATORIO PILATES
# FEATURES
# =====================================

"""
OBSERVATORIO PILATES

Módulo: features.py

Este módulo crea variables derivadas a partir de los datos
limpios del relevamiento.

Entrada:
    data/interim/estudios_limpios.csv

Salida:
    data/processed/estudios_features.csv

Principios:

- Nunca modifica datos originales.
- Cada función crea una única variable derivada.
- Todas las variables creadas son reutilizadas por analysis.py.
- Todas las features son reproducibles.
- id_estudio funciona como identificador estable del estudio.
- Las métricas temporales, como seguidores de Instagram,
  valoración de Google y cantidad de reseñas, conservan
  su fecha de recolección.

Variables implementadas:

✔ id_estudio
✔ comuna
✔ zona
✔ presencia_digital
✔ n_canales_contacto
✔ n_fabricantes
✔ fabricante_multiple

Variables temporales conservadas desde los datos:

✔ seguidores_instagram
✔ puntaje_google
✔ cantidad_resenas
✔ fecha_recoleccion

Próximas variables:

□ densidad territorial
□ equipamiento
□ métricas históricas
□ indicadores temporales
"""

import pandas as pd


# =====================================
# CARGA
# =====================================

def cargar_datos():
    """
    Carga los datos limpios.

    También normaliza el nombre de la columna
    de seguidores de Instagram.

    Si el dataset ya contiene id_estudio,
    se conserva.

    Si no contiene id_estudio, se genera
    por única vez para los registros actuales.

    Retorna
    -------
    pandas.DataFrame
    """

    df = pd.read_csv(
        "data/interim/estudios_limpios.csv"
    )

    # =================================
    # INSTAGRAM
    # =================================

    if (
        "seguidores" in df.columns
        and "seguidores_instagram" not in df.columns
    ):
        df = df.rename(
            columns={
                "seguidores": "seguidores_instagram"
            }
        )

    # =================================
    # ID ESTUDIO
    # =================================

    if "id_estudio" not in df.columns:

        df["id_estudio"] = [
            f"EST-{i:04d}"
            for i in range(1, len(df) + 1)
        ]

        print(
            "\nAdvertencia:"
            "\nid_estudio no estaba presente en "
            "estudios_limpios.csv."
            "\nSe generaron identificadores para "
            "los registros actuales."
        )

    return df


# =====================================
# GEOGRAFÍA
# COMUNAS DE CABA
# =====================================

MAPA_COMUNAS = {

    "Agronomía": 15,
    "Almagro": 5,
    "Balvanera": 3,
    "Barracas": 4,
    "Belgrano": 13,
    "Boedo": 5,
    "Caballito": 6,
    "Chacarita": 15,
    "Coghlan": 12,
    "Colegiales": 13,
    "Constitución": 1,
    "Flores": 7,
    "Floresta": 10,
    "La Boca": 4,
    "La Paternal": 15,
    "Liniers": 9,
    "Mataderos": 9,
    "Monte Castro": 10,
    "Monserrat": 1,
    "Nueva Pompeya": 4,
    "Núñez": 13,
    "Palermo": 14,
    "Parque Avellaneda": 9,
    "Parque Chacabuco": 7,
    "Parque Chas": 15,
    "Parque Patricios": 4,
    "Puerto Madero": 1,
    "Recoleta": 2,
    "Retiro": 1,
    "Saavedra": 12,
    "San Cristóbal": 3,
    "San Nicolás": 1,
    "San Telmo": 1,
    "Vélez Sarsfield": 10,
    "Versalles": 10,
    "Villa Crespo": 15,
    "Villa del Parque": 11,
    "Villa Devoto": 11,
    "Villa General Mitre": 11,
    "Villa Lugano": 8,
    "Villa Luro": 10,
    "Villa Ortúzar": 15,
    "Villa Pueyrredón": 12,
    "Villa Real": 10,
    "Villa Riachuelo": 8,
    "Villa Santa Rita": 11,
    "Villa Soldati": 8,
    "Villa Urquiza": 12,

}


# =====================================
# ZONAS TRANSVERSO
# =====================================

MAPA_ZONAS = {

    1: "Centro",
    2: "Norte",
    3: "Centro",
    4: "Sur",
    5: "Centro",
    6: "Oeste",
    7: "Oeste",
    8: "Sur",
    9: "Oeste",
    10: "Oeste",
    11: "Oeste",
    12: "Norte",
    13: "Norte",
    14: "Norte",
    15: "Norte",

}


# =====================================
# MAESTRO DE MARCAS
# =====================================

def crear_maestro_marcas():
    """
    Crea la estructura maestra de marcas.

    Cada marca tendrá un identificador único
    independiente del identificador del estudio.

    Retorna
    -------
    DataFrame
    """

    marcas = pd.DataFrame({

        "id_marca": pd.Series(dtype="string"),

        "nombre_marca": pd.Series(dtype="string"),

        "observaciones": pd.Series(dtype="string"),

    })

    return marcas


# =====================================
# MARCAS CONOCIDAS
# =====================================

MARCAS_CONOCIDAS = {

    "M-0001": "Pilates del Pino",

}


def cargar_marcas_conocidas():
    """
    Crea el maestro inicial de marcas conocidas.

    Las marcas se incorporan manualmente para evitar
    confundir el nombre comercial de una marca con
    el nombre particular de cada estudio o sucursal.

    Retorna
    -------
    DataFrame
    """

    marcas = pd.DataFrame(
        [
            {
                "id_marca": id_marca,
                "nombre_marca": nombre_marca,
                "observaciones": ""
            }
            for id_marca, nombre_marca
            in MARCAS_CONOCIDAS.items()
        ]
    )

    return marcas


# =====================================
# RELACIÓN ESTUDIO - MARCA
# =====================================

def crear_relacion_estudio_marca():

    relacion = pd.DataFrame({

        "id_estudio": [
            "EST-0077",
            "EST-0112",
        ],

        "id_marca": [
            "M-0001",
            "M-0001",
        ],

    })

    return relacion


# =====================================
# GUARDAR RELACIÓN ESTUDIO - MARCA
# =====================================

def guardar_relacion_estudio_marca(relacion):

    ruta = "data/processed/estudios_marcas.csv"

    relacion.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\nRelación estudio-marca guardada en:\n{ruta}"
    )


# =====================================
# COMUNA
# =====================================

def crear_comuna(df):
    """
    Variable:
        comuna

    Tipo:
        Entero (1–15)

    Origen:
        Barrio normalizado.

    Interpretación:
        Identificador oficial de la comuna de CABA.
    """

    df["comuna"] = (
        df["barrio"]
        .map(MAPA_COMUNAS)
    )

    return df


# =====================================
# ZONA
# =====================================

def crear_zona(df):
    """
    Variable:
        zona

    Tipo:
        Texto

    Origen:
        Comuna.

    Interpretación:
        Agrupación territorial utilizada por
        el Observatorio Transverso.
    """

    df["zona"] = (
        df["comuna"]
        .map(MAPA_ZONAS)
    )

    return df


# =====================================
# PRESENCIA DIGITAL
# =====================================

def crear_presencia_digital(df):
    """
    Variable:
        presencia_digital

    Tipo:
        Entero (0-4)

    Componentes:
        - Instagram
        - Web
        - Email
        - App

    Interpretación:
        Cantidad de canales digitales disponibles
        para cada estudio.
    """

    df["tiene_instagram"] = (
        df["instagram"].notna()
    )

    df["tiene_web"] = (
        df["web"].notna()
    )

    df["tiene_email"] = (
        df["email"].notna()
    )

    df["tiene_app"] = (
        df["app"].notna()
    )

    df["presencia_digital"] = (

        df["tiene_instagram"].astype(int)

        + df["tiene_web"].astype(int)

        + df["tiene_email"].astype(int)

        + df["tiene_app"].astype(int)

    )

    df["presencia_digital"] = (
        df["presencia_digital"]
        .astype("Int64")
    )

    return df


# =====================================
# CANALES DE CONTACTO
# =====================================

def crear_canales_contacto(df):
    """
    Variables:
        tiene_telefono
        tiene_email
        tiene_instagram
        tiene_web
        n_canales_contacto

    Interpretación:
        Cantidad de canales mediante los cuales
        un estudio puede ser contactado.

    No incluye la app, ya que representa un
    sistema de reservas y no un canal directo
    de comunicación.
    """

    df["tiene_telefono"] = (
        df["telefono"].notna()
    )

    df["tiene_email"] = (
        df["email"].notna()
    )

    df["tiene_instagram"] = (
        df["instagram"].notna()
    )

    df["tiene_web"] = (
        df["web"].notna()
    )

    df["n_canales_contacto"] = (

        df["tiene_telefono"].astype(int)

        + df["tiene_email"].astype(int)

        + df["tiene_instagram"].astype(int)

        + df["tiene_web"].astype(int)

    )

    df["n_canales_contacto"] = (
        df["n_canales_contacto"]
        .astype("Int64")
    )

    return df


# =====================================
# NÚMERO DE FABRICANTES
# =====================================

def crear_n_fabricantes(df):
    """
    Variable:
        n_fabricantes

    Tipo:
        Entero

    Origen:
        fabricantes_ref

    Interpretación:
        Cantidad de fabricantes registrados
        para cada estudio.
    """

    df["n_fabricantes"] = 0

    tiene_fabricante = (
        df["fabricantes_ref"].notna()
    )

    df.loc[
        tiene_fabricante,
        "n_fabricantes"
    ] = (
        df.loc[
            tiene_fabricante,
            "fabricantes_ref"
        ]
        .str.count(r",| y ")
        + 1
    )

    df["n_fabricantes"] = (
        df["n_fabricantes"]
        .astype("Int64")
    )

    return df


# =====================================
# FABRICANTE MÚLTIPLE
# =====================================

def crear_fabricante_multiple(df):
    """
    Variable:
        fabricante_multiple

    Tipo:
        Booleano

    Interpretación:
        Indica si el estudio utiliza
        más de un fabricante.
    """

    df["fabricante_multiple"] = (
        df["n_fabricantes"] > 1
    )

    return df


# =====================================
# EXPLORACIÓN
# =====================================

def explorar_comunas(df):

    print("\n==============================")
    print(" COMUNAS")
    print("==============================\n")

    print(
        df["comuna"]
        .value_counts(dropna=False)
        .sort_index()
    )

    print(
        f"\nComunas registradas: "
        f"{df['comuna'].nunique()}"
    )

    print(
        f"Registros sin comuna: "
        f"{df['comuna'].isna().sum()}"
    )


def explorar_zonas(df):

    print("\n==============================")
    print(" ZONAS")
    print("==============================\n")

    print(
        df["zona"]
        .value_counts(dropna=False)
    )

    print(
        f"\nZonas registradas: "
        f"{df['zona'].nunique()}"
    )

    print(
        f"Registros sin zona: "
        f"{df['zona'].isna().sum()}"
    )


def explorar_presencia_digital(df):

    print("\n==============================")
    print(" ÍNDICE DE PRESENCIA DIGITAL")
    print("==============================\n")

    print(
        df["presencia_digital"]
        .value_counts()
        .sort_index()
    )

    print(
        f"\nPromedio: "
        f"{df['presencia_digital'].mean():.2f}"
    )

    print(
        f"Máximo: "
        f"{df['presencia_digital'].max()}"
    )

    print(
        f"Estudios con presencia completa: "
        f"{(df['presencia_digital'] == 4).sum()}"
    )


def explorar_canales_contacto(df):

    print("\n==============================")
    print(" CANALES DE CONTACTO")
    print("==============================\n")

    print(
        df["n_canales_contacto"]
        .value_counts()
        .sort_index()
    )

    print(
        f"\nPromedio: "
        f"{df['n_canales_contacto'].mean():.2f}"
    )

    print(
        f"Máximo: "
        f"{df['n_canales_contacto'].max()}"
    )


def explorar_fabricantes(df):

    print("\n==============================")
    print(" FABRICANTES")
    print("==============================\n")

    print(
        df["n_fabricantes"]
        .value_counts()
        .sort_index()
    )

    print("\nFabricantes múltiples:")

    print(
        df["fabricante_multiple"]
        .value_counts()
    )


# =====================================
# GUARDAR
# =====================================

def guardar_datos(df):

    ruta = "data/processed/estudios_features.csv"

    df.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\nArchivo guardado en:\n{ruta}"
    )


# =====================================
# DETECTAR POSIBLES MARCAS
# =====================================

def detectar_posibles_marcas(df):
    """
    Detecta estudios con nombres idénticos
    como candidatos a pertenecer a una misma marca.

    No realiza ninguna asignación automática.

    Retorna
    -------
    DataFrame
    """

    columnas = [
        "id_estudio",
        "nombre_del_estudio",
    ]

    if "direccion" in df.columns:
        columnas.append("direccion")

    candidatos = df[columnas].copy()

    candidatos["nombre_normalizado"] = (
        candidatos["nombre_del_estudio"]
        .fillna("")
        .str.lower()
        .str.strip()
    )

    frecuencia = (
        candidatos["nombre_normalizado"]
        .value_counts()
    )

    candidatos["cantidad_mismo_nombre"] = (
        candidatos["nombre_normalizado"]
        .map(frecuencia)
    )

    candidatos = candidatos[
        candidatos["cantidad_mismo_nombre"] > 1
    ].copy()

    candidatos = candidatos.sort_values(
        [
            "nombre_normalizado",
            "id_estudio"
        ]
    )

    return candidatos


# =====================================
# MAIN
# =====================================

def main():

    df = cargar_datos()

    # =================================
    # IDENTIFICACIÓN DEL ESTUDIO
    # =================================

    # El ID se conserva si ya existe.
    # Solo se genera cuando todavía no existe.

    if "id_estudio" not in df.columns:

        df["id_estudio"] = [
            f"EST-{i:04d}"
            for i in range(1, len(df) + 1)
        ]

    # =================================
    # DETECCIÓN DE POSIBLES MARCAS
    # =================================

    candidatos_marcas = detectar_posibles_marcas(df)

    pd.set_option(
        "display.max_columns",
        None
    )

    pd.set_option(
        "display.max_colwidth",
        100
    )

    pd.set_option(
        "display.width",
        200
    )

    print("\n=====================================")
    print(" CANDIDATOS A MARCA")
    print("=====================================\n")

    print(
        candidatos_marcas[
            [
                "id_estudio",
                "nombre_del_estudio",
                "direccion",
                "nombre_normalizado",
                "cantidad_mismo_nombre"
            ]
        ].to_string(index=False)
    )

    # =================================
    # ESTUDIOS PILATES DEL PINO
    # =================================

    print("\n=====================================")
    print(" ESTUDIOS PILATES DEL PINO")
    print("=====================================\n")

    print(
        df[
            df["nombre_del_estudio"].str.contains(
                "pino",
                case=False,
                na=False
            )
        ][
            [
                "id_estudio",
                "nombre_del_estudio"
            ]
        ]
    )

    # =================================
    # MAESTRO DE MARCAS
    # =================================

    marcas = cargar_marcas_conocidas()

    relacion_estudio_marca = (
        crear_relacion_estudio_marca()
    )

    guardar_relacion_estudio_marca(
        relacion_estudio_marca
    )

    print("\n=====================================")
    print(" MAESTRO DE MARCAS")
    print("=====================================\n")

    print(marcas)

    # =================================
    # GEOGRAFÍA
    # =================================

    df = crear_comuna(df)
    df = crear_zona(df)

    # =================================
    # DIGITAL
    # =================================

    df = crear_presencia_digital(df)

    # =================================
    # CONTACTO
    # =================================

    df = crear_canales_contacto(df)

    # =================================
    # EQUIPAMIENTO
    # =================================

    df = crear_n_fabricantes(df)
    df = crear_fabricante_multiple(df)

    # =================================
    # EXPLORACIÓN
    # =================================

    explorar_comunas(df)
    explorar_zonas(df)
    explorar_presencia_digital(df)
    explorar_canales_contacto(df)
    explorar_fabricantes(df)

    # =================================
    # GUARDAR FEATURES
    # =================================

    guardar_datos(df)


# =====================================
# EJECUCIÓN
# =====================================

if __name__ == "__main__":
    main()
