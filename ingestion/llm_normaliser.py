import json
import re
from core.llm import chat_json
from ingestion.canonical import make_asset, make_finding

SYSTEM = """You are a data normalisation engine for an industrial MSME facility CDE.

Map arbitrary input data to the standard schema.

TARGET SCHEMA:
assets:   asset_id (TEXT uppercase no spaces), name, type, location
findings: asset_id, object (component/item name), condition (what is observed),
          confidence (REAL 0.0-1.0), source (module name)

RULES:
- asset_id must be short, uppercase, no spaces: M14 not "Machine 14"
- confidence: 1.0 for measurements, 0.9 for high-conf CV, 0.5 if unknown
- object: the component detected (e.g. "Bearing", "Track 1 board", "Square scrap")
- condition: human-readable observation with measurements if available
- Every finding MUST have an asset_id matching an asset in the assets list
- Reply with ONLY a JSON object, no markdown

OUTPUT FORMAT:
{"assets":[{"asset_id":"...","name":"...","type":"...","location":"..."}],
 "findings":[{"asset_id":"...","object":"...","condition":"...","confidence":0.5,"source":"..."}]}"""


def llm_normalise(data) -> tuple:
    try:
        sample = json.dumps(data)[:3000]
        raw    = chat_json(SYSTEM, f"Normalise this data:\n{sample}", max_tokens=1024)
        raw    = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(raw)
        assets   = [make_asset(**a) for a in result.get("assets", [])]
        findings = [make_finding(**f) for f in result.get("findings", [])]
        return assets, findings
    except Exception as e:
        print(f"[llm_normalise] failed: {e}")
        return [], []
