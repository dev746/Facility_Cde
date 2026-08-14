"""
Seed a few realistic test assets into core.assets so fuzzy name
matching (pg_trgm) and the asset_summary view can be exercised
through terminal_chat.py without needing real ingestion files.
"""
from core.db import execute

ASSETS = [
    ("M04",  "Hydraulic Press #4",  "Hydraulic Press",  "Bay 3, Line B"),
    ("M08",  "Conveyor Belt M08",   "Conveyor Belt",    "Bay 1, Line A"),
    ("M12",  "CNC Milling M12",     "CNC Mill",         "Bay 2, Line A"),
]

for asset_id, name, type_, location in ASSETS:
    execute(
        """INSERT INTO core.assets (asset_id, name, type, location)
           VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
        (asset_id, name, type_, location),
    )
    print(f"  seeded: {asset_id} — {name}")

print("Done. Run 'list' in terminal_chat to verify.")
