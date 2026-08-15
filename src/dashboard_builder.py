# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 6.2 — Dashboard Editorial
# Entrega 1/3
# ============================================================

from pathlib import Path
from datetime import datetime
import json
import sqlite3

import pandas as pd
import folium

# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"

PROCESSED = DATA / "processed"
INTELLIGENCE = DATA / "intelligence"
GEO = DATA / "geo"
DATABASE = DATA / "database"
DASHBOARD = DATA / "dashboard"

HTML_PATH = DASHBOARD / "observatorio_caba.html"

DB_PATH = DATABASE / "observatorio_pilates.db"

# ------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------

pd.options.display.max_columns = 100

# ------------------------------------------------------------
# PALETA EDITORIAL
# ------------------------------------------------------------

COLORES = {

    "negro": "#050505",
    "vino": "#220000",
    "rojo": "#8B0000",
    "rojo_intenso": "#A30000",

    "verde": "#5C7A3A",
    "arena": "#A88A4A",
    "terracota": "#8A5A3A",
    "borgona": "#6A2E2E",

    "gris": "#D9D9D9"

}

# ------------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------------

def cargar_csv(nombre):

    rutas = [

        PROCESSED / nombre,
        INTELLIGENCE / nombre,
        DATA / nombre

    ]

    for ruta in rutas:

        if ruta.exists():
            return pd.read_csv(ruta)

    raise FileNotFoundError(nombre)

# ------------------------------------------------------------
# SQLITE
# ------------------------------------------------------------

def conectar():

    return sqlite3.connect(DB_PATH)

def obtener_resumen():

    conn = conectar()

    resumen = {}

    resumen["sedes"] = pd.read_sql(
        "SELECT COUNT(*) c FROM estudios",
        conn
    ).iloc[0]["c"]

    resumen["marcas"] = pd.read_sql(
        "SELECT COUNT(*) c FROM marcas",
        conn
    ).iloc[0]["c"]

    resumen["cadenas"] = pd.read_sql(
        """
        SELECT COUNT(*) c
        FROM (
            SELECT id_marca
            FROM estudio_marca
            GROUP BY id_marca
            HAVING COUNT(*)>1
        )
        """,
        conn
    ).iloc[0]["c"]

    resumen["sedes_cadenas"] = pd.read_sql(
        """
        SELECT COUNT(*) c
        FROM estudio_marca
        WHERE id_marca IN(
            SELECT id_marca
            FROM estudio_marca
            GROUP BY id_marca
            HAVING COUNT(*)>1
        )
        """,
        conn
    ).iloc[0]["c"]

    seguidores = pd.read_sql(
        """
        SELECT AVG(seguidores_instagram) s
        FROM estudios
        WHERE seguidores_instagram IS NOT NULL
        """,
        conn
    ).iloc[0]["s"]

    resumen["seguidores_promedio"] = (
        0 if pd.isna(seguidores) else float(seguidores)
    )

    conn.close()

    return resumen

# ------------------------------------------------------------
# NORMALIZACIÓN
# ------------------------------------------------------------

def normalizar(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).strip().lower()

    reemplazos = {

        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n"

    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    alias = {

        "san nicolás": "san nicolas",
        "san nicolas": "san nicolas",

        "villa gral mitre": "villa general mitre",
        "villa general mitre": "villa general mitre",

        "parque chas": "parque chas",

        # última homologación CABA
        "la boca": "boca"

    }

    return alias.get(texto, texto)

# ------------------------------------------------------------
# GEOJSON (v6.2 definitiva)
# ------------------------------------------------------------

def preparar_geojson():

    candidatos = [

        ROOT / "data" / "reference" / "caba" / "barrios.geojson",
        ROOT / "data" / "geo" / "barrios.geojson",
        ROOT / "data" / "barrios.geojson",
        ROOT / "geo" / "barrios.geojson",
        ROOT / "barrios.geojson"

    ]

    archivo = next((r for r in candidatos if r.exists()), None)

    if archivo is None:

        print("Aviso: falta barrios.geojson")

        return None, None

    print(f"GeoJSON cargado: {archivo.relative_to(ROOT)}")

    with open(archivo, encoding="utf-8") as f:
        geo = json.load(f)

    props = geo["features"][0]["properties"]

    campo = next(
        (c for c in ["BARRIO", "barrio", "nombre"] if c in props),
        list(props.keys())[0]
    )

    for feature in geo["features"]:

        feature["properties"]["barrio_normalizado"] = normalizar(
            feature["properties"][campo]
        )

    return geo, campo
# ------------------------------------------------------------
# MAPA TERRITORIAL (v6.2 definitiva)
# ------------------------------------------------------------

def construir_mapa(df):

    mapa = folium.Map(
        location=[-34.6037, -58.3816],
        zoom_start=11,
        tiles="CartoDB positron"
    )

    geo, campo = preparar_geojson()

    if geo is None:
        folium.Marker(
            [-34.6037, -58.3816],
            tooltip="Falta barrios.geojson"
        ).add_to(mapa)
        return mapa.get_root().render()

    # -------------------------
    # Barrio -> datos
    # -------------------------

    datos = {}

    for _, fila in df.iterrows():

        datos[normalizar(fila["barrio"])] = {

            "oportunidad": float(fila["oportunidad"]),
            "categoria": fila["categoria"]

        }

    # -------------------------
    # Escala editorial
    # -------------------------

    def color(v):

        if v is None:
            return "#D9D9D9"

        if v >= 85:
            return "#4F6F2C"

        if v >= 70:
            return "#7A9A42"

        if v >= 55:
            return "#A88A4A"

        if v >= 40:
            return "#8A5A3A"

        return "#6A2E2E"

    encontrados = 0

    for feature in geo["features"]:

        clave = feature["properties"]["barrio_normalizado"]

        if clave in datos:

            valor = float(datos[clave]["oportunidad"])

            feature["properties"]["oportunidad"] = valor
            feature["properties"]["categoria"] = datos[clave]["categoria"]

            # ← Color precalculado
            feature["properties"]["fill"] = color(valor)

            encontrados += 1

        else:

            feature["properties"]["oportunidad"] = None
            feature["properties"]["categoria"] = "Sin dato"
            feature["properties"]["fill"] = "#D9D9D9"

    print(f"Barrios enlazados con GeoJSON: {encontrados}/48")

    # -------------------------
    # Dibujar polígonos
    # -------------------------

    folium.GeoJson(

        geo,

        name="Índice de Oportunidad",

        style_function=lambda feature: {

            "fillColor": feature["properties"]["fill"],
            "fillOpacity": 0.88,
            "color": "#FFFFFF",
            "weight": 1

        },

        highlight_function=lambda feature: {

            "fillOpacity": 1,
            "weight": 2,
            "color": "#111111"

        },

        tooltip=folium.GeoJsonTooltip(

            fields=[
                campo,
                "oportunidad",
                "categoria"
            ],

            aliases=[
                "Barrio",
                "Oportunidad",
                "Categoría"
            ],

            localize=True,
            sticky=True,
            labels=True

        )

    ).add_to(mapa)

    leyenda = """
    <div style="
        position:fixed;
        bottom:35px;
        left:35px;
        z-index:9999;
        background:white;
        padding:14px;
        border-radius:12px;
        box-shadow:0 4px 14px rgba(0,0,0,.25);
        font-size:13px;
        line-height:20px;">

        <b>Índice de Oportunidad</b><br>

        <span style="display:inline-block;width:15px;height:15px;background:#4F6F2C;"></span> Muy alta<br>
        <span style="display:inline-block;width:15px;height:15px;background:#7A9A42;"></span> Alta<br>
        <span style="display:inline-block;width:15px;height:15px;background:#A88A4A;"></span> Media<br>
        <span style="display:inline-block;width:15px;height:15px;background:#8A5A3A;"></span> Baja<br>
        <span style="display:inline-block;width:15px;height:15px;background:#6A2E2E;"></span> Muy baja

    </div>
    """

    mapa.get_root().html.add_child(
        folium.Element(leyenda)
    )

    return mapa.get_root().render()
# ------------------------------------------------------------
# KPIs
# ------------------------------------------------------------

def construir_kpis(resumen):

    tarjetas = [

        ("Sedes", resumen["sedes"]),
        ("Marcas", resumen["marcas"]),
        ("Cadenas", resumen["cadenas"]),
        ("Sedes de cadenas", resumen["sedes_cadenas"])

    ]

    html = '<div class="kpi-grid">'

    for titulo, valor in tarjetas:

        html += f"""

        <div class="kpi-card">

            <div class="kpi-num">
                {valor}
            </div>

            <div class="kpi-title">
                {titulo}
            </div>

        </div>

        """

    html += "</div>"

    return html

# ============================================================
# CONTINÚA EN ENTREGA 2
# ============================================================
# ============================================================
# TABLAS EDITORIALES
# ============================================================

def construir_tabla(df):

    html = ""

    top = df.sort_values(
        "oportunidad",
        ascending=False
    ).head(10)

    for i, (_, fila) in enumerate(top.iterrows(), start=1):

        cat = fila["categoria"]

        clase = {

            "Alta": "verde",
            "Media": "amarillo",
            "Baja": "naranja"

        }.get(cat, "rojo")

        html += f"""
<tr>

<td>{i}</td>

<td>{fila['barrio']}</td>

<td><b>{fila['oportunidad']:.1f}</b></td>

<td>

<span class="badge {clase}">
{cat}
</span>

</td>

</tr>
"""

    return html


# ============================================================
# HALLAZGOS EDITORIALES
# ============================================================

def construir_hallazgos(resumen, oportunidad):

    mejor = oportunidad.sort_values(
        "oportunidad",
        ascending=False
    ).iloc[0]

    peor = oportunidad.sort_values(
        "oportunidad",
        ascending=True
    ).iloc[0]

    html = f"""
<div class="hallazgos">

<div class="hallazgo">

<h3>📍 Concentración</h3>

<p>

El mercado reúne <b>{resumen['sedes']}</b> sedes distribuidas
en los 48 barrios de CABA.

</p>

</div>

<div class="hallazgo">

<h3>🚀 Mayor oportunidad</h3>

<p>

<b>{mejor['barrio']}</b> lidera el índice con

<b>{mejor['oportunidad']:.1f}</b> puntos.

</p>

</div>

<div class="hallazgo">

<h3>⚠ Mercado maduro</h3>

<p>

<b>{peor['barrio']}</b> presenta el menor margen
de expansión con

<b>{peor['oportunidad']:.1f}</b> puntos.

</p>

</div>

</div>
"""

    return html


# ============================================================
# RADAR DE EXPANSIÓN
# ============================================================

def construir_radar(df):

    top = df.sort_values(
        "oportunidad",
        ascending=False
    ).head(8)

    html = '<div class="radar-grid">'

    for _, fila in top.iterrows():

        if fila["oportunidad"] >= 85:

            estado = "Alta prioridad"
            color = "verde"

        elif fila["oportunidad"] >= 70:

            estado = "Oportunidad alta"
            color = "verde"

        elif fila["oportunidad"] >= 55:

            estado = "Seguimiento"
            color = "amarillo"

        else:

            estado = "Mercado maduro"
            color = "rojo"

        html += f"""
<div class="radar-card">

<div class="radar-header">

<h3>{fila['barrio']}</h3>

<span class="badge {color}">
{estado}
</span>

</div>

<div class="radar-score">

{fila['oportunidad']:.1f}

</div>

<p>

Categoría territorial:
<b>{fila['categoria']}</b>

</p>

</div>
"""

    html += "</div>"

    return html


# ============================================================
# METODOLOGÍA
# ============================================================

def construir_metodologia():

    return """
<div class="metodologia">

<p>

El Índice de Oportunidad sintetiza múltiples variables
territoriales para identificar barrios con mayor potencial
de crecimiento.

</p>

<ul>

<li>Concentración territorial.</li>

<li>Fortaleza digital.</li>

<li>Distribución de marcas.</li>

<li>Presencia de cadenas.</li>

<li>Base Maestra Editorial.</li>

</ul>

<p>

Todas las decisiones metodológicas quedan documentadas
en los DM-001 a DM-009.

</p>

</div>
"""


# ============================================================
# MOTOR 7 (PREPARACIÓN)
# ============================================================

def construir_intake():

    return """
<div class="intake-box">

<h3>¿Tu estudio todavía no aparece?</h3>

<p>

El Observatorio permitirá incorporar nuevas sedes mediante
validación editorial.

</p>

<div class="timeline">

<div class="step">Solicitud</div>

<div class="step">Curación</div>

<div class="step">Marca</div>

<div class="step">SQLite</div>

<div class="step">Dashboard</div>

</div>

<button class="btn-disabled">

Motor 7 · Próximamente

</button>

</div>
"""


# ============================================================
# HELPERS HTML
# ============================================================

def bloque_panel(titulo, contenido):

    return f"""
<div class="panel">

<h2>{titulo}</h2>

{contenido}

</div>
"""


# ============================================================
# CSS EDITORIAL COMPLEMENTARIO
# ============================================================

CSS_EDITORIAL = """

.kpi-grid{

display:grid;

grid-template-columns:repeat(4,1fr);

gap:16px;

margin-bottom:32px;

}

.kpi-card{

background:white;

padding:22px;

border-radius:16px;

text-align:center;

box-shadow:0 8px 22px rgba(0,0,0,.08);

border-top:3px solid var(--rojo-intenso);

transition:transform .2s ease, box-shadow .2s ease;

}

.kpi-card:hover{

transform:translateY(-4px);

box-shadow:0 12px 28px rgba(0,0,0,.12);

}

.kpi-num{

font-size:40px;

font-weight:700;

color:var(--rojo);

}

.kpi-title{

margin-top:8px;

color:var(--texto-suave);

}

.radar-grid{

display:grid;

grid-template-columns:repeat(auto-fit,minmax(230px,1fr));

gap:18px;

}

.radar-card{

background:white;

border-radius:16px;

padding:20px;

box-shadow:0 8px 22px rgba(0,0,0,.08);

transition:transform .2s ease;

}

.radar-card:hover{

transform:translateY(-4px);

}

.radar-header{

display:flex;

justify-content:space-between;

align-items:center;

margin-bottom:14px;

gap:10px;

}

.radar-header h3{

margin:0;

font-size:18px;

}

.radar-score{

font-size:38px;

font-weight:700;

color:var(--rojo);

margin-bottom:8px;

}

.intake-box{

background:linear-gradient(180deg,#220000,#050505);

color:white;

padding:24px;

border-radius:16px;

}

.timeline{

display:flex;

justify-content:space-between;

gap:8px;

margin:18px 0;

flex-wrap:wrap;

}

.step{

background:rgba(255,255,255,.08);

padding:10px 14px;

border-radius:10px;

font-size:12px;

}

.btn-disabled{

background:#444;

border:none;

padding:12px 20px;

border-radius:10px;

color:white;

cursor:not-allowed;

font-weight:600;

}

.metodologia{

line-height:1.8;

}

.metodologia ul{

padding-left:22px;

}

"""

# ============================================================
# CONTINÚA EN ENTREGA 3
# ============================================================
# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================

def construir_dashboard():

    resumen = obtener_resumen()
    oportunidad = cargar_csv("oportunidad_barrios.csv")

    mapa = construir_mapa(oportunidad)

    fecha = datetime.now().strftime("%d/%m/%Y")

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

<span>CABA · v1.0</span>

</div>

<div class="hero-body">

<div class="hero-logo">

<div class="logo-box">

<span class="logo-main">

TRANSVERSO

</span>

<span class="logo-sub">

Observatorio Pilates

</span>

</div>

</div>

<div class="hero-text">

<h1>

Observatorio Pilates Transverso

</h1>

<p>

Inteligencia territorial del ecosistema Pilates.

</p>

<div class="hero-meta">

399 sedes · 369 marcas · 30 cadenas

</div>

</div>

</div>

</header>

{construir_kpis(resumen)}

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

{bloque_panel("Motor 7 — Incorporación Editorial", construir_intake())}

<footer class="footer">

<strong>Observatorio Pilates Transverso</strong><br>

CABA v1.0 · Base Maestra Editorial<br>

399 sedes · 369 marcas · 30 cadenas

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
    print("MOTOR 6.2 — DASHBOARD EDITORIAL")
    print("="*70)

    construir_dashboard()

    print("\nMapa territorial: OK")
    print("\nMotor 6.2 completado.")


if __name__ == "__main__":
    main()