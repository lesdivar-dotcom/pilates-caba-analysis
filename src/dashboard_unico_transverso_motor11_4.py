# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# MOTOR 11 — DASHBOARD ÚNICO
# ============================================================
#
# Prototipo consolidado:
# - estética del Observatorio CABA
# - paleta negro / borgoña / rojo / rosa
# - buscador de estudios
# - filtro territorial
# - porcentajes recalculados sobre el territorio seleccionado
# - comparativo territorial
# - mapa embebido si existe mapa_{city}.html
# - editor de estudios
# - alta manual de estudios
# - persistencia local en navegador (localStorage)
# - exportación CSV de cambios
#
# Uso:
#   python src/dashboard_unico.py --city buenos_aires_provincia --lote ba_norte
#
# El motor NO vuelve a descubrir estudios.
# Consume el dataset provincial ya integrado.
# ============================================================

import argparse
import html
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from city_config import city_paths


ROOT = Path(__file__).resolve().parents[1]

PALETA = {
    # --------------------------------------------------------
    # Hero / marca Transverso
    # --------------------------------------------------------
    "hero_black": "#050505",
    "hero_red": "#8B0000",

    # --------------------------------------------------------
    # Editorial
    # --------------------------------------------------------
    "vino": "#220000",
    "terracota": "#8A5A3A",
    "arena": "#A88A4A",
    "verde": "#5C7A3A",
    "gris": "#ECECEC",

    # --------------------------------------------------------
    # Fondos
    # --------------------------------------------------------
    "fondo": "#F7F9FB",
    "panel": "#FFFFFF",

    # --------------------------------------------------------
    # Texto
    # --------------------------------------------------------
    "texto": "#23313D",
    "texto_suave": "#6B7A86",
    "texto_claro": "#FFFFFF",

    # --------------------------------------------------------
    # Compatibilidad
    # --------------------------------------------------------
    "negro": "#050505",
    "rojo": "#8B0000",
    "rojo_intenso": "#A30000",
    "borgona": "#6A2E2E",
}



def localizar_dataset(city: str, lote: str | None) -> Path:
    rutas = city_paths(city)
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
        base / "processed" / "estudios_features.csv",
    ])

    for p in candidatos:
        if p.exists():
            return p

    raise FileNotFoundError(
        "No se encontró un dataset utilizable.\n"
        + "\n".join(str(p) for p in candidatos)
    )


def localizar_mapa(city: str) -> Path | None:
    rutas = city_paths(city)
    candidatos = [
        rutas["dashboard"] / f"mapa_{city}.html",
    ]
    return next((p for p in candidatos if p.exists()), None)


def cargar_profile(city: str) -> dict:
    rutas = city_paths(city)
    p = rutas["reference"] / "territory_profile.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))

    return {
        "territory_name": city.replace("_", " ").title(),
        "display_name": city.replace("_", " ").title(),
        "country": "Argentina",
        "unit": "localidad",
        "territory_unit": "localidad",
        "version": "1.0",
    }


def _serie_util(df: pd.DataFrame, columna: str) -> bool:
    if columna not in df.columns:
        return False

    serie = (
        df[columna]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return serie.ne("").any()


def detectar_unidad(df: pd.DataFrame, profile: dict, lote: str | None = None) -> tuple[str, str]:
    """
    Devuelve (unidad_operativa, unidad_institucional).

    - territory_profile.json mantiene la unidad institucional.
    - un lote puede trabajar a una granularidad operativa más fina
      si esa columna existe y contiene datos reales.
    - nunca crea silenciosamente una columna territorial vacía.
    """

    institucional = (
        profile.get("territory_unit")
        or profile.get("unit")
        or "territorio"
    )

    if lote:
        candidatos = [
            "localidad",
            institucional,
            "municipio",
            "barrio",
            "comuna",
            "zona",
        ]
    else:
        candidatos = [
            institucional,
            "municipio",
            "barrio",
            "localidad",
            "comuna",
            "zona",
        ]

    vistos = set()

    for columna in candidatos:
        if not columna or columna in vistos:
            continue

        vistos.add(columna)

        if _serie_util(df, columna):
            return columna, institucional

    raise ValueError(
        "No existe una unidad territorial utilizable.\n"
        f"Unidad institucional: {institucional!r}\n"
        f"Columnas disponibles: {list(df.columns)}"
    )


def etiqueta_unidad(unidad: str) -> tuple[str, str]:
    etiquetas = {
        "barrio": ("Barrio", "Barrios"),
        "localidad": ("Localidad", "Localidades"),
        "municipio": ("Municipio", "Municipios"),
        "comuna": ("Comuna", "Comunas"),
        "zona": ("Zona", "Zonas"),
        "territorio": ("Territorio", "Territorios"),
    }

    return etiquetas.get(
        unidad,
        (unidad.capitalize(), unidad.capitalize() + "s"),
    )


def preparar_df(df: pd.DataFrame, unidad: str) -> pd.DataFrame:
    df = df.copy()

    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].fillna("").astype(str)

    if "id_estudio" not in df.columns:
        raise KeyError(
            "El Dashboard exige la columna institucional 'id_estudio'."
        )

    if "nombre_del_estudio" not in df.columns:
        raise KeyError(
            "El Dashboard exige la columna 'nombre_del_estudio'."
        )

    if unidad not in df.columns:
        raise KeyError(
            f"La unidad territorial operativa '{unidad}' no existe."
        )

    if "estado" not in df.columns:
        df["estado"] = ""

    for c in [
        "direccion", "telefono", "email",
        "instagram", "web", "app",
        "observaciones", "fuente_de_datos",
        "fecha_recoleccion",
    ]:
        if c not in df.columns:
            df[c] = ""

    return df


def localizar_candidatos_revision(city: str, lote: str | None) -> list[Path]:
    rutas = city_paths(city)
    base = rutas["base"]
    candidatos = []

    if lote:
        candidatos.extend([
            base / "consolidated" / lote / "candidatos_revision.csv",
            base / "enrichment" / lote / "candidatos_duplicados.csv",
            base / "analysis" / lote / "candidatos_revision.csv",
        ])

    candidatos.append(
        base / "provincial" / "candidatos_revision_provincial.csv"
    )

    return [p for p in candidatos if p.exists()]


def aplicar_estado_editorial(df: pd.DataFrame, archivos: list[Path]) -> pd.DataFrame:
    df = df.copy()
    ids_revision = set()

    for archivo in archivos:
        try:
            revision = pd.read_csv(archivo, encoding="utf-8-sig")
        except Exception:
            continue

        if "id_estudio" in revision.columns:
            ids_revision.update(
                revision["id_estudio"]
                .fillna("")
                .astype(str)
                .str.strip()
                .loc[lambda x: x.ne("")]
                .tolist()
            )

    estado = (
        df["estado"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    normalizados = {
        "verificado": "Verificado",
        "pendiente": "Pendiente",
        "revision": "Revisión",
        "revisión": "Revisión",
    }

    df["estado"] = [
        "Revisión"
        if str(id_estudio).strip() in ids_revision
        else normalizados.get(valor.lower(), "Pendiente")
        for id_estudio, valor in zip(df["id_estudio"], estado)
    ]

    return df


def serializar(df: pd.DataFrame) -> str:
    records = df.fillna("").to_dict(orient="records")
    return json.dumps(records, ensure_ascii=False)


def escape_js_string(value: str) -> str:
    # JSON + HTML script safety: prevents an embedded </script> from
    # terminating the outer dashboard script tag.
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def generar_html(city: str, lote: str | None, df: pd.DataFrame,
                  profile: dict, unidad: str, mapa_html: str | None) -> str:

    records_json = serializar(df)
    title = profile.get("territory_name") or profile.get("display_name") or city
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    unidad_singular, unidad_plural = etiqueta_unidad(unidad)
    unidad_institucional = (
        profile.get("territory_unit")
        or profile.get("unit")
        or unidad
    )

    mapa_doc = ""
    if mapa_html:
        # El mapa generado por Folium ya es un documento HTML.
        # Se muestra dentro de un iframe usando srcdoc.
        mapa_doc = (
            '<iframe id="mapFrame" class="map-frame" '
            'sandbox="allow-scripts allow-same-origin"></iframe>'
        )
    else:
        mapa_doc = """
        <div class="map-empty">
            <b>Mapa territorial</b>
            <span>No hay mapa HTML generado todavía.</span>
            <small>El dashboard sigue funcionando sin él.</small>
        </div>
        """

    mapa_srcdoc = escape_js_string(mapa_html or "")

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Observatorio Pilates Transverso — {html.escape(title)}</title>

<style>
:root {{
  --hero-black: {PALETA["hero_black"]};
  --hero-red: {PALETA["hero_red"]};
  --vino: {PALETA["vino"]};
  --terracota: {PALETA["terracota"]};
  --arena: {PALETA["arena"]};
  --verde: {PALETA["verde"]};
  --gris: {PALETA["gris"]};
  --fondo: {PALETA["fondo"]};
  --panel: {PALETA["panel"]};
  --texto: {PALETA["texto"]};
  --texto-suave: {PALETA["texto_suave"]};
  --texto-claro: {PALETA["texto_claro"]};
  --negro: {PALETA["negro"]};
  --rojo: {PALETA["rojo"]};
  --rojo-intenso: {PALETA["rojo_intenso"]};
  --borgona: {PALETA["borgona"]};
  --borde: #3B2525;
}}

* {{ box-sizing:border-box; }}

body {{
  margin:0;
  background:var(--fondo);
  color:var(--texto);
  font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;
}}

button,input,select,textarea {{ font:inherit; }}

button {{
  cursor:pointer;
}}

.app {{
  display:grid;
  grid-template-columns:225px 1fr;
  min-height:100vh;
}}

.sidebar {{
  background:linear-gradient(180deg,#050505,#220000);
  border-right:1px solid var(--borde);
  padding:18px 10px;
}}

.brand {{
  border:0;
  background:linear-gradient(180deg,#220000,#050505);
  border-radius:10px;
  padding:16px 18px;
  margin-bottom:20px;
}}

.brand-main {{
  font-weight:800;
  letter-spacing:2px;
  font-size:21px;
}}

.brand-sub {{
  color:var(--gris);
  font-size:12px;
  margin-top:4px;
}}

.nav button {{
  width:100%;
  text-align:left;
  color:#FFFFFF;
  background:transparent;
  border:0;
  border-radius:8px;
  padding:12px 13px;
  margin:3px 0;
}}

.nav button:hover,
.nav button.active {{
  background:linear-gradient(90deg,#6A2E2E,#220000);
}}

.territory-card {{
  margin-top:28px;
  border-top:1px solid var(--borde);
  padding:18px 12px;
}}

.territory-card b {{
  display:block;
  font-size:16px;
  margin:8px 0 14px;
}}

.territory-line {{
  display:flex;
  justify-content:space-between;
  padding:4px 0;
  color:var(--texto-suave);
  font-size:13px;
}}

.main {{
  padding:24px;
  min-width:0;
}}

.hero {{
  background:linear-gradient(90deg,var(--negro),var(--rojo));
  color:#FFFFFF;
  border-radius:18px;
  padding:20px 36px 26px;
  border:0;
  margin-bottom:22px;
  box-shadow:0 8px 22px rgba(0,0,0,.10);
}}

.hero-top {{
  display:flex;
  justify-content:space-between;
  color:#ECECEC;
  font-size:12px;
}}

.hero-body {{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:20px;
  margin-top:22px;
}}

.hero h1 {{
  font-size:36px;
  margin:0;
  letter-spacing:-1px;
}}

.hero p {{
  margin:7px 0 13px;
  color:#FFFFFF;
  font-size:16px;
}}

.hero h1, .hero-meta {{
  color:#FFFFFF;
}}

.kpi .value {{color:var(--vino);}}
.kpi .label, .card h2, .legend-row, th, td {{color:var(--texto);}}

.hero-meta {{
  font-size:14px;
}}

.toolbar {{
  display:flex;
  gap:8px;
  align-items:center;
  margin-bottom:15px;
}}

.search {{
  flex:1;
  background:#FFFFFF;
  color:var(--texto);
  border:1px solid #D8DDE2;
  border-radius:9px;
  padding:11px 13px;
}}

.select {{
  background:#FFFFFF;
  color:var(--texto);
  border:1px solid #D8DDE2;
  border-radius:9px;
  padding:11px 12px;
}}

.btn {{
  border:1px solid #D8DDE2;
  background:#FFFFFF;
  color:var(--texto);
  border-radius:9px;
  padding:10px 13px;
}}

.btn.primary {{
  background:var(--vino);
  color:#FFFFFF;
  border-color:var(--vino);
}}

.btn.soft {{
  background:#6A2E2E;
}}

.kpis {{
  display:grid;
  grid-template-columns:repeat(5,minmax(150px,1fr));
  gap:10px;
  margin-bottom:12px;
}}

.kpi {{
  background:#FFFFFF;
  border:0;
  box-shadow:0 8px 22px rgba(0,0,0,.08);
  border-top:3px solid var(--borgona);
  border-radius:14px;
  padding:19px 20px;
}}

.kpi .value {{
  font-size:31px;
  font-weight:700;
  color:var(--vino);
}}

.kpi .label {{
  margin-top:4px;
  font-size:13px;
  color:var(--texto);
}}

.kpi .sub {{
  color:#6B7A86;
  font-size:11px;
  margin-top:5px;
}}

.grid {{
  display:grid;
  grid-template-columns:1.05fr 1.45fr 1fr;
  gap:10px;
}}

.card {{
  background:#FFFFFF;
  border:0;
  box-shadow:0 8px 22px rgba(0,0,0,.08);
  border-radius:16px;
  padding:22px;
}}

.card h2 {{
  font-size:18px;
  margin:0 0 17px;
  letter-spacing:0;
  color:var(--texto);
}}

.donut-wrap {{
  display:flex;
  align-items:center;
  gap:18px;
}}

.donut {{
  width:150px;
  height:150px;
  border-radius:50%;
  position:relative;
  background:conic-gradient(#5C7A3A 0deg,#5C7A3A 120deg,#A88A4A 120deg,#A88A4A 190deg,#8A5A3A 190deg,#8A5A3A 260deg,#6A2E2E 260deg,#6A2E2E 315deg,#ECECEC 315deg);
}}

.donut::after {{
  content:"";
  position:absolute;
  inset:35px;
  border-radius:50%;
  background:#FFFFFF;
  box-shadow:inset 0 0 0 1px #ECECEC;
}}

.donut-center {{
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-direction:column;
  z-index:2;
  font-weight:800;
}}

.legend-row {{
  display:flex;
  justify-content:space-between;
  gap:10px;
  padding:4px 0;
  font-size:12px;
}}

.dot {{
  display:inline-block;
  width:9px;
  height:9px;
  border-radius:2px;
  margin-right:6px;
}}

.map-card {{
  min-height:380px;
}}

.map-frame {{
  width:100%;
  height:345px;
  border:0;
  border-radius:8px;
  background:#050505;
}}

.map-empty {{
  height:345px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  gap:9px;
  color:var(--texto-suave);
}}

.finding {{
  border:0;
  border-left:4px solid var(--rojo-intenso);
  border-radius:14px;
  padding:18px 20px;
  margin:8px 0;
  background:linear-gradient(180deg,var(--vino),var(--negro));
  color:#FFFFFF;
  line-height:1.6;
}}

.finding strong {{
  display:block;
  margin-bottom:5px;
  color:#FFFFFF;
}}

.comparativo {{
  margin-top:10px;
}}

table {{
  width:100%;
  border-collapse:collapse;
  font-size:12px;
}}

th,td {{
  border-bottom:1px solid #ECEFF1;
  padding:10px;
  text-align:left;
  color:var(--texto);
}}

th {{
  color:var(--texto);
  background:#FAFAFA;
  font-weight:600;
}}

.bar {{
  height:9px;
  background:#ECECEC;
  border-radius:999px;
  overflow:hidden;
}}

.bar > span {{
  display:block;
  height:100%;
  background:var(--arena);
}}

.studies {{
  margin-top:10px;
}}

.study-tools {{
  display:flex;
  gap:8px;
  margin-bottom:10px;
}}

.tabs button {{
  border:1px solid #D9DDE0;
  color:var(--texto);
  background:#FFFFFF;
  border-radius:7px;
  padding:8px 12px;
}}

.tabs button.active {{
  background:var(--vino);
  color:#FFFFFF;
  border-color:var(--vino);
}}

.status {{
  padding:4px 8px;
  border-radius:10px;
  font-size:10px;
}}

.status.verificado {{ background:#5c7a3a; }}
.status.pendiente {{ background:#a88a4a;color:#050505; }}
.status.revision {{ background:#6A2E2E; }}
.status.ok {{ background:#5c7a3a; }}

.actions {{
  display:flex;
  gap:5px;
}}

.icon-btn {{
  border:1px solid #493336;
  background:#151010;
  color:#fff;
  border-radius:5px;
  padding:4px 7px;
}}

.drawer {{
  position:fixed;
  top:0;
  right:-480px;
  width:470px;
  max-width:95vw;
  height:100vh;
  background:#FFFFFF;
  border-left:1px solid #E3E6E8;
  box-shadow:-15px 0 40px rgba(0,0,0,.5);
  transition:right .22s ease;
  z-index:20;
  padding:18px;
  overflow:auto;
}}

.drawer.open {{ right:0; }}

.drawer-head {{
  display:flex;
  justify-content:space-between;
  align-items:center;
  border-bottom:1px solid #3B2525;
  padding-bottom:12px;
  margin-bottom:15px;
}}

.drawer h2 {{ margin:0; }}

.field {{
  margin:10px 0;
}}

.field label {{
  display:block;
  font-size:10px;
  color:#6B7A86;
  margin-bottom:5px;
  text-transform:uppercase;
}}

.field input,
.field select,
.field textarea {{
  width:100%;
  background:#FFFFFF;
  color:var(--texto);
  border:1px solid #D8DDE2;
  border-radius:6px;
  padding:9px;
}}

.field textarea {{ min-height:80px; resize:vertical; }}

.drawer-actions {{
  display:flex;
  justify-content:flex-end;
  gap:8px;
  margin-top:18px;
}}

.notice {{
  padding:10px 12px;
  border:0;
  border-left:4px solid var(--borgona);
  background:#F6EEEE;
  border-radius:7px;
  color:var(--texto);
  font-size:12px;
}}

.footer {{
  color:#6B7A86;
  font-size:11px;
  padding:16px 2px;
}}

@media(max-width:1150px) {{
  .app {{ grid-template-columns:1fr; }}
  .sidebar {{ display:none; }}
  .kpis {{ grid-template-columns:repeat(2,1fr); }}
  .grid {{ grid-template-columns:1fr; }}
}}

@media(max-width:650px) {{
  .main {{ padding:10px; }}
  .hero {{ padding:17px; }}
  .hero h1 {{ font-size:26px; }}
  .hero-body {{ display:block; }}
  .kpis {{ grid-template-columns:1fr; }}
  .toolbar {{ flex-wrap:wrap; }}
}}

/* ==========================================================
   MOTOR 11.4 — REFINAMIENTO VISUAL INSTITUCIONAL
   Solo presentación. No modifica datos ni lógica.
   ========================================================== */

:root{{
  --hero-black:#050505;
  --hero-wine:#220000;
  --hero-burgundy:#6A2E2E;
}}

body{{
  background:
    radial-gradient(circle at 82% 0%, rgba(106,46,46,.055), transparent 28%),
    var(--fondo);
  color:var(--texto);
  letter-spacing:-0.005em;
}}

.sidebar{{
  background:
    linear-gradient(180deg,#080707 0%,#110809 58%,#220000 100%);
  border-right:1px solid rgba(255,255,255,.09);
}}

.brand{{
  border-color:rgba(168,138,74,.42);
  background:linear-gradient(180deg,rgba(34,0,0,.48),rgba(5,5,5,.34));
}}

.brand-main{{ color:#F5F5F5; letter-spacing:2.3px; }}
.brand-sub{{ color:#D9D9D9; }}

.nav button{{
  color:#F0EEEE;
  font-weight:500;
  transition:background .18s ease, transform .18s ease;
}}

.nav button:hover{{
  background:rgba(106,46,46,.30);
  transform:translateX(1px);
}}

.nav button.active{{
  background:linear-gradient(90deg,rgba(106,46,46,.88),rgba(34,0,0,.78));
  box-shadow:inset 3px 0 0 var(--arena);
}}

#revisionBadge{{
  display:inline-flex;
  min-width:20px;
  height:20px;
  padding:0 6px;
  align-items:center;
  justify-content:center;
  margin-left:8px;
  border-radius:999px;
  background:var(--arena);
  color:#17110A;
  font-size:11px;
  font-weight:700;
  vertical-align:middle;
}}

#revisionBadge:empty{{ display:none; }}

.territory-card small{{ color:#BFC4C8; }}
.territory-card b{{ color:#F4F4F4; font-weight:700; }}
.territory-line{{ color:#D9D9D9; }}
.territory-line b{{ color:#E9D9A7; }}

.hero{{
  background:
    radial-gradient(circle at 82% 28%,rgba(138,90,58,.20),transparent 34%),
    linear-gradient(100deg,var(--hero-black) 0%,var(--hero-wine) 62%,var(--hero-burgundy) 100%);
  color:#FFFFFF;
  border-radius:18px;
  box-shadow:0 12px 30px rgba(34,0,0,.15);
}}

.hero-top{{ color:#E4DDDD; }}
.hero h1{{
  color:#FFFFFF;
  font-weight:720;
  letter-spacing:-.025em;
}}
.hero p{{ color:#F2ECEC; }}
.hero-meta{{ color:#F2EDED; }}

.search,
.select{{
  border-color:#D8DEE3;
  box-shadow:0 2px 8px rgba(35,49,61,.025);
}}

.search::placeholder{{ color:#87939D; }}

.search:focus,
.select:focus{{
  border-color:var(--arena);
  box-shadow:0 0 0 3px rgba(168,138,74,.14);
  outline:none;
}}

.btn{{
  box-shadow:0 2px 8px rgba(35,49,61,.04);
  transition:transform .15s ease, box-shadow .15s ease, background .15s ease;
}}
.btn:hover{{
  transform:translateY(-1px);
  box-shadow:0 5px 14px rgba(35,49,61,.09);
}}
.btn.primary{{
  background:linear-gradient(180deg,#351012,var(--vino));
  border-color:#4C2022;
}}

.kpi{{
  position:relative;
  overflow:hidden;
  background:var(--panel);
  border-top:3px solid var(--borgona);
  box-shadow:0 8px 24px rgba(35,49,61,.075);
}}
.kpi:nth-child(2){{ border-top-color:var(--verde); }}
.kpi:nth-child(3){{ border-top-color:var(--verde); }}
.kpi:nth-child(4){{ border-top-color:var(--arena); }}
.kpi:nth-child(5){{ border-top-color:var(--borgona); }}

.kpi .value{{
  color:var(--vino);
  font-weight:750;
  letter-spacing:-.035em;
}}
.kpi .label{{
  color:var(--texto);
  font-weight:600;
}}
.kpi .sub{{ color:var(--texto-suave); }}
.kpi > div:first-child{{ color:var(--arena) !important; }}

.card{{
  background:rgba(255,255,255,.98);
  border:1px solid rgba(35,49,61,.045);
  box-shadow:0 9px 26px rgba(35,49,61,.07);
}}
.card h2{{
  color:var(--texto);
  font-weight:720;
  letter-spacing:-.015em;
}}

.donut::after{{ background:#FFFFFF; }}
.donut-center{{ color:var(--texto); }}
.legend-row{{ color:var(--texto); }}
.legend-row b{{ color:#18242D; }}

.finding{{
  background:
    linear-gradient(145deg,#2A0708 0%,#170707 66%,#0B0909 100%);
  border:1px solid rgba(168,138,74,.20);
  border-left:4px solid var(--borgona);
  color:#FFFFFF !important;
  box-shadow:0 7px 18px rgba(34,0,0,.12);
  line-height:1.62;
}}
.finding,
.finding *{{ color:#FFFFFF !important; }}
.finding strong,
.finding b{{ color:#F6E7C0 !important; }}

.map-frame{{
  border:1px solid #E6EAED;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.65);
}}

table{{ color:var(--texto); }}
th{{
  color:#45545F;
  background:#F7F8F9;
  border-bottom:1px solid #DDE2E6;
}}
td{{ color:#34434E; }}
tbody tr:hover{{ background:#FAF8F6; }}

.bar{{ background:#ECEFF1; }}
.bar > span{{
  background:linear-gradient(90deg,var(--arena),var(--terracota));
}}

.status.verificado{{ background:var(--verde); color:#FFFFFF; }}
.status.pendiente{{ background:var(--arena); color:#20180B; }}
.status.revision{{ background:var(--borgona); color:#FFFFFF; }}

.icon-btn{{
  background:#FFFFFF;
  color:var(--vino);
  border-color:#D7DDE1;
}}
.icon-btn:hover{{ background:#F7F2F1; }}

.drawer{{
  background:#FFFFFF;
  color:var(--texto);
}}
.drawer h2,
.drawer .field label{{ color:var(--texto); }}

.field label{{ color:#5E6C76; }}

.field input,
.field select,
.field textarea{{
  background:#FFFFFF;
  color:var(--texto);
  border-color:#D7DDE1;
}}

.field input:focus,
.field select:focus,
.field textarea:focus{{
  border-color:var(--arena);
  outline:none;
  box-shadow:0 0 0 3px rgba(168,138,74,.12);
}}

.notice{{
  background:#F8F1EF;
  color:var(--texto);
  border-left:4px solid var(--borgona);
}}

.footer{{ color:#6B7A86; }}

#methodSection{{ color:var(--texto); }}
#methodSection p,
#methodSection .method{{ color:#52616B; }}

@media(max-width:1180px){{
  .hero h1{{ font-size:31px; }}
}}

</style>
</head>

<body>
<div class="app">

<aside class="sidebar">
  <div class="brand">
    <div class="brand-main">TRANSVERSO</div>
    <div class="brand-sub">Observatorio Pilates</div>
  </div>

  <div class="nav">
    <button class="active">▦ &nbsp; Dashboard</button>
    <button onclick="document.getElementById('mapSection').scrollIntoView()">⌖ &nbsp; Mapa territorial</button>
    <button onclick="document.getElementById('studiesSection').scrollIntoView()">◉ &nbsp; Estudios</button>
    <button onclick="document.getElementById('comparativoSection').scrollIntoView()">▤ &nbsp; Comparativos</button>
    <button onclick="document.getElementById('methodSection').scrollIntoView()">◷ &nbsp; Metodología</button>
    <button onclick="filtrarRevision()">⚠ &nbsp; Candidatos a revisión <span id="revisionBadge"></span></button>
  </div>

  <div class="territory-card">
    <small>TERRITORIO ACTUAL</small>
    <b>{html.escape(title)}</b>
    <div id="territorySummary"></div>
    <button class="btn soft" style="width:100%;margin-top:12px" onclick="resetFiltros()">↔ Cambiar territorio</button>
  </div>
</aside>

<main class="main">

<header class="hero">
  <div class="hero-top">
    <span>Actualizado automáticamente · {fecha}</span>
    <span>{html.escape(profile.get("country","Argentina"))} · {html.escape(str(profile.get("version","1.0")))}</span>
  </div>
  <div class="hero-body">
    <div>
      <h1>Observatorio Pilates Transverso</h1>
      <p>Inteligencia territorial del ecosistema Pilates.</p>
      <div class="hero-meta">
        <b id="heroCount">0</b> estudios ·
        <b id="heroLocalidades">0</b> {unidad_plural.lower()} ·
        <b id="heroRevision">0</b> candidatos a revisión
      </div>
    </div>
  </div>
</header>

<div class="toolbar">
  <input id="search" class="search"
    placeholder="Buscar estudio, {unidad_singular.lower()}, dirección, teléfono, Instagram..."
    oninput="render()">
  <select id="territoryFilter" class="select" onchange="render()">
    <option value="">{unidad_singular}: todos</option>
  </select>
  <select id="statusFilter" class="select" onchange="render()">
    <option value="">Estado: todos</option>
    <option value="Verificado">Verificados</option>
    <option value="Pendiente">Pendientes</option>
    <option value="Revisión">Revisión</option>
  </select>
  <button class="btn primary" onclick="nuevoEstudio()">+ Nuevo estudio</button>
  <button class="btn" onclick="exportarCSV()">↓ Exportar CSV</button>
</div>

<section class="kpis" id="kpis"></section>

<div class="grid">

  <section class="card">
    <h2>DISTRIBUCIÓN POR {html.escape(unidad_singular.upper())}</h2>
    <div class="donut-wrap">
      <div class="donut" id="donut">
        <div class="donut-center">
          <span id="donutTotal">0</span>
          <small>Estudios</small>
        </div>
      </div>
      <div id="legend" style="flex:1"></div>
    </div>
  </section>

  <section class="card map-card" id="mapSection">
    <h2>MAPA TERRITORIAL</h2>
    <div style="font-size:11px;color:var(--texto-suave);margin-bottom:8px;">Cartografía institucional: {html.escape(str(unidad_institucional))}. Filtro analítico: {html.escape(unidad_singular.lower())}.</div>
    {mapa_doc}
  </section>

  <section class="card">
    <h2>HALLAZGOS PRINCIPALES</h2>
    <div id="hallazgos"></div>
  </section>

  <section class="card" id="comparativoSection">
    <h2>COMPARATIVO POR {html.escape(unidad_singular.upper())}</h2>
    <div id="comparativo"></div>
  </section>

  <section class="card">
    <h2>CANALES DIGITALES</h2>
    <div id="digital"></div>
  </section>

</div>

<section class="card studies" id="studiesSection">
  <h2>ESTUDIOS</h2>
  <div class="study-tools">
    <div class="tabs">
      <button id="tabAll" class="active" onclick="setStatus('')">Todos</button>
      <button id="tabVerified" onclick="setStatus('Verificado')">Verificados</button>
      <button id="tabPending" onclick="setStatus('Pendiente')">Pendientes</button>
      <button id="tabReview" onclick="setStatus('Revisión')">Revisión</button>
    </div>
  </div>
  <div id="studyTable"></div>
</section>

<section class="card studies" id="methodSection" style="margin-top:10px;">
  <h2>METODOLOGÍA</h2>
  <p style="color:var(--texto-suave);font-size:12px;line-height:1.6;">
    El Dashboard consume la capa consolidada o integrada del territorio.
    La unidad institucional proviene de territory_profile.json; la unidad operativa
    corresponde a la granularidad disponible en el lote seleccionado. El editor
    trabaja como capa editorial local y no modifica automáticamente SQLite ni
    estudios_features.csv.
  </p>
</section>

<div class="footer">
  Observatorio Pilates Transverso · Motor 11 ·
  Fuente: integración territorial {html.escape(city)}
  {(" · lote " + html.escape(lote)) if lote else ""}
  · Los cambios del editor se guardan localmente en este navegador y pueden exportarse.
</div>

</main>
</div>

<div class="drawer" id="drawer">
  <div class="drawer-head">
    <h2 id="drawerTitle">Editar estudio</h2>
    <button class="icon-btn" onclick="cerrarDrawer()">✕</button>
  </div>

  <div id="duplicateNotice"></div>
  <div id="form"></div>

  <div class="drawer-actions">
    <button class="btn" onclick="cerrarDrawer()">Cancelar</button>
    <button class="btn primary" onclick="guardarEstudio()">Guardar cambios</button>
  </div>
</div>

<script>
const INITIAL = {records_json};
const UNIT = {escape_js_string(unidad)};
const MAP_SRC = {mapa_srcdoc};
const STORAGE_KEY = "transverso_dashboard_{html.escape(city)}_{html.escape(lote or 'provincial')}_m11_3_visual";

let rows = loadRows();
if (!Array.isArray(rows)) rows = [];
let editingIndex = null;
let activeStatus = "";

console.info(
  "[Motor 11.1] Fuente canónica:",
  {{
    registros: Array.isArray(INITIAL) ? INITIAL.length : 0,
    unidad: UNIT,
    territorios: Array.isArray(INITIAL)
      ? [...new Set(
          INITIAL
            .map(r => text(r[UNIT]).trim())
            .filter(Boolean)
        )]
      : [],
    revisiones: Array.isArray(INITIAL)
      ? INITIAL.filter(r => normalize(r.estado) === "revision").length
      : 0
  }}
);

function loadRows() {{
  const canonical = Array.isArray(INITIAL) ? INITIAL : [];

  let saved = null;

  try {{
    const raw = localStorage.getItem(STORAGE_KEY);

    if (raw) {{
      const parsed = JSON.parse(raw);

      if (Array.isArray(parsed)) {{
        saved = parsed;
      }}
    }}
  }} catch(e) {{
    console.warn("No se pudo leer localStorage:", e);
  }}

  if (!saved || !saved.length) {{
    return canonical;
  }}

  const savedById = new Map(
    saved
      .filter(r => r && r.id_estudio)
      .map(r => [String(r.id_estudio), r])
  );

  return canonical.map(base => {{
    const id = String(base.id_estudio || "");
    const editado = savedById.get(id);

    if (!editado) {{
      return base;
    }}

    const merged = {{
      ...base,
      ...editado
    }};

    // Contrato territorial:
    // la unidad operativa procede siempre de la fuente consolidada.
    merged[UNIT] = base[UNIT];

    // Contrato editorial:
    // un candidato canónico a revisión no puede perder ese estado
    // por datos persistidos por una versión anterior del Dashboard.
    if (normalize(base.estado) === "revision") {{
      merged.estado = "Revisión";
    }}

    return merged;
  }});
}}

function persist() {{
  localStorage.setItem(STORAGE_KEY, JSON.stringify(rows));
}}

function text(v) {{
  return v === null || v === undefined ? "" : String(v);
}}

function escapeHtml(v) {{
  return text(v)
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;")
    .replaceAll('"',"&quot;")
    .replaceAll("'","&#039;");
}}

function valueFor(r, key) {{
  return text(r[key]);
}}

function normalize(v) {{
  return text(v).toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"");
}}

function visibleRows() {{
  const q = normalize(document.getElementById("search").value);
  const territory = document.getElementById("territoryFilter").value;
  const status = activeStatus || document.getElementById("statusFilter").value;

  return rows.map((r,i)=>({{r,i}})).filter(x => {{
    const r = x.r;
    const blob = [
      r.id_estudio,
      r.nombre_del_estudio,
      r[UNIT],
      r.direccion,
      r.telefono,
      r.email,
      r.instagram,
      r.web
    ].map(normalize).join(" ");

    return (!q || blob.includes(q))
      && (!territory || text(r[UNIT]) === territory)
      && (!status || text(r.estado) === status);
  }});
}}

function territories() {{
  return [
    ...new Set(
      rows
        .map(r => text(r[UNIT]).trim())
        .filter(Boolean)
    )
  ].sort((a,b)=>a.localeCompare(b,"es"));
}}

function pct(n,total) {{
  return total ? (100*n/total).toFixed(2) : "0.00";
}}

function renderSelectors() {{
  const sel = document.getElementById("territoryFilter");
  const current = sel.value;
  sel.innerHTML = '<option value="">{unidad_singular}: todos</option>' +
    territories().map(t=>`<option value="${{escapeHtml(t)}}">${{escapeHtml(t)}}</option>`).join("");
  sel.value = current;
}}

function renderKpis(data) {{
  const total = data.length;
  const locs = new Set(data.map(x=>text(x.r[UNIT]).trim()).filter(Boolean)).size;
  const review = data.filter(x=>normalize(x.r.estado)==="revision").length;
  const pending = data.filter(x=>normalize(x.r.estado)==="pendiente").length;
  const verified = data.filter(x=>normalize(x.r.estado)==="verificado").length;

  document.getElementById("heroCount").textContent = total;
  document.getElementById("heroLocalidades").textContent = locs;
  document.getElementById("heroRevision").textContent = review;
  document.getElementById("revisionBadge").textContent = review ? review : "";

  document.getElementById("kpis").innerHTML = [
    ["▦",total,"Estudios","Totales visibles"],
    ["⌖",locs,"{unidad_plural}","Con estudios"],
    ["✓",verified, "Verificados", total ? pct(verified,total)+"%" : "0%"],
    ["◷",pending,"Pendientes", total ? pct(pending,total)+"%" : "0%"],
    ["⚠",review,"Revisión","Posibles duplicados"]
  ].map(k=>`
    <div class="kpi">
      <div style="color:#A88A4A;font-size:18px">${{k[0]}}</div>
      <div class="value">${{k[1]}}</div>
      <div class="label">${{k[2]}}</div>
      <div class="sub">${{k[3]}}</div>
    </div>`).join("");
}}

function renderTerritory(data) {{
  const counts = {{}};
  data.forEach(x => {{
    const k = text(x.r[UNIT]).trim() || "Sin territorio";
    counts[k] = (counts[k]||0)+1;
  }});
  const items = Object.entries(counts).sort((a,b)=>b[1]-a[1]);

  document.getElementById("donutTotal").textContent = data.length;

  const colors = ["#5C7A3A","#A88A4A","#8A5A3A","#6A2E2E","#B8BDC2","#7B858C"];
  let start = 0;
  const stops = [];
  items.forEach((it,idx)=>{{
    const deg = data.length ? 360*it[1]/data.length : 0;
    stops.push(`${{colors[idx%colors.length]}} ${{start}}deg ${{start+deg}}deg`);
    start += deg;
  }});
  document.getElementById("donut").style.background =
    stops.length ? `conic-gradient(${{stops.join(",")}})` : "#332a2c";

  document.getElementById("legend").innerHTML = items.map((it,idx)=>`
    <div class="legend-row">
      <span><span class="dot" style="background:${{colors[idx%colors.length]}}"></span>${{escapeHtml(it[0])}}</span>
      <b>${{pct(it[1],data.length)}}% (${{it[1]}})</b>
    </div>`).join("");

  document.getElementById("comparativo").innerHTML = `
    <table>
      <thead><tr><th>#</th><th>Territorio</th><th>Estudios</th><th>%</th></tr></thead>
      <tbody>${{items.map((it,idx)=>`
        <tr>
          <td>${{idx+1}}</td>
          <td>${{escapeHtml(it[0])}}</td>
          <td>${{it[1]}}</td>
          <td>${{pct(it[1],data.length)}}%</td>
        </tr>`).join("")}}</tbody>
    </table>`;
}}

function renderDigital(data) {{
  const fields = [
    ["instagram","Instagram"],
    ["web","Web"],
    ["email","Email"],
    ["app","App"]
  ];

  document.getElementById("digital").innerHTML = fields.map(([key,label])=>{{
    const n = data.filter(x=>text(x.r[key]).trim()!=="").length;
    return `<div style="margin:10px 0">
      <div style="display:flex;justify-content:space-between;font-size:12px">
        <span>${{label}}</span><b>${{pct(n,data.length)}}%</b>
      </div>
      <div class="bar"><span style="width:${{pct(n,data.length)}}%"></span></div>
    </div>`;
  }}).join("");
}}

function renderHallazgos(data) {{
  const total = data.length;
  const counts = {{}};
  data.forEach(x=>{{const k=text(x.r[UNIT]).trim()||"Sin territorio";counts[k]=(counts[k]||0)+1;}});
  const top = Object.entries(counts).sort((a,b)=>b[1]-a[1])[0];

  const instagram = data.filter(x=>text(x.r.instagram).trim()!=="").length;
  const web = data.filter(x=>text(x.r.web).trim()!=="").length;
  const review = data.filter(x=>normalize(x.r.estado)==="revision").length;

  const findings = [
    top ? `${{escapeHtml(top[0])}} concentra el ${{pct(top[1],total)}}% de los estudios del territorio.` : "Sin datos territoriales.",
    `Instagram está presente en ${{pct(instagram,total)}}% de los estudios visibles.`,
    `Web está presente en ${{pct(web,total)}}% de los estudios visibles.`,
    `${{review}} estudio(s) requieren revisión según el estado editorial actual.`
  ];

  document.getElementById("hallazgos").innerHTML =
    findings.map(x=>`<div class="finding">${{escapeHtml(x)}}</div>`).join("");
}}

function statusBadge(s) {{
  const n = normalize(s);
  if (n==="verificado") return `<span class="status verificado">Verificado</span>`;
  if (n==="pendiente") return `<span class="status pendiente">Pendiente</span>`;
  if (n==="revision") return `<span class="status revision">Revisión</span>`;
  return `<span class="status ok">${{escapeHtml(s||"OK")}}</span>`;
}}

function renderStudies(data) {{
  const rowsHtml = data.slice(0,100).map(x=>`
    <tr>
      <td>${{escapeHtml(x.r.id_estudio)}}</td>
      <td>${{escapeHtml(x.r.nombre_del_estudio)}}</td>
      <td>${{escapeHtml(x.r[UNIT])}}</td>
      <td>${{escapeHtml(x.r.direccion)}}</td>
      <td>${{escapeHtml(x.r.telefono)}}</td>
      <td>${{escapeHtml(x.r.instagram)}}</td>
      <td>${{statusBadge(x.r.estado)}}</td>
      <td class="actions">
        <button class="icon-btn" onclick="editarEstudio(${{x.i}})">✎</button>
      </td>
    </tr>`).join("");

  document.getElementById("studyTable").innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Estudio</th><th>{unidad_singular}</th>
          <th>Dirección</th><th>Teléfono</th><th>Instagram</th>
          <th>Estado</th><th>Editar</th>
        </tr>
      </thead>
      <tbody>${{rowsHtml}}</tbody>
    </table>
    <div style="color:#6B7A86;font-size:11px;margin-top:10px">
      Mostrando ${{Math.min(data.length,100)}} de ${{data.length}} registros visibles.
    </div>`;
}}

function renderTerritorySummary() {{
  const counts = {{}};
  rows.forEach(r=>{{const k=text(r[UNIT]).trim(); if(k) counts[k]=(counts[k]||0)+1;}});
  document.getElementById("territorySummary").innerHTML =
    Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([k,v])=>
      `<div class="territory-line"><span>${{escapeHtml(k)}}</span><b>${{v}}</b></div>`
    ).join("");
}}

function render() {{
  activeStatus = document.getElementById("statusFilter").value;
  const data = visibleRows();

  console.info(
    "[Motor 11.2] Vista",
    {{
      registros: data.length,
      territorios: [...new Set(
        data.map(x => text(x.r[UNIT]).trim()).filter(Boolean)
      )],
      revisiones: data.filter(
        x => normalize(x.r.estado) === "revision"
      ).length
    }}
  );

  renderSelectors();
  renderKpis(data);
  renderTerritory(data);
  renderDigital(data);
  renderHallazgos(data);
  renderStudies(data);
  renderTerritorySummary();

  if (MAP_SRC) {{
    const frame = document.getElementById("mapFrame");

    if (frame && !frame.dataset.loaded) {{
      frame.srcdoc = MAP_SRC;
      frame.dataset.loaded = "1";
    }}
  }}
}}

function setStatus(status) {{
  activeStatus = status;
  document.getElementById("statusFilter").value = status;
  document.querySelectorAll(".tabs button").forEach(b=>b.classList.remove("active"));
  if (!status) document.getElementById("tabAll").classList.add("active");
  if (status==="Verificado") document.getElementById("tabVerified").classList.add("active");
  if (status==="Pendiente") document.getElementById("tabPending").classList.add("active");
  if (status==="Revisión") document.getElementById("tabReview").classList.add("active");
  render();
}}

function filtrarRevision() {{
  setStatus("Revisión");
  document.getElementById("studiesSection").scrollIntoView();
}}

function resetFiltros() {{
  document.getElementById("search").value = "";
  document.getElementById("territoryFilter").value = "";
  setStatus("");
}}

function editarEstudio(index) {{
  editingIndex = index;
  const r = rows[index];
  abrirDrawer("Editar estudio");
  pintarForm(r);
}}

function nuevoEstudio() {{
  editingIndex = null;
  abrirDrawer("Nuevo estudio");
  pintarForm({{
    id_estudio: "",
    nombre_del_estudio: "",
    [UNIT]: "",
    direccion: "",
    telefono: "",
    email: "",
    instagram: "",
    web: "",
    estado: "Pendiente",
    observaciones: ""
  }});
}}

function abrirDrawer(titulo) {{
  document.getElementById("drawerTitle").textContent = titulo;
  document.getElementById("drawer").classList.add("open");
}}

function cerrarDrawer() {{
  document.getElementById("drawer").classList.remove("open");
  editingIndex = null;
}}

function pintarForm(r) {{
  const fields = [
    ["id_estudio","ID estudio"],
    ["nombre_del_estudio","Nombre del estudio"],
    [UNIT,UNIT],
    ["direccion","Dirección"],
    ["telefono","Teléfono"],
    ["email","Email"],
    ["instagram","Instagram"],
    ["web","Web"],
    ["estado","Estado"],
    ["observaciones","Observaciones"]
  ];

  document.getElementById("form").innerHTML = fields.map(([key,label])=>{{
    if (key==="estado") {{
      return `<div class="field">
        <label>${{escapeHtml(label)}}</label>
        <select id="f_${{escapeHtml(key)}}">
          ${{["Verificado","Pendiente","Revisión"].map(s=>
            `<option ${{text(r[key])===s?"selected":""}}>${{s}}</option>`).join("")}}
        </select>
      </div>`;
    }}

    if (key==="observaciones") {{
      return `<div class="field">
        <label>${{escapeHtml(label)}}</label>
        <textarea id="f_${{escapeHtml(key)}}">${{escapeHtml(r[key])}}</textarea>
      </div>`;
    }}

    return `<div class="field">
      <label>${{escapeHtml(label)}}</label>
      <input id="f_${{escapeHtml(key)}}" value="${{escapeHtml(r[key])}}">
    </div>`;
  }}).join("");

  const duplicates = rows.filter((x,i)=>
    i!==editingIndex &&
    normalize(x.nombre_del_estudio)===normalize(r.nombre_del_estudio) &&
    normalize(r.nombre_del_estudio)!==""
  );

  document.getElementById("duplicateNotice").innerHTML =
    duplicates.length
      ? `<div class="notice"><b>Posible duplicado:</b> se encontraron ${{duplicates.length}} registro(s) con el mismo nombre.</div>`
      : "";
}}

function guardarEstudio() {{
  const keys = [
    "id_estudio","nombre_del_estudio",UNIT,"direccion",
    "telefono","email","instagram","web","estado","observaciones"
  ];

  const r = {{}};
  keys.forEach(k=>{{
    const el = document.getElementById("f_"+k);
    r[k] = el ? el.value.trim() : "";
  }});

  if (!r.nombre_del_estudio) {{
    alert("El nombre del estudio es obligatorio.");
    return;
  }}

  if (!r.id_estudio) {{
    r.id_estudio = "MANUAL-" + Date.now();
  }}

  if (editingIndex === null) {{
    rows.push(r);
  }} else {{
    rows[editingIndex] = {{...rows[editingIndex], ...r}};
  }}

  persist();
  cerrarDrawer();
  render();
}}

function csvEscape(v) {{
  const s = text(v).replaceAll('"','""');
  return `"${{s}}"`;
}}

function exportarCSV() {{
  const columns = [...new Set(rows.flatMap(r=>Object.keys(r)))];
  const csv = [
    columns.map(csvEscape).join(","),
    ...rows.map(r=>columns.map(c=>csvEscape(r[c])).join(","))
  ].join("\\n");

  const blob = new Blob(["\\ufeff"+csv], {{type:"text/csv;charset=utf-8;"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "estudios_editados_dashboard.csv";
  a.click();
  URL.revokeObjectURL(url);
}}

try {{
  render();
}} catch (e) {{
  console.error("Error inicializando el dashboard:", e);
  const host = document.getElementById("hallazgos");
  if (host) host.innerHTML = '<div class="finding">No se pudo inicializar una vista del dashboard.</div>';
}}
</script>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Dashboard Único del Observatorio Pilates Transverso."
    )
    parser.add_argument("--city", required=True)
    parser.add_argument("--lote", default=None)
    args = parser.parse_args()

    dataset = localizar_dataset(args.city, args.lote)
    profile = cargar_profile(args.city)

    df = pd.read_csv(dataset, encoding="utf-8-sig")
    unidad, unidad_institucional = detectar_unidad(df, profile, args.lote)
    df = preparar_df(df, unidad)
    df = aplicar_estado_editorial(
        df,
        localizar_candidatos_revision(args.city, args.lote),
    )

    if args.lote == "ba_norte":
        esperado = {
            "San Isidro": 16,
            "Tigre": 10,
            "Vicente López": 10,
            "Olivos": 8,
            "San Fernando": 7,
        }
        conteo = (
            df[unidad]
            .fillna("")
            .astype(str)
            .str.strip()
            .value_counts()
            .to_dict()
        )
        if len(df) != 51:
            raise ValueError(
                f"Checkpoint ba_norte inválido: {len(df)} estudios; esperados 51."
            )
        diferencias = {
            k: {"esperado": v, "actual": int(conteo.get(k, 0))}
            for k, v in esperado.items()
            if int(conteo.get(k, 0)) != v
        }
        if diferencias:
            raise ValueError(
                "Checkpoint territorial ba_norte inválido:\n"
                + json.dumps(diferencias, ensure_ascii=False, indent=2)
            )

    mapa = localizar_mapa(args.city)
    mapa_html = mapa.read_text(encoding="utf-8") if mapa else None

    html_out = generar_html(
        args.city,
        args.lote,
        df,
        profile,
        unidad,
        mapa_html,
    )

    rutas = city_paths(args.city)
    rutas["dashboard"].mkdir(parents=True, exist_ok=True)

    destino = rutas["dashboard"] / "observatorio_unico.html"
    destino.write_text(html_out, encoding="utf-8")

    print("=" * 60)
    print("OBSERVATORIO PILATES TRANSVERSO")
    print("MOTOR 11 — DASHBOARD ÚNICO")
    print("=" * 60)
    print(f"Territorio : {args.city}")
    print(f"Lote       : {args.lote or 'provincial'}")
    print(f"Entrada    : {dataset}")
    print(f"Unidad institucional : {unidad_institucional}")
    print(f"Unidad operativa     : {unidad}")
    print(f"Candidatos revisión  : {(df['estado'] == 'Revisión').sum()}")
    print(f"Estudios   : {len(df)}")
    print()
    print("Dashboard generado:")
    print(destino)


if __name__ == "__main__":
    main()