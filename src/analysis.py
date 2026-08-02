#analysis.py
import pandas as pd

RUTA_LIMPIO = "data/interim/estudios_limpios.csv"


def cargar_datos():

    print("Leyendo datos limpios...")

    df = pd.read_csv(
        RUTA_LIMPIO,
        dtype_backend="pyarrow"
    )

    return df
def resumen_general(df):

    print("\n==============================")
    print(" OBSERVATORIO PILATES CABA ")
    print("==============================\n")

    print(f"Total de estudios: {len(df)}")

    print(f"Con Instagram: {df['instagram'].notna().sum()}")

    print(f"Con web: {df['web'].notna().sum()}")

    print(f"Con email: {df['email'].notna().sum()}")

    print(f"Con teléfono: {df['telefono'].notna().sum()}")

    print(f"Con app: {df['app'].notna().sum()}")

    print(f"Barrios: {df['barrio'].nunique()}")

    print(f"Fabricantes registrados: {df['fabricantes_ref'].nunique(dropna=True)}")
    
def analizar_barrios(df):

    tabla = (
        df.groupby("barrio", dropna=False)
        .agg(
            estudios=("nombre_del_estudio", "count"),
            seguidores_promedio=("seguidores", "mean"),
            puntaje_promedio=("puntaje", "mean"),
            resenas_promedio=("cantidad_resenas", "mean"),
        )
        .sort_values("estudios", ascending=False)
        .round(1)
    )

    tabla["porcentaje"] = (
        tabla["estudios"] / len(df) * 100
    ).round(1)

    print("\n===== MERCADO POR BARRIO =====\n")
    print(tabla)

    return tabla
    
def main():

    df = cargar_datos()

    resumen_general(df)


if __name__ == "__main__":

    main() 