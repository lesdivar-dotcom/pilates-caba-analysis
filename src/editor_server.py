# ============================================================
# OBSERVATORIO PILATES TRANSVERSO
# Motor 7.4 — Editorial Web
# Entrega 1
#
# Servidor editorial local
# ============================================================

from pathlib import Path

from flask import (
    Flask,
    jsonify,
    request,
    send_file,
    render_template
)

from validators import validar_draft
from draft_store import create_draft
from alias_detector import detectar_alias, top_candidatos
from duplicate_guard import buscar

# ------------------------------------------------------------
# Rutas
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DASHBOARD_HTML = (
    ROOT /
    "data" /
    "dashboard" /
    "observatorio_caba.html"
)

TEMPLATE_FOLDER = ROOT / "templates"

# ------------------------------------------------------------
# Flask
# ------------------------------------------------------------

app = Flask(

    __name__,

    template_folder=str(TEMPLATE_FOLDER)

)

# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def editor():
    return render_template("editor_shell.html")


@app.route("/dashboard")
def dashboard():

    return send_file(DASHBOARD_HTML)

# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "ok",

        "motor": "7.4",

        "dashboard": DASHBOARD_HTML.exists(),

        "templates": TEMPLATE_FOLDER.exists()

    })

# ============================================================
# VALIDAR
# ============================================================

@app.route("/api/validar", methods=["POST"])
def api_validar():

    payload = request.json or {}

    return jsonify(

        validar_draft("caba", payload)

    )

# ============================================================
# ALIAS
# ============================================================

@app.route("/api/alias", methods=["POST"])
def api_alias():

    payload = request.json or {}

    nombre = payload.get("nombre", "")

    return jsonify({

        "principal": detectar_alias(nombre),

        "top": top_candidatos(nombre, 5)

    })

# ============================================================
# DUPLICATE GUARD
# ============================================================

@app.route("/api/duplicate", methods=["POST"])
def api_duplicate():

    payload = request.json or {}

    return jsonify(

        buscar(

            payload.get("nombre", ""),

            payload.get("direccion", ""),

            payload.get("barrio", "")

        )

    )

# ============================================================
# DRAFT
# ============================================================

@app.route("/api/draft", methods=["POST"])
def api_draft():

    payload = request.json or {}

    validacion = validar_draft(

        "caba",

        payload

    )

    if not validacion["ok"]:

        return jsonify({

            "ok": False,

            "errores": validacion["errores"]

        }), 400

    draft = create_draft(

        "caba",

        validacion["normalizado"]

    )

    return jsonify({

        "ok": True,

        "draft": draft

    })

# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("MOTOR 7.4 — EDITORIAL WEB")
    print("=" * 70)

    print("\nServidor editorial listo.\n")

    print("Dashboard:")
    print("http://127.0.0.1:5000")

    print("\nAPI disponible:")
    print("  /health")
    print("  /api/validar")
    print("  /api/alias")
    print("  /api/duplicate")
    print("  /api/draft")

    print("\nCtrl+C para finalizar.\n")

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False

    )


if __name__ == "__main__":

    main()