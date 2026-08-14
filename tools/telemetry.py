"""
Parses unstructured worker messages into structured telemetry readings.
Workers type things like:
  "M14 temperature 45 degrees"
  "pressure on hydraulic press is 280 bar"
  "M22 vibration 3.2 mm/s RPM 1450"
This module extracts asset_id, metric, value, unit from that text.
"""
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


def handle_telemetry_message(text: str, user: dict) -> str:
    """
    Full pipeline: parse → validate → store → analyse → reply.
    Called from commands.dispatch() when intent == 'telemetry'.
    """
    from core.db import query
    from tools.calculator import check_threshold, analyse_readings

    reading = parse_telemetry(text)

    if not reading:
        return (
            "❓ Could not parse your reading.\n"
            "Try: *M14 temperature 67 degrees*\n"
            "Or:  *pressure 280 bar*"
        )

    asset_id = reading.get("asset_id")
    metric   = reading["metric"]
    value    = float(reading["value"])
    unit     = reading.get("unit", "")

    # if no asset_id in message, ask for it
    if not asset_id:
        return (
            f"📡 Got reading: *{metric} = {value}{unit}*\n"
            f"Which machine? Reply: *M14 {metric} {value}{unit}*"
        )

    # check asset exists
    rows = query("SELECT type FROM core.assets WHERE asset_id=?", (asset_id,))
    asset_type = rows[0]["type"] if rows else "default"

    # store it
    store_reading(asset_id, metric, value, unit, source=f"whatsapp_{user['role']}")

    # threshold check
    check = check_threshold(value, metric, asset_type)

    # pull last 10 readings for trend
    history = query(
        """SELECT raw_json FROM cv.detections
           WHERE asset_id=? AND object=?
           ORDER BY timestamp DESC LIMIT 10""",
        (asset_id, f"{metric.capitalize()} reading"),
    )
    import json
    vals = []
    for r in history:
        try:
            rj = r.get("raw_json")
            d = json.loads(rj) if isinstance(rj, str) else (rj or {})
            if "value" in d:
                vals.append(float(d["value"]))
        except Exception:
            pass

    lines = [
        f"📡 *Recorded — {asset_id}*",
        f"Metric: {metric.capitalize()}",
        f"Value:  {value}{unit}",
        f"Status: {check['status']}",
    ]

    if len(vals) >= 3:
        analysis = analyse_readings(vals, metric, asset_type, unit)
        lines.append(f"Trend:  {analysis['trend']}")

    if not check["ok"]:
        lines.append(f"\n⚠️ Alert sent to experts.")
        # auto-create a finding for threshold breach
        import uuid as _uuid
        from ingestion.canonical import _severity
        conf = 0.95
        execute = __import__("core.db", fromlist=["execute"]).execute
        execute(
            """INSERT INTO cv.detections
               (detection_id, asset_id, object, condition, confidence, source)
               VALUES (?,?,?,?,?,?)""",
            (str(_uuid.uuid4()), asset_id,
             f"{metric.capitalize()} alert",
             f"{metric} = {value}{unit} — {check['status']}",
             conf, "telemetry_alert"),
        )

    return "\n".join(lines)
