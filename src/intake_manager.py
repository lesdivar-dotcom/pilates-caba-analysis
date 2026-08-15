from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SUBMISSIONS = ROOT / "data" / "submissions"
SUBMISSIONS.mkdir(parents=True, exist_ok=True)

PENDIENTES = SUBMISSIONS / "pendientes.csv"
APROBADOS = SUBMISSIONS / "aprobados.csv"
RECHAZADOS = SUBMISSIONS / "rechazados.csv"

ESTUDIOS = ROOT / "data" / "processed" / "estudios.csv"

CAMPOS = [
    "fecha",
    "ciudad",
    "barrio",
    "nombre_estudio",
    "direccion",
    "instagram",
    "telefono",
    "email",
    "responsable",
    "reformer",
    "mat",
    "cadillac",
    "chair",
    "barre",
    "prenatal",
    "observaciones",
    "estado"
]


def asegurar_csv(path):

    if not path.exists():

        pd.DataFrame(columns=CAMPOS).to_csv(
            path,
            index=False,
            encoding="utf-8-sig"
        )


def agregar_envio(datos):

    asegurar_csv(PENDIENTES)

    df = pd.read_csv(
        PENDIENTES,
        encoding="utf-8-sig"
    )

    fila = {c: "" for c in CAMPOS}
    fila.update(datos)

    fila["fecha"] = datetime.now().strftime("%Y-%m-%d")
    fila["estado"] = "Pendiente"

    df = pd.concat(
        [df, pd.DataFrame([fila])],
        ignore_index=True
    )

    df.to_csv(
        PENDIENTES,
        index=False,
        encoding="utf-8-sig"
    )


def mover(origen, destino, indice, estado):

    asegurar_csv(origen)
    asegurar_csv(destino)

    df = pd.read_csv(origen)
    out = pd.read_csv(destino)

    fila = df.loc[indice].copy()
    fila["estado"] = estado

    out = pd.concat(
        [out, pd.DataFrame([fila])],
        ignore_index=True
    )

    df = df.drop(indice).reset_index(drop=True)

    df.to_csv(origen, index=False, encoding="utf-8-sig")
    out.to_csv(destino, index=False, encoding="utf-8-sig")


def aprobar_envio(indice):

    mover(
        PENDIENTES,
        APROBADOS,
        indice,
        "Publicado"
    )


def rechazar_envio(indice):

    mover(
        PENDIENTES,
        RECHAZADOS,
        indice,
        "Rechazado"
    )


def integrar_aprobados():

    asegurar_csv(APROBADOS)

    nuevos = pd.read_csv(APROBADOS)
    estudios = pd.read_csv(ESTUDIOS)

    if nuevos.empty:

        print("No hay estudios aprobados.")
        return

    estudios = pd.concat(
        [estudios, nuevos],
        ignore_index=True
    )

    estudios.to_csv(
        ESTUDIOS,
        index=False,
        encoding="utf-8-sig"
    )

    nuevos.iloc[0:0].to_csv(
        APROBADOS,
        index=False,
        encoding="utf-8-sig"
    )

    print("Estudios integrados correctamente.")


if __name__ == "__main__":

    asegurar_csv(PENDIENTES)
    asegurar_csv(APROBADOS)
    asegurar_csv(RECHAZADOS)

    print("Sistema editorial listo.")