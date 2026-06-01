import os
import math
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Fonte de dados orbitais REAIS (publica, sem login/chave): CelesTrak GP API.
# Grupo "cosmos-2251-debris": fragmentos reais da colisao Cosmos-2251 / Iridium-33 (2009),
# um dos maiores eventos de geracao de detritos espaciais da historia.
CELESTRAK_URL = (
    "https://celestrak.org/NORAD/elements/gp.php"
    "?GROUP=cosmos-2251-debris&FORMAT=json"
)

# Constantes fisicas (Terra)
MU = 398600.4418          # km^3/s^2  -> parametro gravitacional padrao
EARTH_RADIUS = 6378.137   # km        -> raio equatorial medio

# Cache em memoria. A CelesTrak atualiza os dados poucas vezes ao dia e limita
# requisicoes frequentes (rate-limit), entao usamos um TTL longo (2h).
_CACHE = {"ts": 0, "data": None, "source": None}
_CACHE_TTL = 7200  # 2 horas (alinhado a recomendacao da CelesTrak)

# Fallback simulado (usado apenas se a API real estiver indisponivel)
_FALLBACK = [
    {"id": "DEB-2207", "name": "COSMOS 2251 DEB (sim)", "type": "Detrito",
     "altitude_km": 782.5, "velocity_kms": 7.18, "inclination_deg": 76.6,
     "collision_prob": 0.887, "norad_id": None, "epoch": None},
    {"id": "SAT-OG-01", "name": "Objeto Rastreado (sim)", "type": "Objeto Rastreado",
     "altitude_km": 621.2, "velocity_kms": 7.55, "inclination_deg": 25.4,
     "collision_prob": 0.031, "norad_id": None, "epoch": None},
]


def _risk_from(altitude_km, collision_prob):
    if collision_prob >= 0.7 or altitude_km < 500:
        return "CRITICO"
    if collision_prob >= 0.35:
        return "ATENCAO"
    return "NOMINAL"


def _transform(gp):
    mm = float(gp.get("MEAN_MOTION", 0) or 0)
    if mm <= 0:
        return None
    period_s = 86400.0 / mm
    a = (MU * (period_s / (2 * math.pi)) ** 2) ** (1.0 / 3.0)
    ecc = float(gp.get("ECCENTRICITY", 0) or 0)
    altitude = a * (1 - ecc) - EARTH_RADIUS
    velocity = math.sqrt(MU / a)
    incl = float(gp.get("INCLINATION", 0) or 0)
    name = gp.get("OBJECT_NAME", "Desconhecido")
    norad = gp.get("NORAD_CAT_ID")
    is_deb = "DEB" in name.upper() or "R/B" in name.upper()
    obj_type = "Detrito" if is_deb else "Objeto Rastreado"
    bstar = abs(float(gp.get("BSTAR", 0) or 0))
    prob = max(0.0, min(0.99, (1.0 / max(altitude, 1)) * 250 + bstar * 800))
    return {
        "id": gp.get("OBJECT_ID", str(norad)),
        "norad_id": norad,
        "name": name,
        "type": obj_type,
        "altitude_km": round(altitude, 1),
        "velocity_kms": round(velocity, 2),
        "inclination_deg": round(incl, 1),
        "collision_prob": round(prob, 3),
        "epoch": gp.get("EPOCH"),
        "risk": _risk_from(altitude, prob),
    }


def fetch_objects():
    now = time.time()
    if _CACHE["data"] and now - _CACHE["ts"] < _CACHE_TTL:
        return _CACHE["data"], _CACHE["source"]
    try:
        r = requests.get(CELESTRAK_URL, timeout=15,
                         headers={"User-Agent": "OrbitGuard/2.0"})
        r.raise_for_status()
        raw = r.json()
        objs = [t for t in (_transform(g) for g in raw) if t]
        objs = sorted(objs, key=lambda o: o["collision_prob"], reverse=True)[:25]
        if objs:
            _CACHE.update(ts=now, data=objs, source="CelesTrak (dados reais)")
            return objs, "CelesTrak (dados reais)"
    except Exception as e:
        app.logger.warning("Falha CelesTrak, usando fallback: %s", e)
    for f in _FALLBACK:
        f["risk"] = _risk_from(f["altitude_km"], f["collision_prob"])
    return _FALLBACK, "Fallback simulado (API indisponivel)"


def build_summary(data):
    return {
        "total": len(data),
        "criticos": sum(1 for d in data if d["risk"] == "CRITICO"),
        "atencao": sum(1 for d in data if d["risk"] == "ATENCAO"),
        "nominais": sum(1 for d in data if d["risk"] == "NOMINAL"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.route("/")
def index():
    data, source = fetch_objects()
    return render_template("index.html", objects=data,
                           summary=build_summary(data), source=source)


@app.route("/api/objects")
def api_objects():
    data, source = fetch_objects()
    summary = build_summary(data)
    summary["source"] = source
    return jsonify({"summary": summary, "objects": data})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "orbitguard", "version": "2.0.0"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
