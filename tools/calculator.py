"""
Telemetry helpers used by the WhatsApp bot and REST API.
"""
import math
import re
import uuid
from core.db import execute
from core.llm import chat_json

# ── Regex fast-path ───────────────────────────────────────────

METRIC_ALIASES = {
    "temperature": ["temperature", "temp", "heat", "thermal"],
    "pressure":    ["pressure", "psi", "bar", "pascal"],
    "vibration":   ["vibration", "vibe", "vibrate"],
    "rpm":         ["rpm", "rotation", "speed", "revolutions"],
    "current":     ["current", "amps", "ampere"],
    "voltage":     ["voltage", "volts", "volt"],
    "humidity":    ["humidity", "humid"],
    "flow":        ["flow", "flow rate", "flowrate"],
}

UNIT_ALIASES = {
    "°c": ["°c","celsius","degrees","deg c","c"],
    "°f": ["°f","fahrenheit","deg f","f"],
    "bar": ["bar","bars"],
    "psi": ["psi"],
    "mm/s": ["mm/s","mm per second"],
    "rpm":  ["rpm"],
    "a":    ["amps","ampere","a"],
    "v":    ["volts","v","voltage"],
    "%":    ["%","percent","percentage"],
}

NUMBER_PATTERN = re.compile(r"[-+]?\d*\.?\d+")
ASSET_PATTERN  = re.compile(r"\b([A-Z]{1,3}\d{1,4})\b", re.IGNORECASE)


def _find_metric(text: str) -> str | None:
    lower = text.lower()
    for metric, aliases in METRIC_ALIASES.items():
        if any(a in lower for a in aliases):
            return metric
    return None


def _find_unit(text: str) -> str:
    lower = text.lower()
    for unit, aliases in UNIT_ALIASES.items():
        if any(a in lower for a in aliases):
            return unit
    return ""


def _find_value(text: str) -> float | None:
    matches = NUMBER_PATTERN.findall(text)
    if matches:
        return float(matches[0])
    return None


def _find_asset(text: str) -> str | None:
    match = ASSET_PATTERN.search(text)
    return match.group(1).upper() if match else None


def parse_telemetry_fast(text: str) -> dict | None:
    """
    Fast regex-based parser. Returns structured reading or None if unclear.
    """
    asset_id = _find_asset(text)
    metric   = _find_metric(text)
    value    = _find_value(text)
    unit     = _find_unit(text)

    if asset_id and metric and value is not None:
        return {
            "asset_id": asset_id,
            "metric":   metric,
            "value":    value,
            "unit":     unit,
        }
    return None


def parse_telemetry_llm(text: str) -> dict | None:
    """
    LLM fallback for ambiguous telemetry messages.
    """
    system = """You parse worker messages about machine sensor readings.
Extract structured data. Reply ONLY with valid JSON.

Schema: {"asset_id": string or null, "metric": string, "value": float, "unit": string}

Metric options: temperature, pressure, vibration, rpm, current, voltage, humidity, flow
Unit: use standard symbols (°C, °F, bar, PSI, mm/s, RPM, A, V, %)
If asset_id not found use null.

Examples:
"M14 temp is 67 degrees"     → {"asset_id":"M14","metric":"temperature","value":67,"unit":"°C"}
"pressure 280 bar on press"  → {"asset_id":null,"metric":"pressure","value":280,"unit":"bar"}
"M37 RPM reading 1450"       → {"asset_id":"M37","metric":"rpm","value":1450,"unit":"RPM"}
"""
    try:
        import json, re as _re
        raw    = chat_json(system, text, max_tokens=100)
        raw    = _re.sub(r"```json|```", "", raw).strip()
        result = json.loads(raw)
        if "metric" in result and "value" in result:
            return result
    except Exception as e:
        print(f"[telemetry] LLM parse failed: {e}")
    return None


def parse_telemetry(text: str) -> dict | None:
    """
    Try fast path first, fall back to LLM.
    """
    result = parse_telemetry_fast(text)
    if result:
        return result
    return parse_telemetry_llm(text)


def store_reading(asset_id: str, metric: str, value: float,
                  unit: str = "", source: str = "whatsapp") -> None:
    """Persist a telemetry reading to cv.detections as a sensor event."""
    import json
    execute(
        """INSERT INTO cv.detections
           (detection_id, asset_id, object, condition, confidence, source, raw_json)
           VALUES (?,?,?,?,?,?,?)""",
        (str(uuid.uuid4()), asset_id.upper(),
         f"{metric.capitalize()} reading",
         f"{metric} = {value}{unit}",
         1.0, source,
         json.dumps({"metric": metric, "value": value, "unit": unit})),
    )


def check_threshold(value: float, metric: str, asset_type: str = "default") -> dict:
    thresholds = {
        "temperature": {"default": 80, "pump": 70, "motor": 75},
        "pressure": {"default": 120, "pump": 100, "motor": 110},
        "vibration": {"default": 4.0, "pump": 3.5, "motor": 3.8},
        "rpm": {"default": 1800, "pump": 1600, "motor": 1700},
        "current": {"default": 50, "pump": 45, "motor": 48},
        "voltage": {"default": 240, "pump": 230, "motor": 235},
        "humidity": {"default": 80, "pump": 75, "motor": 78},
        "flow": {"default": 100, "pump": 90, "motor": 95},
    }
    limit = thresholds.get(metric, {}).get(asset_type.lower(), thresholds.get(metric, {}).get("default", 100))
    ok = value <= limit
    status = "ok" if ok else "alert"
    return {"ok": ok, "status": status, "limit": limit}


def analyse_readings(values: list[float], metric: str, asset_id: str = "", unit: str = "") -> dict:
    if not values:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "trend": "stable", "status": "ok"}
    mean = sum(values) / len(values)
    minimum = min(values)
    maximum = max(values)
    if len(values) >= 2:
        delta = values[0] - values[-1]
        trend = "rising" if delta > 0 else "falling" if delta < 0 else "stable"
    else:
        trend = "stable"
    status = "ok"
    return {
        "mean": round(mean, 2),
        "min": round(minimum, 2),
        "max": round(maximum, 2),
        "trend": trend,
        "status": status,
    }


def summarise_telemetry_for_asset(asset_id: str) -> dict:
    """Return the last 10 sensor readings for an asset, extracted from cv.detections."""
    import json
    from core.db import query
    rows = query(
        """SELECT object, condition, raw_json, timestamp FROM cv.detections
           WHERE asset_id=? AND source LIKE 'whatsapp%%'
           ORDER BY timestamp DESC LIMIT 10""",
        (asset_id.upper(),)
    )

    if not rows:
        return {"reply": "No telemetry readings found for this asset."}
    lines = [f"📡 *Telemetry — {asset_id.upper()}*"]
    for r in rows:
        try:
            rj = r.get("raw_json")
            d = json.loads(rj) if isinstance(rj, str) else (rj or {})
            metric = d.get("metric", r["object"])
            value  = d.get("value", "?")
            unit   = d.get("unit", "")
            ts     = str(r.get("timestamp", ""))[:16]
            lines.append(f"• {metric}: {value}{unit} @ {ts}")
        except Exception:
            lines.append(f"• {r['condition']}")
    return {"reply": "\n".join(lines)}


def convert_unit(value: float, frm: str, to: str) -> dict:
    frm = frm.lower().strip()
    to = to.lower().strip()
    
    # Map synonyms to canonical short forms
    unit_map = {
        "celsius": "c", "c": "c", "°c": "c",
        "fahrenheit": "f", "f": "f", "°f": "f",
        "bar": "bar", "bars": "bar",
        "psi": "psi",
        "mm": "mm",
        "cm": "cm",
        "m": "m", "meter": "m", "meters": "m"
    }
    
    u_from = unit_map.get(frm)
    u_to = unit_map.get(to)
    
    if not u_from or not u_to:
        return {"error": f"Unknown units: {frm} or {to}."}
        
    conversions = {
        ("c", "f"): lambda v: (v * 9 / 5) + 32,
        ("f", "c"): lambda v: (v - 32) * 5 / 9,
        ("bar", "psi"): lambda v: v * 14.5038,
        ("psi", "bar"): lambda v: v / 14.5038,
        ("mm", "cm"): lambda v: v / 10.0,
        ("cm", "mm"): lambda v: v * 10.0,
        ("cm", "m"): lambda v: v / 100.0,
        ("m", "cm"): lambda v: v * 100.0,
    }
    
    key = (u_from, u_to)
    if key in conversions:
        converted = conversions[key](value)
        return {"reply": f"{value} {frm} = {converted:.2f} {to}"}
    
    return {"error": f"Cannot convert {frm} to {to}."}
