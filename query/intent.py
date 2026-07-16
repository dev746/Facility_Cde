import re
import json
from core.llm import chat_json

SYSTEM = """You are the intent parser for an industrial MSME facility management system.
Workers send natural language messages — in English, Hindi, or Hinglish — about machines, defects, inspections, and quality checks.

Extract intent and asset reference. Reply ONLY with valid JSON.

Output schema:
{"intent": string, "asset_id": string or null, "filters": {"severity": string or null, "source": string or null}}

Intent definitions:
  machine     → info about an asset: type, location, specs, status
  findings    → defects, faults, anomalies, issues, detections
  notes       → expert annotations, engineer comments, recommendations
  summary     → full status overview for a machine
  list        → enumerate all assets or filter by type/line/zone
  critical    → high-confidence or high-severity findings across facility
  latest      → most recent findings or inspections
  ask         → open question needing document/manual search
  image       → request for a CV output image
  addnote     → user wants to record an observation or note
  report      → user is reporting a new fault or field observation
  search      → keyword search across all findings
  linestatus  → status of a production line
  adduser     → register a new worker
  removeuser  → deactivate a worker
  listusers   → show registered workers
  help        → available commands
  unknown     → cannot determine

asset_id rules:
  - Extract codes like M14, BATCH1, LINE3 — always uppercase
  - Machine names ("hydraulic press", "cnc lathe") → null, resolver handles it
  - If no asset → null

severity filter: extract if user says critical/urgent/severe/high/minor/low
source filter: extract if user says CV/batch/field report/inspection

Examples:
"what's wrong with M14"               → {"intent":"findings","asset_id":"M14","filters":{}}
"M14 ki kya problem hai"              → {"intent":"findings","asset_id":"M14","filters":{}}
"location of cnc lathe"               → {"intent":"machine","asset_id":null,"filters":{}}
"hydraulic press kahan hai"           → {"intent":"machine","asset_id":null,"filters":{}}
"show batch 2 defects"                → {"intent":"findings","asset_id":"BATCH2","filters":{}}
"critical issues on line 3"           → {"intent":"critical","asset_id":"LINE3","filters":{"severity":"critical"}}
"kaun si machine critical hai"        → {"intent":"critical","asset_id":null,"filters":{}}
"conveyor belt ka summary do"         → {"intent":"summary","asset_id":null,"filters":{}}
"latest findings M37"                 → {"intent":"latest","asset_id":"M37","filters":{}}
"show batch 1 image"                  → {"intent":"image","asset_id":"BATCH1","filters":{}}
"add note M22 bearing replaced today" → {"intent":"addnote","asset_id":"M22","filters":{}}
"report M14 oil leak near spindle"    → {"intent":"report","asset_id":"M14","filters":{}}
"search bearing wear"                 → {"intent":"search","asset_id":null,"filters":{}}
"how to maintain hydraulic pump"      → {"intent":"ask","asset_id":null,"filters":{}}
"line A status"                       → {"intent":"linestatus","asset_id":null,"filters":{}}
"kya karo agar M14 band ho jaye"      → {"intent":"ask","asset_id":"M14","filters":{}}
"help"                                → {"intent":"help","asset_id":null,"filters":{}}"""

KEYWORDS = {
    "machine":    ["machine", "asset", "show", "info", "location", "where", "type",
                   "details", "equipment", "lathe", "press", "conveyor", "kahan", "kya hai"],
    "findings":   ["finding", "defect", "issue", "wrong", "fault", "problem", "damage",
                   "crack", "leak", "wear", "broken", "detect", "problem", "kya problem"],
    "notes":      ["note", "expert", "annotation", "comment", "recommendation"],
    "summary":    ["summary", "overview", "status", "condition", "ka summary"],
    "list":       ["list", "all machines", "all assets", "show all"],
    "critical":   ["critical", "urgent", "severe", "high priority", "critical hai"],
    "latest":     ["latest", "recent", "last inspection", "newest"],
    "ask":        ["how", "what is", "explain", "manual", "procedure", "kya karo", "kaise"],
    "image":      ["image", "photo", "picture", "visual", "output image", "show image"],
    "search":     ["search", "find", "look for", "dhundho"],
    "linestatus": ["line status", "line a", "line b", "line c", "production line"],
    "addnote":    ["addnote", "add note"],
    "report":     ["report", "log issue", "submit"],
    "adduser":    ["adduser", "add user"],
    "removeuser": ["removeuser", "remove user"],
    "listusers":  ["listusers", "list users"],
    "help":       ["help", "commands"],
}

ASSET_PATTERN = re.compile(r'\b([A-Z]{1,3}\d{1,4})\b', re.IGNORECASE)


def _keyword_parse(text: str) -> dict:
    lower = text.lower()
    match = ASSET_PATTERN.search(text)
    asset_id = match.group(1).upper() if match else None
    for intent, words in KEYWORDS.items():
        if any(w in lower for w in words):
            return {"intent": intent, "asset_id": asset_id, "filters": {}}
    if asset_id:
        return {"intent": "machine", "asset_id": asset_id, "filters": {}}
    return {"intent": "unknown", "asset_id": None, "filters": {}}


def parse_intent(text: str) -> dict:
    try:
        raw    = chat_json(SYSTEM, text, max_tokens=128)
        raw    = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(raw)
        if "intent" not in result:
            return _keyword_parse(text)
        result.setdefault("filters", {})
        return result
    except Exception as e:
        print(f"[intent] LLM failed ({e}), keyword fallback")
        return _keyword_parse(text)
