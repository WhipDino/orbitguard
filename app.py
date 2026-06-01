import os
import math
import random
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# ---------------------------------------------------------------------------
# OrbitGuard - Dashboard de Status Orbital + Risco de Colisao
# Global Solution / SDTCC - Industria Espacial - ODS 9
# Dados de detritos espaciais SIMULADOS para fins de demonstracao.
# ---------------------------------------------------------------------------

TRACKED_OBJECTS = [
    {"id": "SAT-OG-01", "name": "Sentinel-A", "type": "Satelite Ativo"},
    {"id": "SAT-OG-02", "name": "MeteoSat-BR", "type": "Satelite Ativo"},
    {"id": "DEB-1142", "name": "Fragmento Cosmos", "type": "Detrito"},
    {"id": "DEB-2207", "name": "Estagio de Foguete", "type": "Detrito"},
    {"id": "DEB-3391", "name": "Painel Solar Perdido", "type": "Detrito"},
    {"id": "DEB-4456", "name": "Fragmento Anti-Sat", "type": "Detrito"},
]


def risk_level(prob):
    if prob >= 0.66:
        return "CRITICO"
    if prob >= 0.33:
        return "ATENCAO"
    return "NOMINAL"


def snapshot():
    rng = random.Random()
    objs = []
    for o in TRACKED_OBJECTS:
        alt = round(rng.uniform(400, 1200), 1)
        vel = round(rng.uniform(6.9, 7.8), 2)
        prob = round(rng.random(), 3)
        objs.append({
            **o,
            "altitude_km": alt,
            "velocity_kms": vel,
            "inclination_deg": round(rng.uniform(0, 98), 1),
            "collision_prob": prob,
            "risk": risk_level(prob),
        })
    objs.sort(key=lambda x: x["collision_prob"], reverse=True)
    return objs


@app.route("/")
def index():
    return render_template("index.html",
                           updated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))


@app.route("/api/objects")
def api_objects():
    data = snapshot()
    summary = {
        "total": len(data),
        "criticos": sum(1 for d in data if d["risk"] == "CRITICO"),
        "atencao": sum(1 for d in data if d["risk"] == "ATENCAO"),
        "nominais": sum(1 for d in data if d["risk"] == "NOMINAL"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify({"summary": summary, "objects": data})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "orbitguard", "version": "1.1.0"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
