"""
One-time seeder. Run after first install.
PYTHONPATH=. python seed_data.py
"""
import json
import uuid
import shutil
from pathlib import Path
from core.schema import db_init
from core.db import execute

db_init()

SAMPLES = Path("data/samples")
INBOX   = Path("data/inbox")

# ── Sample JSON files ─────────────────────────────────────────

BATCH1 = {
    "batch_number": 1, "cm_per_pixel": 0.10583867704109558, "total_scraps": 3,
    "scraps": [
        {"id":1,"piece_name":"square_1","shape_type":"square","vertices_count":4,
         "vertex_labels":{"A":[185,367],"B":[183,394],"C":[214,398],"D":[217,371]},
         "side_lengths_cm":{"AB":2.87,"BC":3.31,"CD":2.88,"DA":3.41},"area_cm2":11.15},
        {"id":2,"piece_name":"rectangle_1","shape_type":"rectangle","vertices_count":4,
         "vertex_labels":{"A":[351,220],"B":[347,289],"C":[397,293],"D":[400,224]},
         "side_lengths_cm":{"AB":7.32,"BC":5.31,"CD":7.31,"DA":5.2},"area_cm2":40.53},
        {"id":3,"piece_name":"triangle_1","shape_type":"triangle","vertices_count":3,
         "vertex_labels":{"A":[268,251],"B":[256,200],"C":[153,222]},
         "side_lengths_cm":{"AB":5.55,"BC":11.15,"CA":12.55},"area_cm2":36.95},
    ]
}

BATCH2 = {
    "batch_number": 2, "cm_per_pixel": 0.10421311648724584, "total_scraps": 5,
    "scraps": [
        {"id":1,"piece_name":"irregular_1","shape_type":"irregular","vertices_count":6,
         "vertex_labels":{"A":[131,335],"B":[128,351],"C":[172,363],"D":[162,416],"E":[177,420],"F":[197,350]},
         "side_lengths_cm":{"AB":1.7,"BC":4.75,"CD":5.62,"DE":1.62,"EF":7.59,"FA":7.05},"area_cm2":25.18},
        {"id":2,"piece_name":"irregular_2","shape_type":"irregular","vertices_count":8,
         "vertex_labels":{"A":[384,322],"B":[364,336],"C":[361,362],"D":[381,383],
                          "E":[403,384],"F":[421,367],"G":[423,344],"H":[411,329]},
         "side_lengths_cm":{"AB":2.54,"BC":2.73,"CD":3.02,"DE":2.3,"EF":2.58,"FG":2.41,"GH":2.0,"HA":2.91},"area_cm2":33.7},
        {"id":3,"piece_name":"circle_1","shape_type":"circle","vertices_count":7,
         "vertex_labels":{"A":[268,300],"B":[253,305],"C":[249,312],"D":[248,323],"E":[260,334],"F":[273,330],"G":[280,308]},
         "side_lengths_cm":{"AB":1.65,"BC":0.84,"CD":1.15,"DE":1.7,"EF":1.42,"FG":2.41,"GA":1.5},"area_cm2":8.87},
        {"id":4,"piece_name":"irregular_3","shape_type":"irregular","vertices_count":5,
         "vertex_labels":{"A":[144,220],"B":[128,230],"C":[128,236],"D":[160,273],"E":[163,242]},
         "side_lengths_cm":{"AB":1.97,"BC":0.63,"CD":5.1,"DE":3.25,"EA":3.03},"area_cm2":11.12},
        {"id":5,"piece_name":"irregular_4","shape_type":"irregular","vertices_count":6,
         "vertex_labels":{"A":[311,212],"B":[301,258],"C":[362,269],"D":[370,214],"E":[342,229],"F":[334,216]},
         "side_lengths_cm":{"AB":4.91,"BC":6.46,"CD":5.79,"DE":3.31,"EF":1.59,"FA":2.43},"area_cm2":31.36},
    ]
}

M14 = {
    "asset_id":"M14","asset_type":"CNC Lathe","location":"Bay 2, Line A",
    "timestamp":"2024-12-01T08:30:00Z",
    "detections":[
        {"object":"Bearing","condition":"Wear detected","confidence":0.92},
        {"object":"Spindle housing","condition":"Hairline crack","confidence":0.87},
        {"object":"Oil seal","condition":"Minor leak","confidence":0.74},
    ]
}

M22 = {
    "asset_id":"M22","asset_type":"Hydraulic Press","location":"Bay 4, Line B",
    "timestamp":"2024-12-02T11:15:00Z",
    "detections":[
        {"object":"Hydraulic cylinder","condition":"Pressure drop","confidence":0.89},
        {"object":"Piston rod","condition":"Surface corrosion","confidence":0.81},
    ]
}

M37 = {
    "asset_id":"M37","asset_type":"Conveyor Belt","location":"Bay 1, Line C",
    "timestamp":"2024-12-03T09:00:00Z",
    "detections":[
        {"object":"Belt tension roller","condition":"Misalignment","confidence":0.66},
        {"object":"Drive motor","condition":"Overheating","confidence":0.91},
    ]
}

ANNOTATIONS = {
    "asset_id":"M14","source":"cv_tracking",
    "track_1":{
        "track_id":1,"label":"board","category":"furniture","class_name":"tv",
        "frame_id":240,"area":12750.5,"bbox":[284,91,137,113],"centroid":[350,147],
        "angle":-3.4,"saved_at":"2026-06-04T10:07:42.628Z","notes":""
    },
    "track_23":{
        "track_id":23,"label":"","category":"unknown","class_name":"chair",
        "frame_id":200,"area":2625,"bbox":[514,190,37,121],"centroid":[531,240],
        "angle":-89.5,"saved_at":"2026-06-04T09:30:29.609Z","notes":""
    },
}

# write sample files
for name, data in [("batch_1.json",BATCH1),("batch_2.json",BATCH2),
                    ("M14.json",M14),("M22.json",M22),("M37.json",M37),
                    ("annotations.json",ANNOTATIONS)]:
    p = SAMPLES / name
    p.write_text(json.dumps(data, indent=2))
    shutil.copy(p, INBOX / name)

print(f"[seed] {len(list(INBOX.glob('*.json')))} JSON files copied to inbox/")

# run watcher
from ingestion.watcher import scan_inbox
result = scan_inbox()
print(f"[seed] watcher: {result}")

# expert notes
notes = [
    ("M14","Bearing replacement scheduled for next maintenance window.","Priya Sharma"),
    ("M14","Crack on spindle housing flagged — monitor closely.","Arjun Mehta"),
    ("M22","Hydraulic fluid topped up. Pressure drop persists — investigate cylinder seal.","Priya Sharma"),
    ("M37","Drive motor thermal trip recorded twice this week. Priority review.","Ravi Kumar"),
]
for asset_id, comment, author in notes:
    execute(
        """INSERT INTO core.expert_notes (note_id, asset_id, comment, author)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT (note_id) DO NOTHING""",
        (str(uuid.uuid4()), asset_id, comment, author),
    )
print(f"[seed] {len(notes)} expert notes seeded")
print("\nDone. Run: PYTHONPATH=. python terminal_chat.py")
