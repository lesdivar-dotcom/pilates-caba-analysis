# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.2 — Dashboard Editorial Vivo
# Archivo: dashboard_builder.py
#
# Entrega 1/3
# ============================================================

from pathlib import Path
from datetime import datetime
import sqlite3
import json

import pandas as pd


# ============================================================
# RUTAS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

PROCESSED = ROOT / "data" / "processed"
INTELLIGENCE = ROOT / "data" / "intelligence"
REFERENCE = ROOT / "data" / "reference"
DASHBOARD = ROOT / "data" / "dashboard"

HTML_PATH = DASHBOARD / "observatorio_caba.html"

DB_PATH = ROOT / "data" / "database" / "observatorio_pilates.db"


# ============================================================
# CARGA CSV
# ============================================================
def cargar_csv(nombre):

    # oportunidad_barrios siempre vive en data/intelligence
    if nombre == "oportunidad_barrios.csv":
        return pd.read_csv(INTELLIGENCE / nombre)

    return pd.read_csv(PROCESSED / nombre)

# ============================================================
# RESUMEN
# ============================================================

def obtener_resumen():

    conn = sqlite3.connect(DB_PATH)

    resumen = pd.read_sql_query(

        """
        SELECT
            COUNT(*) AS estudios
        FROM estudios
        """,

        conn

    )

    conn.close()

    return resumen.iloc[0]


# ============================================================
# ESTADO EDITORIAL (Motor 7.2)
# ============================================================

def obtener_estado_observatorio():

    conn = sqlite3.connect(DB_PATH)

    estudios = conn.execute(
        "SELECT COUNT(*) FROM estudios"
    ).fetchone()[0]

    marcas = conn.execute(
        "SELECT COUNT(*) FROM marcas"
    ).fetchone()[0]

    cadenas = conn.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT id_marca
            FROM estudio_marca
            GROUP BY id_marca
            HAVING COUNT(*)>1
        )
    """).fetchone()[0]

    ultimo = conn.execute("""
        SELECT
            id_estudio,
            nombre_del_estudio
        FROM estudios
        ORDER BY CAST(SUBSTR(id_estudio,5) AS INTEGER) DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    return {

        "estudios": estudios,
        "marcas": marcas,
        "cadenas": cadenas,

        "ultimo_estudio": ultimo[0],
        "ultimo_nombre": ultimo[1],

        "ultimo_draft": f"DRF-{estudios-398:06d}"

    }


# ============================================================
# CSS EDITORIAL
# ============================================================

CSS_EDITORIAL = """
.kpi-grid{

display:grid;
grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
gap:16px;

}

.kpi{

background:white;
padding:20px;
border-radius:14px;
text-align:center;
box-shadow:0 8px 22px rgba(0,0,0,.08);
border-top:3px solid var(--rojo-intenso);

}

.kpi-num{

font-size:34px;
font-weight:700;
color:var(--vino);

}

.kpi-label{

margin-top:8px;
color:var(--texto-suave);

}
"""


# ============================================================
# COMPONENTES AUXILIARES
# ============================================================

def bloque_panel(titulo, contenido):

    return f"""
<div class="panel">

<h2>{titulo}</h2>

{contenido}

</div>
"""


# ============================================================
# KPIs
# ============================================================

def construir_kpis(resumen):

    estado = obtener_estado_observatorio()

    return f"""
<div class="kpi-grid">

<div class="kpi">

<div class="kpi-num">{estado["estudios"]}</div>

<div class="kpi-label">Estudios</div>

</div>

<div class="kpi">

<div class="kpi-num">{estado["marcas"]}</div>

<div class="kpi-label">Marcas</div>

</div>

<div class="kpi">

<div class="kpi-num">{estado["cadenas"]}</div>

<div class="kpi-label">Cadenas</div>

</div>

<div class="kpi">

<div class="kpi-num">48</div>

<div class="kpi-label">Barrios</div>

</div>

</div>
"""


# ============================================================
# TABLA TOP BARRIOS
# ============================================================

def construir_tabla(df):

    html = ""

    for _, fila in df.head(10).iterrows():

        categoria = fila["categoria"].lower()

        color = {

            "alta": "verde",
            "media": "amarillo",
            "baja": "rojo"

        }.get(categoria, "naranja")

        html += f"""
<tr>

<td>{fila["ranking"]}</td>

<td>{fila["barrio"]}</td>

<td>{fila["oportunidad"]:.1f}</td>

<td><span class="badge {color}">{fila["categoria"]}</span></td>

</tr>
"""

    return html


# ============================================================
# HALLAZGOS
# ============================================================

def construir_hallazgos(resumen, oportunidad):

    estado = obtener_estado_observatorio()

    top = oportunidad.iloc[0]["barrio"]

    return f"""
<div class="hallazgos">

<div class="hallazgo">

<b>Liderazgo territorial</b><br><br>

{top} continúa encabezando el Índice de Oportunidad.

</div>

<div class="hallazgo">

<b>Mercado actual</b><br><br>

{estado["estudios"]} estudios distribuidos en los 48 barrios oficiales.

</div>

<div class="hallazgo">

<b>Estructura competitiva</b><br><br>

{estado["marcas"]} marcas con {estado["cadenas"]} cadenas multisede.

</div>

</div>
"""


# ============================================================
# METODOLOGÍA
# ============================================================

def construir_metodologia():

    return """
<p>

El Observatorio integra las decisiones metodológicas DM-001 a DM-017.

El Índice de Oportunidad combina saturación territorial, población,
fortaleza digital y concentración de marcas.

Todos los indicadores institucionales se leen directamente desde SQLite.

</p>
"""


# ============================================================
# RADAR
# ============================================================

def construir_radar(oportunidad):

    return """
<p>

Cada barrio posee una ficha individual generada automáticamente.

</p>

<code>data/intelligence/radar_expansion/</code>
"""


# ============================================================
# MOTOR 7 — INCORPORACIÓN EDITORIAL
# ============================================================
def construir_intake():

    estado = obtener_estado_observatorio()

    return f"""
<div class="hallazgos">

    <div class="hallazgo">

        <b>Incorporación editorial activa</b><br><br>

        El Observatorio ya permite incorporar estudios nuevos mediante el flujo editorial oficial.

        <br><br>

        <span style="color:#D0D0D0">
        Intake → Validación → Alias → Duplicate Guard → Publicación.
        </span>

    </div>

    <div class="hallazgo">

        <b>¿Qué sucede cuando se incorpora un estudio?</b><br><br>

        ✓ Validación editorial.<br>
        ✓ Detector de marca.<br>
        ✓ Duplicate Guard.<br>
        ✓ Publicación en la Base Maestra.<br>
        ✓ Actualización automática de SQLite, Dashboard y PDF.

    </div>

    <div class="hallazgo">

        <b>Estado actual</b><br><br>

        {estado["estudios"]} estudios publicados.<br>
        {estado["marcas"]} marcas consolidadas.<br>
        {estado["cadenas"]} cadenas multisede.

    </div>

</div>

<div style="
margin-top:18px;
padding:20px;
border:1px solid #E5E7EB;
border-radius:12px;
background:#FAFAFA;
color:#4A5560;
line-height:1.8;">

<b>Incorporación de nuevos estudios</b><br><br>

El Observatorio incorpora nuevas sedes mediante un proceso editorial con trazabilidad completa.

Cada alta atraviesa cinco etapas:

<ol style="margin-top:10px;margin-bottom:10px;">
<li>Registro del estudio.</li>
<li>Validación editorial.</li>
<li>Detección automática de marca y sedes existentes.</li>
<li>Control de duplicados.</li>
<li>Publicación en la Base Maestra.</li>
</ol>

<text highlight inline>Todo estudio publicado actualiza automáticamente la Base Maestra, SQLite, el Dashboard y el Intelligence Report.</text>

</div>
"""
# ============================================================
# MAPA TERRITORIAL (Motor 6.2 congelado)
# ============================================================

import folium


def color_oportunidad(valor, minimo, maximo):
    """
    Paleta institucional Transverso.
    Mantener congelada.
    """

    if maximo == minimo:
        return "#A30000"

    t = (valor - minimo) / (maximo - minimo)

    if t >= 0.75:
        return "#5C7A3A"      # verde

    elif t >= 0.50:
        return "#A88A4A"      # arena

    elif t >= 0.25:
        return "#8A5A3A"      # terracota

    else:
        return "#6A2E2E"      # borgoña


# ------------------------------------------------------------
# Construcción del mapa
# ------------------------------------------------------------

def construir_mapa(oportunidad):

    geojson_path = REFERENCE / "caba" / "barrios.geojson"

    if not geojson_path.exists():

        print("Aviso: falta barrios.geojson")

        return """
        <div style="
            height:420px;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#EFEFEF;
            border-radius:12px;
            color:#666;">
            GeoJSON no encontrado.
        </div>
        """

    print(f"GeoJSON cargado: {geojson_path.relative_to(ROOT)}")

    with open(geojson_path, encoding="utf-8") as f:
        geo = json.load(f)

    # --------------------------------------------------------
    # Índice por barrio
    # --------------------------------------------------------

    indice = {}

    for _, fila in oportunidad.iterrows():

        indice[str(fila["barrio"]).strip().lower()] = {

            "puntaje": float(fila["oportunidad"]),
            "categoria": fila["categoria"]

        }

    minimo = oportunidad["oportunidad"].min()
    maximo = oportunidad["oportunidad"].max()

    # --------------------------------------------------------
    # Mapa base
    # --------------------------------------------------------

    mapa = folium.Map(

        location=[-34.61, -58.44],

        zoom_start=11,

        tiles="CartoDB positron"

    )

    enlazados = 0

    # --------------------------------------------------------
    # Función de estilo
    # --------------------------------------------------------

    def estilo(feature):

        nonlocal enlazados

        nombre = (
            feature["properties"]
            .get("barrio")
            or feature["properties"].get("nombre")
            or feature["properties"].get("NOMBRE")
            or ""
        )

        clave = nombre.strip().lower()

        if clave in indice:

            enlazados += 1

            valor = indice[clave]["puntaje"]

            color = color_oportunidad(
                valor,
                minimo,
                maximo
            )

            return {

                "fillColor": color,

                "color": "#FFFFFF",

                "weight": 1,

                "fillOpacity": 0.78

            }

        return {

            "fillColor": "#DDDDDD",

            "color": "#FFFFFF",

            "weight": 1,

            "fillOpacity": 0.35

        }

    # --------------------------------------------------------
    # Tooltip
    # --------------------------------------------------------

    def tooltip(feature):

        nombre = (
            feature["properties"]
            .get("barrio")
            or feature["properties"].get("nombre")
            or feature["properties"].get("NOMBRE")
            or "Sin nombre"
        )

        clave = nombre.strip().lower()

        if clave in indice:

            dato = indice[clave]

            return (
                f"<b>{nombre}</b><br>"
                f"Oportunidad: {dato['puntaje']:.1f}<br>"
                f"Categoría: {dato['categoria']}"
            )

        return f"<b>{nombre}</b>"

    # --------------------------------------------------------
    # Dibujar barrios
    # --------------------------------------------------------

    for feature in geo["features"]:

        folium.GeoJson(

            feature,

            style_function=lambda f, feat=feature: estilo(feat),

            tooltip=folium.Tooltip(
                tooltip(feature),
                sticky=True
            )

        ).add_to(mapa)

    print(
        f"Barrios enlazados con GeoJSON: {enlazados}/48"
    )

    # --------------------------------------------------------
    # Leyenda institucional
    # --------------------------------------------------------

    leyenda = """
    <div style="
    position:fixed;
    bottom:28px;
    left:28px;
    z-index:9999;
    background:white;
    padding:12px 14px;
    border-radius:10px;
    box-shadow:0 4px 12px rgba(0,0,0,.18);
    font-size:12px;
    line-height:1.6;
    min-width:165px;
    ">

    <b>Índice de Oportunidad</b><br>

    <span style="color:#5C7A3A;">■</span> Alta<br>
    <span style="color:#A88A4A;">■</span> Media alta<br>
    <span style="color:#8A5A3A;">■</span> Media baja<br>
    <span style="color:#6A2E2E;">■</span> Baja

    </div>
    """

    mapa.get_root().html.add_child(
        folium.Element(leyenda)
    )

    return mapa.get_root().render()
# ============================================================
# DASHBOARD PRINCIPAL (Motor 7.2)
# ============================================================

def construir_dashboard():

    resumen = obtener_resumen()
    oportunidad = cargar_csv("oportunidad_barrios.csv")

    mapa = construir_mapa(oportunidad)

    fecha = datetime.now().strftime("%d/%m/%Y")
    estado = obtener_estado_observatorio()

    html = f"""<!DOCTYPE html>
<html lang="es">

<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Observatorio Pilates Transverso</title>

<style>

:root{{

--negro:#050505;
--vino:#220000;
--rojo:#8B0000;
--rojo-intenso:#A30000;

--fondo:#F7F9FB;
--panel:#FFFFFF;

--texto:#23313D;
--texto-suave:#6B7A86;

--verde:#5C7A3A;
--arena:#A88A4A;
--terracota:#8A5A3A;
--borgona:#6A2E2E;

}}

*{{box-sizing:border-box;}}

body{{

margin:0;
font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;
background:var(--fondo);
color:var(--texto);

}}

main{{

max-width:1450px;
margin:auto;
padding:24px;

}}

.hero{{

background:linear-gradient(90deg,#050505,#8B0000);
color:white;
padding:20px 36px 24px;
border-radius:18px;
margin-bottom:26px;

}}

.hero-top{{

display:flex;
justify-content:space-between;
font-size:12px;
opacity:.86;

}}

.hero-body{{

display:flex;
align-items:center;
gap:24px;
margin-top:14px;
flex-wrap:wrap;

}}

.logo-box{{

border:1px solid rgba(255,255,255,.35);
padding:14px 18px;
border-radius:10px;

}}

.logo-main{{

display:block;
font-weight:700;
letter-spacing:2px;
font-size:20px;

}}

.logo-sub{{

display:block;
font-size:12px;
opacity:.82;
margin-top:4px;

}}

.hero-text{{

flex:1;

}}

.hero h1{{

margin:0;
font-size:34px;

}}

.hero p{{

margin:10px 0;
opacity:.94;

}}

.hero-meta{{

font-size:14px;
color:#E6E6E6;

}}

.panel{{

background:white;
padding:22px;
border-radius:16px;
box-shadow:0 8px 22px rgba(0,0,0,.08);
margin-bottom:26px;

}}

.grid{{

display:grid;
grid-template-columns:1fr 1.35fr;
gap:24px;

}}

table{{

width:100%;
border-collapse:collapse;

}}

th,td{{

padding:12px;
border-bottom:1px solid #EEE;
text-align:left;

}}

th{{

background:#FAFAFA;
font-weight:600;

}}

.badge{{

padding:5px 12px;
border-radius:18px;
color:white;
font-size:12px;
display:inline-block;

}}

.verde{{background:var(--verde);}}
.amarillo{{background:var(--arena);color:#222;}}
.naranja{{background:var(--terracota);}}
.rojo{{background:var(--borgona);}}

.hallazgos{{

display:grid;
grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:18px;

}}

.hallazgo{{

background:linear-gradient(180deg,var(--vino),var(--negro));
padding:22px;
border-left:4px solid var(--rojo-intenso);
border-radius:14px;
color:white;
line-height:1.6;

}}

{CSS_EDITORIAL}

.footer{{

margin-top:40px;
text-align:center;
color:#666;
font-size:13px;
padding:28px;

}}

@media(max-width:1000px){{

.grid{{grid-template-columns:1fr;}}
.kpi-grid{{grid-template-columns:repeat(2,1fr);}}
.hero h1{{font-size:28px;}}

}}

@media(max-width:650px){{

.kpi-grid{{grid-template-columns:1fr;}}
.hero-body{{flex-direction:column;align-items:flex-start;}}

}}

</style>

</head>

<body>

<main>

<header class="hero">

<div class="hero-top">

<span>Actualizado automáticamente · {fecha}</span>

<span>CABA · v1.0-caba-rc1</span>

</div>

<div class="hero-body">

<div class="hero-logo">

<div class="logo-box">

<span class="logo-main">TRANSVERSO</span>

<span class="logo-sub">Observatorio Pilates</span>

</div>

</div>

<div class="hero-text">

<h1>Observatorio Pilates Transverso</h1>

<p>Inteligencia territorial del ecosistema Pilates.</p>

<div class="hero-meta">

<b>{estado["estudios"]}</b> estudios ·
<b>{estado["marcas"]}</b> marcas ·
<b>{estado["cadenas"]}</b> cadenas multisede

</div>

</div>

</div>

</header>

{construir_kpis(resumen)}

{bloque_panel("Estado del Observatorio", f'''
<div class="hallazgos">

<div class="hallazgo">

<b>Última publicación</b><br><br>

Draft: {estado["ultimo_draft"]}<br>
Estudio: {estado["ultimo_estudio"]}<br>
Marca: {estado["ultimo_nombre"]}<br><br>

<span style="color:#D0D0D0">
Pipeline editorial operativo.
</span>

</div>

<div class="hallazgo">

<b>Base institucional</b><br><br>

Estudios: {estado["estudios"]}<br>
Marcas: {estado["marcas"]}<br>
Cadenas: {estado["cadenas"]}<br>
Ciudad: CABA<br>
Versión: v1.0-caba-rc1

</div>

</div>
''')}

{bloque_panel("Hallazgos del Observatorio", construir_hallazgos(resumen, oportunidad))}

<div class="grid">

{bloque_panel("Top 10 Barrios con Mayor Oportunidad", f'''
<table>

<thead>

<tr>

<th>#</th>
<th>Barrio</th>
<th>Puntaje</th>
<th>Categoría</th>

</tr>

</thead>

<tbody>

{construir_tabla(oportunidad)}

</tbody>

</table>
''')}

{bloque_panel("Mapa Territorial", mapa)}

</div>

{bloque_panel("Metodología", construir_metodologia())}

{bloque_panel("Radar de Expansión", construir_radar(oportunidad))}

{bloque_panel("Incorporación Editorial", construir_intake())}

<footer class="footer">

<strong>Observatorio Pilates Transverso</strong><br>

Dashboard Editorial Vivo · v1.0-caba-rc1<br>

{estado["estudios"]} estudios · {estado["marcas"]} marcas · {estado["cadenas"]} cadenas multisede

</footer>

</main>

</body>

</html>
"""

    DASHBOARD.mkdir(parents=True, exist_ok=True)

    HTML_PATH.write_text(
        html,
        encoding="utf-8"
    )

    print("\nDashboard generado:\n")
    print(HTML_PATH)


# ============================================================
# MAIN
# ============================================================

def main():

    print("="*70)
    print("MOTOR 7.2 — DASHBOARD EDITORIAL VIVO")
    print("="*70)

    construir_dashboard()

    print("\nMapa territorial: OK")

    print("\nMotor 7.2 completado.")


if __name__ == "__main__":

    main()