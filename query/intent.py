import re
import json
from core.llm import chat_json

SYSTEM = """You are the intent parser for an industrial MSME facility management system.
Workers send messages in English, Hindi, Hinglish, Kannada about machines, defects, inspections, and sensor readings.

Extract intent and asset reference. Reply ONLY with valid JSON.

Output schema:
{"intent": string, "asset_id": string or null, "filters": {"severity": string or null, "source": string or null}}

Intent definitions:
  machine     -> info about an asset: type, location, specs, status
  findings    -> defects, faults, anomalies, issues, detections
  notes       -> expert annotations, engineer comments
  summary     -> full status overview for a machine
  list        -> enumerate all assets
  critical    -> high-severity findings across facility
  latest      -> most recent findings
  ask         -> open question needing document search
  image       -> request for CV output image
  telemetry   -> worker is reporting a sensor reading (temperature, pressure, RPM, vibration etc.)
  calculate   -> worker wants analysis or calculation on telemetry data
  convert     -> unit conversion request (celsius to fahrenheit, bar to PSI etc.)
  addnote     -> user wants to record a note
  report      -> user is reporting a new fault
  search      -> keyword search across findings
  linestatus  -> status of a production line
  adduser     -> register a new worker
  removeuser  -> deactivate a worker
  listusers   -> show registered workers
  help        -> available commands
  unknown     -> cannot determine

asset_id: codes like M14, BATCH1 uppercase. Names -> null.

Examples:
"M14 temperature 67 degrees"          -> {"intent":"telemetry","asset_id":"M14","filters":{}}
"pressure on M22 is 280 bar"          -> {"intent":"telemetry","asset_id":"M22","filters":{}}
"analyse M14 temperature readings"    -> {"intent":"calculate","asset_id":"M14","filters":{}}
"convert 45 celsius to fahrenheit"    -> {"intent":"convert","asset_id":null,"filters":{}}
"M14 ki kya problem hai"              -> {"intent":"findings","asset_id":"M14","filters":{}}
"critical issues on line 3"           -> {"intent":"critical","asset_id":"LINE3","filters":{"severity":"critical"}}
"show batch 1 image"                  -> {"intent":"image","asset_id":"BATCH1","filters":{}}
"help"                                -> {"intent":"help","asset_id":null,"filters":{}}"""

KEYWORDS = {
    # Specific commands first
    "addnote":    ["addnote", "add note"],
    "report":     ["report", "log issue", "submit fault"],
    "adduser":    ["adduser", "add user"],
    "removeuser": ["removeuser", "remove user"],
    "listusers":  ["listusers", "list users"],
    "help":       ["help", "commands", "sahayata"],
    "linestatus": ["line status", "line a", "line b", "line c", "production line"],
    "critical":   ["critical", "urgent", "severe", "high priority", "gambhir"],
    "latest":     ["latest", "recent", "last inspection", "newest", "haal hi"],
    "list":       ["list", "all machines", "all assets", "show all", "sabhibhi", "yantragalu"],
    "convert":    ["convert", "conversion", "to fahrenheit", "to celsius", "to psi", "to bar"],
    "calculate":  ["analyse", "analyze", "analysis", "calculate", "stats", "statistics", "average", "mean", "trend", "min", "max"],
    "telemetry":  ["temperature", "temp", "pressure", "vibration", "rpm", "rotation", "current", "voltage", "humidity", "flow", "reading", "sensor", "degrees", "bar", "psi", "taapman"],
    "image":      ["image", "photo", "picture", "visual", "output image", "chhavi", "chitra"],
    "findings":   ["finding", "defect", "issue", "wrong", "fault", "problem", "damage", "crack", "leak", "kharab", "kharrab", "bhadh", "dosa", "samase", "shikayat"],
    "notes":      ["note", "annotation", "recommendation", "tippani"],
    "summary":    ["summary", "overview", "status", "condition", "sthiti", "saransh", "vivaran"],
    "search":     ["search", "find", "look for", "dhundho", "hudu"],
    "machine":    ["machine", "asset", "show", "info", "location", "where", "type", "equipment", "kahan", "yantra", "kahan hai"],
    "ask":        ["how many", "how", "explain", "manual", "procedure", "kya karo", "kaise", "hege", "shift", "insight", "logged", "count", "total", "expert", "comment"],
}

ASSET_PATTERN = re.compile(r'\b([A-Z]{1,5}\d{1,4}|BATCH\d+|LINE\d+|SCRAP\d+)\b', re.IGNORECASE)
FILLER_WORDS = {
    "where", "is", "the", "what", "how", "show", "me", "find", "get", "of", "on", "in", "for",
    "kahan", "hai", "kya", "kaise", "kab", "ko", "ki", "par", "se", "yantrada", "enu", "kodi",
    "please", "can", "you", "tell", "status", "info", "problem", "issue", "detail", "details"
}


def extract_asset_name(text: str) -> str | None:
    """Strips common query filler and command words to extract potential asset name phrase."""
    match = ASSET_PATTERN.search(text)
    if match:
        return match.group(1).upper()
        
    words = re.findall(r'\w+', text, re.UNICODE)
    cleaned = [w for w in words if w.lower() not in FILLER_WORDS and not w.isdigit()]
    if cleaned:
        return " ".join(cleaned)
    return None


def _keyword_parse(text: str) -> dict:
    lower = text.lower()
    match = ASSET_PATTERN.search(text)
    asset_id = match.group(1).upper() if match else None
    
    extracted_name = None if asset_id else extract_asset_name(text)
    
    found_intent = None
    for intent, words in KEYWORDS.items():
        if any(w in lower for w in words):
            found_intent = intent
            break
            
    if not found_intent:
        if asset_id or extracted_name:
            found_intent = "machine"
        else:
            found_intent = "unknown"
            
    res = {"intent": found_intent, "asset_id": asset_id, "filters": {}}
    if extracted_name and not asset_id:
        res["raw_asset_name"] = extracted_name
    return res


def parse_intent(text: str) -> dict:
    try:
        raw = chat_json(SYSTEM, text, max_tokens=512)
        raw = re.sub(r"```json|```", "", raw).strip()
        if not raw:
            raise ValueError("empty LLM response")
        result = json.loads(raw)
        if "intent" not in result:
            return _keyword_parse(text)
        result.setdefault("filters", {})
        
        # If asset_id missing, attempt extraction
        if not result.get("asset_id"):
            extracted = extract_asset_name(text)
            if extracted:
                if ASSET_PATTERN.match(extracted):
                    result["asset_id"] = extracted.upper()
                else:
                    result["raw_asset_name"] = extracted
                    
        return result
    except Exception as e:
        print(f"[intent] LLM failed ({e}), keyword fallback")
        return _keyword_parse(text)

