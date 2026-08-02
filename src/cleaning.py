"""
Limpieza de datos
Proyecto: Mercado de Estudios de Pilates en CABA
Autor: Tu nombre
"""
"""
Proyecto: Análisis del mercado de estudios de Pilates en CABA

Módulo:
    cleaning.py

Responsabilidad:
    - Leer datos originales
    - Limpiar columnas
    - Transformar variables
    - Validar datos
    - Exportar dataset limpio

Autor:
    Tu nombre

Fecha:
    2026
"""

import pandas as pd
import re
from pathlib import Path

# =====================================
# RUTAS
# =====================================

RUTA_RAW = Path("data/raw/estudios_raw.csv")
RUTA_LIMPIO = Path("data/interim/estudios_limpios.csv")


# =====================================
# CARGA DE DATOS
# =====================================

def cargar_datos():

    print("Leyendo archivo...")

    df = pd.read_csv(RUTA_RAW)

    print(f"Se cargaron {len(df)} estudios.")

    return df


# =====================================
# LIMPIEZA DE COLUMNAS
# =====================================

def limpiar_columnas(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    df = df.rename(columns={
        "dirección": "direccion",
        "teléfono": "telefono",
        "diseño": "diseno",
        "presentación": "presentacion",
        "código_plus": "codigo_plus",
        "fecha_de_recolección": "fecha_recoleccion",
        "puntaje_x_reserñas": "puntaje_google",
        "observacciones": "observaciones",
        "opiniones": "resena_destacada",
    })

    df = df.drop(columns=["unnamed:_20"], errors="ignore")

    return df


# =====================================
# SEGUIDORES
# =====================================

def limpiar_valor_seguidores(valor):

    if pd.isna(valor):
        return None

    valor = str(valor).strip().lower()

    if "mil" in valor:

        numero = (
            valor
            .replace("mil", "")
            .replace(",", ".")
            .strip()
        )

        return int(float(numero) * 1000)

    valor = valor.replace(".", "")
    valor = valor.replace(",", "")

    return int(valor)


def limpiar_seguidores(df):

    df["seguidores"] = (
        df["seguidores"]
        .apply(limpiar_valor_seguidores)
        .astype("Int64")
    )

    return df


# =====================================
# PUNTAJE GOOGLE
# =====================================

def limpiar_puntajes(df):

    separado = (
        df["puntaje_google"]
        .str.replace(",", ".", regex=False)
        .str.extract(
            r"(?P<puntaje>\d+\.\d)\s*x\s*(?P<resenas>\d+)"
        )
    )

    df["puntaje_google"] = separado["puntaje"].astype(float)

    df["cantidad_resenas"] = separado["resenas"].astype("Int64")

    return df

# =====================================
# TELEFONOS
# =====================================

def explorar_telefonos(df):

    print("\n===== TELEFONOS =====\n")

    print(df["telefono"].head(20))

    print("\nPrimeros 30 valores únicos:\n")

    print(df["telefono"].dropna().unique()[:30])

    print("\nCantidad de teléfonos vacíos:")

    print(df["telefono"].isna().sum())
    
def analizar_longitud_telefonos(df):

    telefonos = (
        df["telefono"]
        .dropna()
        .astype(str)
        .str.replace(r"\D", "", regex=True)
    )

    print("\n===== LONGITUD DE TELEFONOS =====\n")

    print(
        telefonos
        .str.len()
        .value_counts()
        .sort_index()
    )
# =====================================
# LIMPIEZA DE TELEFONOS
# =====================================

def limpiar_telefonos(df):

    df["telefono"] = (
        df["telefono"]
        .astype("string")
        .str.replace(r"\D", "", regex=True)  # elimina guiones, espacios, paréntesis
        .str.strip()
    )

    return df
# =====================================
# EMAIL
# =====================================

def explorar_emails(df):

    print("\n===== EMAILS =====\n")

    print(df["email"].head(20))

    print("\nPrimeros 30 valores únicos:\n")

    print(df["email"].dropna().unique()[:30])

    print("\nCantidad de emails vacíos:")

    print(df["email"].isna().sum())
    

def limpiar_emails(df):
    """
    Conserva únicamente los emails con un formato válido.
    El resto se convierte en NA.
    """

    patron = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    df["email"] = (
        df["email"]
        .astype("string")
        .str.strip()
    )

    df["email"] = df["email"].where(
        df["email"].str.match(patron, na=False),
        pd.NA
    )

    return df

def validar_emails(df):

    print("\n===== EMAILS VALIDOS =====\n")

    print(df["email"].dropna().head(20))

    print("\nCantidad de emails válidos:")

    print(df["email"].notna().sum())
    
def explorar_barrios(df):

    print("\n===== BARRIOS =====\n")

    print(df["barrio"].head(20))

    print("\nCantidad de barrios distintos:")

    print(df["barrio"].nunique())

    print("\nBarrios únicos:\n")

    print(sorted(df["barrio"].dropna().unique()))
def limpiar_barrios(df):

    df["barrio"] = (
        df["barrio"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    reemplazos = {

        "Belgrano, Sede Nueva En Recoleta.": "Belgrano",

        "Palermo Soho": "Palermo",
        "Palermo Hollywood": "Palermo",
        "Palermo Chico": "Palermo",
        "Palermo  Soho": "Palermo",
        "Palermo Es Recoleta": "Palermo",
        "Palermo  Es Recoleta": "Palermo",
        "Palermo  Es Recoleta ": "Palermo",
        "Palermo Hollywood ": "Palermo",

        "Recoleta O Palermo": "Recoleta",
        "Recoleta Y Palermo": "Recoleta",

        "Colegiales- Palermo Hollywood": "Colegiales",

        "Villa Del Parque": "Villa del Parque",
        "Villa Del parque": "Villa del Parque",

        "Villa Crespo": "Villa Crespo",
        "Villa Urquiza": "Villa Urquiza",

        "Villa General Mitre": "Villa General Mitre",
        "Villa Real ": "Villa Real",

        "Agranomía": "Agronomía",
        "Chacharita": "Chacarita",
        "Linier": "Liniers",
        "Paque Chacabuco": "Parque Chacabuco",

        "Villa Luro O Floresta": "Villa Luro",
        "Villa Luro O Versalles": "Villa Luro",
        "Almagro (Está Dentro Del Abasto)": "Almagro",
        "Vélez": "Vélez Sársfield"
    }

    df["barrio"] = df["barrio"].replace(reemplazos)

    return df
def contar_barrios(df):

    print("\n===== CANTIDAD DE ESTUDIOS POR BARRIO =====\n")

    conteo = (
        df["barrio"]
        .value_counts()
        .sort_values(ascending=False)
    )

    print(conteo)
    print("\nBarrios vacíos:")

    print(df["barrio"].isna().sum())
def revisar_barrios_vacios(df):

    print("\n===== ESTUDIOS SIN BARRIO =====\n")

    print(
        df.loc[
            df["barrio"].isna(),
            [
                "nombre_del_estudio",
                "direccion",
                "telefono",
                "instagram",
                "web"
            ]
        ]
    )
  
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 200)

def revisar_barrios_vacios(df):

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.width", 200)

    print("\n===== ESTUDIOS SIN BARRIO =====\n")

    print(
        df.loc[
            df["barrio"].isna(),
            [
                "nombre_del_estudio",
                "direccion",
                "telefono",
                "instagram",
                "web"
            ]
        ]
    )  
def completar_barrios_faltantes(df):

    correcciones = {
        "Mikigai Pilates": "Floresta",
        "Espacio Mat - CLASES ONLINE de Pilates - Elongación - Yoga": "Colegiales",
        "Holística Yoga & Pilates": "Boedo",
        "CONSCIOUS STUDIO PILATES": "Villa del Parque",
    }

    for estudio, barrio in correcciones.items():
        df.loc[
            df["nombre_del_estudio"] == estudio,
            "barrio"
        ] = barrio

    return df
# =====================================
# FABRICANTES
# =====================================

def explorar_fabricantes(df):

    print("\n===== FABRICANTES =====\n")

    print(df["fabricantes_ref"].head(20))

    print("\nCantidad de valores únicos:")

    print(df["fabricantes_ref"].nunique())

    print("\nCantidad de valores vacíos:")

    print(df["fabricantes_ref"].isna().sum())


def contar_fabricantes(df):

    print("\n===== FRECUENCIA DE FABRICANTES =====\n")

    conteo = (
        df["fabricantes_ref"]
        .fillna("No informado")
        .value_counts(dropna=False)
        .sort_values(ascending=False)
    )

    print(conteo.to_string())
def explorar_diseno(df):

    print("\n===== DISEÑO =====\n")

    print(df["diseno"].head(20))

    print("\nCantidad de valores únicos:")

    print(df["diseno"].nunique(dropna=True))

    print("\nCantidad de valores vacíos:")

    print(df["diseno"].isna().sum())

    print("\n===== FRECUENCIA DE DISEÑO =====\n")

    conteo = (
        df["diseno"]
        .fillna("No informado")
        .value_counts(dropna=False)
    )

    print(conteo.to_string())  
# =====================================
# WEB
# =====================================

def explorar_web(df):

    print("\n===== WEB =====\n")

    print(df["web"].head(20))

    print("\nCantidad de webs:")

    print(df["web"].notna().sum())

    print("\nCantidad de vacíos:")

    print(df["web"].isna().sum())

    print("\nPrimeros 30 valores únicos:\n")

    print(df["web"].dropna().unique()[:30])  
# =====================================
# LIMPIAR WEB
# =====================================

def limpiar_web(df):

    df["web"] = (
        df["web"]
        .astype("string")
        .str.strip()
    )

    # Valores que no son sitios web
    reemplazos = {
        "-": pd.NA,
        "": pd.NA,
        "No": pd.NA,
        "No tiene": pd.NA,
        "Pilates Mat online": pd.NA
    }

    df["web"] = df["web"].replace(reemplazos)

    return df
# =====================================
# INSTAGRAM
# =====================================

def explorar_instagram(df):

    print("\n===== INSTAGRAM =====\n")
    print(df["instagram"].head(20))

    print("\nCantidad de cuentas:")
    print(df["instagram"].notna().sum())

    print("\nCantidad de vacíos:")
    print(df["instagram"].isna().sum())

    print("\nCantidad de valores únicos:")
    print(df["instagram"].nunique(dropna=True))

    print("\nPrimeros 30 valores únicos:\n")
    print(df["instagram"].dropna().unique()[:30])
    
def limpiar_instagram(df):

    df["instagram"] = (
        df["instagram"]
        .astype("string")
        .str.strip()
        .str.replace(
            r"https?://(www\.)?instagram\.com/",
            "",
            regex=True
        )
        .str.replace(r"\?.*", "", regex=True)
        .str.replace(r"#.*", "", regex=True)
        .str.strip("/")
    )

    return df
# =====================================
# DISEÑO
# =====================================

def explorar_diseno(df):

    print("\n===== DISEÑO =====\n")

    print(df["diseno"].head(20))

    print("\nCantidad con información:")

    print(df["diseno"].notna().sum())

    print("\nCantidad de vacíos:")

    print(df["diseno"].isna().sum())

    print("\nCantidad de valores únicos:")

    print(df["diseno"].nunique(dropna=True))

    print("\nPrimeros 30 valores únicos:\n")

    print(df["diseno"].dropna().unique()[:30])
    
def limpiar_diseno(df):

    df["diseno"] = (
        df["diseno"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    return df

# =====================================
# APP
# =====================================

def explorar_app(df):

    print("\n===== APP =====\n")

    print(df["app"].head(20))

    print("\nCantidad con información:")

    print(df["app"].notna().sum())

    print("\nCantidad de vacíos:")

    print(df["app"].isna().sum())

    print("\nCantidad de valores únicos:")

    print(df["app"].nunique(dropna=True))

    print("\nPrimeros 30 valores únicos:\n")

    print(df["app"].dropna().unique()[:30])

# =====================================
# APP
# =====================================

def limpiar_app(df):

    df["app"] = (
        df["app"]
        .astype("string")
        .str.strip()
    )

    # Valores que no aportan
    df["app"] = df["app"].replace(
        ["-", "No tiene recientes"],
        pd.NA
    )

    # Reseñas pegadas por error
    df.loc[
        df["app"].str.startswith("Hace ", na=False),
        "app"
    ] = pd.NA

    # Plataformas
    df.loc[
        df["app"].str.contains("siguefit", case=False, na=False),
        "app"
    ] = "Siguefit"

    df.loc[
        df["app"].str.contains("reservaclase", case=False, na=False),
        "app"
    ] = "ReservaClase"

    df.loc[
        df["app"].str.contains("luweva", case=False, na=False),
        "app"
    ] = "Luweva"

    df.loc[
        df["app"].str.contains("agendapro", case=False, na=False),
        "app"
    ] = "AgendaPro"

    df.loc[
        df["app"].str.contains("quedeporte", case=False, na=False),
        "app"
    ] = "Quedeporte"

    df.loc[
        df["app"].str.contains("somapilates", case=False, na=False),
        "app"
    ] = "SomaPilates"

    df.loc[
        df["app"].str.contains("fitfit", case=False, na=False),
        "app"
    ] = "Fitfit"

    df.loc[
        df["app"].str.contains("hawafitness", case=False, na=False),
        "app"
    ] = "Hawa Fitness"

    df.loc[
        df["app"].str.contains("linktr.ee", case=False, na=False),
        "app"
    ] = "Linktree"

    return df
# =====================================
# GUARDAR
# =====================================

def guardar_csv(df):

    df.to_csv(RUTA_LIMPIO, index=False)

    print(f"\nArchivo guardado en:\n{RUTA_LIMPIO}")


# =====================================
# MAIN
# =====================================

def main():

    df = cargar_datos()

    df = limpiar_columnas(df)
    df = limpiar_seguidores(df)
    df = limpiar_puntajes(df)
    df = limpiar_telefonos(df)
    df = limpiar_emails(df)
    df = limpiar_barrios(df)
    df = limpiar_web(df)
    df = limpiar_instagram(df)
    df = limpiar_diseno(df)
    df = limpiar_app(df)          # ← AGREGAR ESTA LÍNEA
    df = completar_barrios_faltantes(df)

    print("\nPrimeras filas:")
    print(df.head())

    explorar_emails(df)
    validar_emails(df)
    explorar_telefonos(df)
    explorar_barrios(df)
    contar_barrios(df)
    explorar_fabricantes(df)
    contar_fabricantes(df)
    explorar_diseno(df)
    explorar_web(df)
    explorar_instagram(df)
    explorar_app(df)              # ← ahora muestra la columna ya limpia
    revisar_barrios_vacios(df)
    analizar_longitud_telefonos(df)

    print("\n===== APP LIMPIA =====\n")
    print(df["app"].value_counts(dropna=False))

    guardar_csv(df)

if __name__ == "__main__":
    main()