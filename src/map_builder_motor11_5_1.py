# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 11.5.1 — Escala Cromática Territorial Continua
# ============================================================
#
# Responsabilidad única
# ---------------------
# Construir la cartografía territorial del Observatorio a partir
# del checkpoint vigente del territorio, respetando:
#
# - city_paths() como contrato institucional de rutas;
# - territory_profile.json como contrato cartográfico;
# - unidad operativa del lote;
# - unidad cartográfica institucional;
# - bridge territorial explícito cuando ambas unidades difieren;
# - GeoJSON declarado por territory_profile.json;
# - paleta institucional Transverso;
# - territorios sin cobertura en gris;
# - encuadre mediante fit_bounds sobre geometrías observadas.
#
# NO:
# - descubre estudios;
# - modifica datasets;
# - inventa equivalencias territoriales;
# - redefine la unidad analítica del Dashboard;
# - hardcodea comportamiento por ciudad.
#
# Uso:
#   python src/map_builder_motor11_5.py \
#       --city buenos_aires_provincia \
#       --lote ba_norte
#
# Salida:
#   data/countries/.../<territorio>/dashboard/mapa_<city>.html
# ============================================================

import argparse
import json
import math
import unicodedata
from copy import deepcopy
from pathlib import Path

import folium
import pandas as pd

from city_config import city_paths
from theme import TRANSVERSO as T


# ============================================================
# CONSTANTES
# ============================================================

COLUMNAS_TERRITORIALES = [
    "localidad",
    "municipio",
    "barrio",
    "comuna",
    "zona",
]

COLOR_SIN_DATO = T.get("gris", "#ECECEC")

# La escala se usa para intensidad relativa de la métrica cartográfica.
PALETA_DATOS = [
    T.get("borgona", "#6A2E2E"),
    T.get("terracota", "#8A5A3A"),
    T.get("arena", "#A88A4A"),
    T.get("verde", "#5C7A3A"),
]


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalizar(texto):
    """
    Normaliza claves territoriales sin modificar el valor original.
    """

    if texto is None or pd.isna(texto):
        return ""

    texto = str(texto).strip()

    texto = "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

    return " ".join(texto.lower().split())


# ============================================================
# PERFIL TERRITORIAL
# ============================================================

def cargar_profile(rutas):
    """
    Carga el contrato territorial institucional.
    """

    ruta = rutas["reference"] / "territory_profile.json"

    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe territory_profile.json:\n{ruta}"
        )

    profile = json.loads(
        ruta.read_text(encoding="utf-8")
    )

    requeridos = [
        "display_name",
        "territory_unit",
        "geojson",
    ]

    faltantes = [
        c for c in requeridos
        if not profile.get(c)
    ]

    if faltantes:
        raise KeyError(
            "territory_profile.json incompleto. "
            f"Faltan: {faltantes}"
        )

    return profile


# ============================================================
# DATASET DEL CHECKPOINT
# ============================================================

def localizar_dataset(rutas, lote=None):
    """
    Respeta el orden del pipeline vigente.

    Para un lote:
        consolidated -> enrichment -> processed

    Sin lote:
        provincial -> consolidated general -> processed

    No vuelve hacia raw/interim.
    """

    base = rutas["base"]

    candidatos = []

    if lote:
        candidatos.extend([
            base / "consolidated" / lote / "estudios_consolidados.csv",
            base / "enrichment" / lote / "estudios_enriquecidos.csv",
            base / "processed" / lote / "estudios_features.csv",
        ])

    candidatos.extend([
        base / "provincial" / "estudios_provincia.csv",
        base / "consolidated" / "estudios_consolidados.csv",
        base / "processed" / "estudios_features.csv",
    ])

    for ruta in candidatos:
        if ruta.exists():
            return ruta

    raise FileNotFoundError(
        "No se encontró un dataset territorial válido.\n"
        + "\n".join(str(p) for p in candidatos)
    )


def cargar_dataset(ruta):
    return pd.read_csv(
        ruta,
        encoding="utf-8-sig"
    )


# ============================================================
# UNIDAD OPERATIVA
# ============================================================

def detectar_unidad_operativa(df, unidad_institucional, lote=None):
    """
    La unidad institucional viene del profile.
    Un lote puede operar a granularidad más fina.

    Prioridad para lotes:
        localidad -> municipio -> barrio -> comuna -> institucional

    Sin lote:
        institucional -> resto de columnas territoriales.
    """

    if lote:
        prioridad = [
            "localidad",
            "municipio",
            "barrio",
            "comuna",
            unidad_institucional,
        ]
    else:
        prioridad = [
            unidad_institucional,
            "municipio",
            "localidad",
            "barrio",
            "comuna",
        ]

    vistas = []

    for c in prioridad:
        if c and c not in vistas:
            vistas.append(c)

    for c in vistas:
        if c in df.columns:
            serie = df[c].fillna("").astype(str).str.strip()

            if serie.ne("").any():
                return c

    raise KeyError(
        "No fue posible detectar una unidad territorial operativa. "
        f"Columnas disponibles: {list(df.columns)}"
    )


# ============================================================
# GEOJSON
# ============================================================

def cargar_geojson(rutas, profile):
    """
    Carga EXCLUSIVAMENTE el GeoJSON declarado por el profile.
    """

    ruta = rutas["reference"] / profile["geojson"]

    if not ruta.exists():
        raise FileNotFoundError(
            f"GeoJSON institucional no encontrado:\n{ruta}"
        )

    geojson = json.loads(
        ruta.read_text(encoding="utf-8")
    )

    if not geojson.get("features"):
        raise ValueError(
            f"El GeoJSON no contiene features:\n{ruta}"
        )

    return ruta, geojson


def obtener_name_field(geojson, unidad_institucional):
    """
    Detecta el campo nominal del GeoJSON.

    Primero intenta candidatos específicos de la unidad declarada.
    Después usa candidatos institucionales conocidos.
    """

    props = geojson["features"][0].get("properties", {})

    candidatos = [
        f"{unidad_institucional}_nombre",
        unidad_institucional,
        unidad_institucional.upper(),
        "municipio_nombre",
        "municipio",
        "MUNICIPIO",
        "barrio",
        "BARRIO",
        "nombre",
        "NOMBRE",
        "localidad",
        "LOCALIDAD",
        "comuna",
        "COMUNA",
    ]

    for campo in candidatos:
        if campo in props:
            return campo

    raise KeyError(
        "No se encontró el campo nominal del GeoJSON. "
        f"Propiedades disponibles: {list(props.keys())}"
    )


# ============================================================
# BRIDGE TERRITORIAL
# ============================================================

def localizar_bridge(rutas, unidad_operativa, unidad_institucional):
    """
    Contrato de naming:
        <unidad_operativa>_<unidad_institucional>.csv

    Ejemplo:
        localidad_municipio.csv
    """

    nombre = (
        f"{unidad_operativa}_{unidad_institucional}.csv"
    )

    ruta = rutas["reference"] / nombre

    return ruta


def cargar_bridge(
    rutas,
    unidad_operativa,
    unidad_institucional,
):
    """
    El bridge es obligatorio únicamente cuando las unidades difieren.
    """

    if unidad_operativa == unidad_institucional:
        return None, None

    ruta = localizar_bridge(
        rutas,
        unidad_operativa,
        unidad_institucional,
    )

    if not ruta.exists():
        raise FileNotFoundError(
            "Las unidades operativa e institucional difieren y "
            "no existe el bridge territorial requerido:\n"
            f"{ruta}"
        )

    bridge = pd.read_csv(
        ruta,
        encoding="utf-8-sig"
    )

    requeridas = [
        unidad_operativa,
        unidad_institucional,
    ]

    faltantes = [
        c for c in requeridas
        if c not in bridge.columns
    ]

    if faltantes:
        raise KeyError(
            f"Bridge territorial inválido: {ruta}\n"
            f"Faltan columnas: {faltantes}"
        )

    bridge = bridge[
        requeridas
    ].copy()

    bridge[unidad_operativa] = (
        bridge[unidad_operativa]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    bridge[unidad_institucional] = (
        bridge[unidad_institucional]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Una localidad/unidad operativa no puede apuntar
    # a dos unidades institucionales diferentes.
    conflictos = (
        bridge
        .assign(
            _op=bridge[unidad_operativa].map(normalizar),
            _inst=bridge[unidad_institucional].map(normalizar),
        )
        .groupby("_op")["_inst"]
        .nunique()
    )

    conflictos = conflictos[
        conflictos > 1
    ]

    if not conflictos.empty:
        raise ValueError(
            "El bridge territorial contiene equivalencias ambiguas:\n"
            + "\n".join(conflictos.index.tolist())
        )

    return ruta, bridge


# ============================================================
# AGREGACIÓN CARTOGRÁFICA
# ============================================================

def preparar_agregado(
    df,
    unidad_operativa,
    unidad_institucional,
    bridge=None,
):
    """
    Genera una vista derivada para cartografía.

    Métrica inicial:
        cantidad de estudios observados.

    El dataset original no se modifica.
    """

    trabajo = df.copy()

    if unidad_operativa not in trabajo.columns:
        raise KeyError(
            f"La unidad operativa '{unidad_operativa}' "
            "no existe en el dataset."
        )

    trabajo[unidad_operativa] = (
        trabajo[unidad_operativa]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    trabajo = trabajo[
        trabajo[unidad_operativa] != ""
    ].copy()

    if bridge is None:
        trabajo["_unidad_cartografica"] = (
            trabajo[unidad_operativa]
        )
    else:
        puente = bridge.copy()

        puente["_clave_operativa"] = (
            puente[unidad_operativa]
            .map(normalizar)
        )

        lookup = dict(
            zip(
                puente["_clave_operativa"],
                puente[unidad_institucional],
            )
        )

        trabajo["_clave_operativa"] = (
            trabajo[unidad_operativa]
            .map(normalizar)
        )

        trabajo["_unidad_cartografica"] = (
            trabajo["_clave_operativa"]
            .map(lookup)
        )

        sin_bridge = trabajo[
            trabajo["_unidad_cartografica"].isna()
            | trabajo["_unidad_cartografica"].astype(str).str.strip().eq("")
        ]

        if not sin_bridge.empty:
            valores = sorted(
                sin_bridge[unidad_operativa]
                .astype(str)
                .unique()
                .tolist()
            )

            raise ValueError(
                "Existen unidades operativas sin equivalencia "
                "en el bridge territorial:\n"
                + "\n".join(valores)
            )

    total = len(trabajo)

    agregado = (
        trabajo
        .groupby(
            "_unidad_cartografica",
            dropna=False,
        )
        .agg(
            estudios=("id_estudio", "size")
            if "id_estudio" in trabajo.columns
            else (unidad_operativa, "size"),
            localidades_observadas=(
                unidad_operativa,
                lambda s: " · ".join(
                    sorted(
                        {
                            str(v).strip()
                            for v in s
                            if str(v).strip()
                        }
                    )
                ),
            ),
            n_unidades_operativas=(
                unidad_operativa,
                lambda s: len(
                    {
                        normalizar(v)
                        for v in s
                        if normalizar(v)
                    }
                ),
            ),
        )
        .reset_index()
        .rename(
            columns={
                "_unidad_cartografica":
                    unidad_institucional
            }
        )
    )

    if total:
        agregado["participacion_pct"] = (
            agregado["estudios"]
            / total
            * 100
        )
    else:
        agregado["participacion_pct"] = 0.0

    agregado["_clave_cartografica"] = (
        agregado[unidad_institucional]
        .map(normalizar)
    )

    return trabajo, agregado


# ============================================================
# ESCALA CROMÁTICA
# ============================================================

def _hex_a_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def _rgb_a_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(
        *[
            max(0, min(255, int(round(v))))
            for v in rgb
        ]
    )


def _interpolar_color(color_a, color_b, t):
    """
    Interpolación lineal RGB.
    t debe estar entre 0 y 1.
    """

    t = max(0.0, min(1.0, float(t)))

    a = _hex_a_rgb(color_a)
    b = _hex_a_rgb(color_b)

    rgb = tuple(
        a[i] + (b[i] - a[i]) * t
        for i in range(3)
    )

    return _rgb_a_hex(rgb)


def color_datos(valor, minimo, maximo):
    """
    Escala cromática continua institucional:

        borgoña -> terracota -> arena -> verde

    Cada valor observado recibe un color interpolado según
    su posición relativa entre mínimo y máximo.

    Gris queda reservado exclusivamente para "sin dato".
    """

    if valor is None or pd.isna(valor):
        return COLOR_SIN_DATO

    valor = float(valor)

    if valor <= 0:
        return COLOR_SIN_DATO

    if maximo <= minimo:
        return PALETA_DATOS[-1]

    ratio = (
        (valor - minimo)
        / (maximo - minimo)
    )

    ratio = max(
        0.0,
        min(1.0, ratio)
    )

    if ratio <= (1 / 3):
        local_t = ratio / (1 / 3)

        return _interpolar_color(
            PALETA_DATOS[0],
            PALETA_DATOS[1],
            local_t,
        )

    if ratio <= (2 / 3):
        local_t = (
            ratio - (1 / 3)
        ) / (1 / 3)

        return _interpolar_color(
            PALETA_DATOS[1],
            PALETA_DATOS[2],
            local_t,
        )

    local_t = (
        ratio - (2 / 3)
    ) / (1 / 3)

    return _interpolar_color(
        PALETA_DATOS[2],
        PALETA_DATOS[3],
        local_t,
    )


# ============================================================
# BOUNDS GEOJSON
# ============================================================

def _iter_coords(obj):
    """
    Itera coordenadas GeoJSON de cualquier profundidad.
    Produce pares (lon, lat).
    """

    if isinstance(obj, (list, tuple)):
        if (
            len(obj) >= 2
            and isinstance(obj[0], (int, float))
            and isinstance(obj[1], (int, float))
        ):
            yield float(obj[0]), float(obj[1])
        else:
            for item in obj:
                yield from _iter_coords(item)


def bounds_features(features):
    """
    Devuelve [[south, west], [north, east]]
    para un conjunto de features.
    """

    lons = []
    lats = []

    for feature in features:
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates")

        if coords is None:
            continue

        for lon, lat in _iter_coords(coords):
            if math.isfinite(lon) and math.isfinite(lat):
                lons.append(lon)
                lats.append(lat)

    if not lons or not lats:
        return None

    return [
        [min(lats), min(lons)],
        [max(lats), max(lons)],
    ]


def centro_desde_bounds(bounds):
    if not bounds:
        return [-36.6769, -60.5588]

    (south, west), (north, east) = bounds

    return [
        (south + north) / 2,
        (west + east) / 2,
    ]


# ============================================================
# ENRIQUECIMIENTO DEL GEOJSON
# ============================================================

def enriquecer_geojson(
    geojson,
    campo_nombre,
    agregado,
    unidad_institucional,
):
    """
    Inserta métricas cartográficas en una copia del GeoJSON.
    """

    salida = deepcopy(geojson)

    lookup = {
        r["_clave_cartografica"]: r
        for _, r in agregado.iterrows()
    }

    valores = (
        agregado["estudios"]
        .astype(float)
        .tolist()
    )

    minimo = min(valores) if valores else 0
    maximo = max(valores) if valores else 0

    enlazados = 0
    observadas = []

    for feature in salida["features"]:

        props = feature.setdefault(
            "properties",
            {}
        )

        nombre_original = str(
            props.get(campo_nombre, "")
        ).strip()

        clave = normalizar(
            nombre_original
        )

        fila = lookup.get(clave)

        if fila is None:
            props["_transverso_estudios"] = None
            props["_transverso_participacion"] = None
            props["_transverso_localidades"] = ""
            props["_transverso_cobertura"] = "Sin cobertura observada"
            props["_transverso_color"] = COLOR_SIN_DATO

        else:
            estudios = int(fila["estudios"])
            participacion = float(
                fila["participacion_pct"]
            )

            props["_transverso_estudios"] = estudios
            props["_transverso_participacion"] = round(
                participacion,
                2,
            )
            props["_transverso_localidades"] = (
                fila["localidades_observadas"]
            )
            props["_transverso_cobertura"] = "Observado"
            props["_transverso_color"] = color_datos(
                estudios,
                minimo,
                maximo,
            )

            enlazados += 1
            observadas.append(feature)

    return salida, observadas, enlazados


# ============================================================
# LEYENDA
# ============================================================

def construir_leyenda(
    unidad_institucional,
    lote,
):
    contexto = (
        f" · lote {lote}"
        if lote
        else ""
    )

    return f"""
    <div style="
        position:fixed;
        bottom:28px;
        left:28px;
        z-index:9999;
        background:white;
        padding:13px 15px;
        border-radius:10px;
        box-shadow:0 4px 14px rgba(0,0,0,.18);
        font-size:12px;
        line-height:1.65;
        min-width:210px;
        color:#23313D;
    ">
        <b>Estudios observados por {unidad_institucional}{contexto}</b><br>
        <span style="color:{PALETA_DATOS[3]};">■</span> Intensidad alta<br>
        <span style="color:{PALETA_DATOS[2]};">■</span> Intensidad media alta<br>
        <span style="color:{PALETA_DATOS[1]};">■</span> Intensidad media baja<br>
        <span style="color:{PALETA_DATOS[0]};">■</span> Intensidad baja<br>
        <span style="color:{COLOR_SIN_DATO};">■</span> Sin cobertura observada
    </div>
    """


# ============================================================
# CONSTRUCCIÓN DEL MAPA
# ============================================================

def construir_mapa(
    city,
    lote,
    profile,
    geojson,
    campo_nombre,
    agregado,
):
    """
    Construye la vista cartográfica universal.
    """

    unidad_institucional = (
        profile["territory_unit"]
    )

    (
        geo_enriquecido,
        features_observadas,
        enlazados,
    ) = enriquecer_geojson(
        geojson,
        campo_nombre,
        agregado,
        unidad_institucional,
    )

    # El mapa nunca recibe una geometría como location.
    # Inicializamos con el centro calculado del GeoJSON total
    # y luego aplicamos fit_bounds.
    bounds_total = bounds_features(
        geo_enriquecido["features"]
    )

    location = centro_desde_bounds(
        bounds_total
    )

    mapa = folium.Map(
        location=location,
        zoom_start=7,
        tiles="CartoDB positron",
        control_scale=True,
    )

    tooltip_fields = [
        campo_nombre,
        "_transverso_estudios",
        "_transverso_participacion",
        "_transverso_localidades",
        "_transverso_cobertura",
    ]

    tooltip_aliases = [
        f"{unidad_institucional.capitalize()}:",
        "Estudios:",
        "Participación del contexto (%):",
        "Unidades operativas observadas:",
        "Cobertura:",
    ]

    folium.GeoJson(
        geo_enriquecido,
        name="Cobertura territorial",
        style_function=lambda f: {
            "fillColor": (
                f["properties"]
                .get(
                    "_transverso_color",
                    COLOR_SIN_DATO,
                )
            ),
            "color": "#FFFFFF",
            "weight": 1.0,
            "fillOpacity": (
                0.82
                if (
                    f["properties"]
                    .get("_transverso_estudios")
                    is not None
                )
                else 0.28
            ),
        },
        highlight_function=lambda f: {
            "weight": 2.2,
            "color": "#23313D",
            "fillOpacity": (
                0.90
                if (
                    f["properties"]
                    .get("_transverso_estudios")
                    is not None
                )
                else 0.38
            ),
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            sticky=True,
            localize=True,
            labels=True,
        ),
    ).add_to(mapa)

    # Para un lote se encuadra la cobertura observada.
    # Sin lote se mantiene el territorio completo.
    if lote and features_observadas:
        bounds_obs = bounds_features(
            features_observadas
        )

        if bounds_obs:
            mapa.fit_bounds(
                bounds_obs,
                padding=(28, 28),
            )

    elif bounds_total:
        mapa.fit_bounds(
            bounds_total,
            padding=(12, 12),
        )

    leyenda = construir_leyenda(
        unidad_institucional,
        lote,
    )

    mapa.get_root().html.add_child(
        folium.Element(leyenda)
    )

    folium.LayerControl(
        collapsed=True
    ).add_to(mapa)

    print(
        f"{unidad_institucional.capitalize()}s enlazados "
        f"con GeoJSON: {enlazados}/{len(agregado)}"
    )

    return mapa, enlazados


# ============================================================
# VALIDACIONES
# ============================================================

def validar_checkpoint(
    df,
    agregado,
    unidad_operativa,
    unidad_institucional,
):
    """
    Validaciones que deben cumplirse antes de exportar.
    """

    if df.empty:
        raise ValueError(
            "El dataset territorial está vacío."
        )

    if agregado.empty:
        raise ValueError(
            "No se pudo generar el agregado cartográfico."
        )

    total_agregado = int(
        agregado["estudios"].sum()
    )

    total_df = int(
        df[unidad_operativa]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    if total_agregado != total_df:
        raise AssertionError(
            "La agregación cartográfica perdió registros: "
            f"{total_agregado}/{total_df}"
        )

    print(
        "✓ Checkpoint cartográfico válido: "
        f"{total_agregado}/{total_df}"
    )

    print(
        f"✓ Unidad operativa     : {unidad_operativa}"
    )

    print(
        f"✓ Unidad institucional : {unidad_institucional}"
    )


# ============================================================
# EXPORTACIÓN
# ============================================================

def exportar(
    city,
    lote,
    rutas,
    profile,
    geojson,
    campo_nombre,
    agregado,
):
    dashboard_dir = rutas["dashboard"]

    dashboard_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino = (
        dashboard_dir
        / f"mapa_{city}.html"
    )

    mapa, enlazados = construir_mapa(
        city,
        lote,
        profile,
        geojson,
        campo_nombre,
        agregado,
    )

    if enlazados != len(agregado):
        faltan = (
            len(agregado)
            - enlazados
        )

        raise AssertionError(
            "No todas las unidades cartográficas del agregado "
            "fueron enlazadas con el GeoJSON. "
            f"Faltan: {faltan}"
        )

    mapa.save(
        str(destino)
    )

    print(
        f"\nMapa exportado:\n{destino}"
    )

    return destino


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Motor 11.5 — Cartografía Territorial Universal"
        )
    )

    parser.add_argument(
        "--city",
        required=True,
        help="Territorio institucional.",
    )

    parser.add_argument(
        "--lote",
        help="Lote territorial opcional.",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("OBSERVATORIO PILATES TRANSVERSO")
    print("MOTOR 11.5.1 — CARTOGRAFÍA TERRITORIAL UNIVERSAL")
    print("=" * 60)

    rutas = city_paths(
        args.city
    )

    profile = cargar_profile(
        rutas
    )

    unidad_institucional = (
        profile["territory_unit"]
    )

    archivo = localizar_dataset(
        rutas,
        args.lote,
    )

    df = cargar_dataset(
        archivo
    )

    unidad_operativa = detectar_unidad_operativa(
        df,
        unidad_institucional,
        args.lote,
    )

    geo_path, geojson = cargar_geojson(
        rutas,
        profile,
    )

    campo_nombre = obtener_name_field(
        geojson,
        unidad_institucional,
    )

    bridge_path, bridge = cargar_bridge(
        rutas,
        unidad_operativa,
        unidad_institucional,
    )

    (
        df_cartografia,
        agregado,
    ) = preparar_agregado(
        df,
        unidad_operativa,
        unidad_institucional,
        bridge,
    )

    validar_checkpoint(
        df_cartografia,
        agregado,
        unidad_operativa,
        unidad_institucional,
    )

    print(f"\nTerritorio : {args.city}")
    print(f"Lote       : {args.lote}")
    print(f"Entrada    : {archivo}")
    print(f"GeoJSON    : {geo_path}")
    print(
        "Bridge     : "
        + (
            str(bridge_path)
            if bridge_path
            else "no requerido"
        )
    )
    print(
        f"Campo GeoJSON : {campo_nombre}"
    )
    print(
        f"Estudios      : {len(df_cartografia)}"
    )
    print(
        f"Unidades cartográficas observadas: {len(agregado)}"
    )

    print("\nAGREGADO CARTOGRÁFICO")
    print("-" * 60)

    columnas = [
        unidad_institucional,
        "estudios",
        "participacion_pct",
        "localidades_observadas",
    ]

    print(
        agregado[
            columnas
        ]
        .sort_values(
            "estudios",
            ascending=False,
        )
        .to_string(
            index=False
        )
    )

    exportar(
        args.city,
        args.lote,
        rutas,
        profile,
        geojson,
        campo_nombre,
        agregado,
    )

    print("\n" + "=" * 60)
    print("MOTOR 11.5 COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()