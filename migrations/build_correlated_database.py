"""
Database Builder & Knowledge Correlation SQL Dump Generator for Facility CDE v2.
Populates PostgreSQL with all schemas, tables, multi-medium data, expert notes, users,
and cross-schema knowledge correlations, then dumps the full database to a SQL file.
"""
import os
import json
import uuid
import sqlite3
import subprocess
from pathlib import Path
import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:Wegro26@localhost:5432/FACILITY1.DB")
PG_DUMP_PATH = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

def build_database_and_export_sql():
    print("[1/6] Connecting to PostgreSQL...")
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    # Step 0: Clean schema drop to guarantee a fresh build
    print("[1.5/6] Resetting PostgreSQL schemas for clean build...")
    cur.execute("""
        DROP SCHEMA IF EXISTS core, auth, cv, scrap, geometry, bim, rag, comms, ingest CASCADE;
    """)
    conn.commit()

    # Step 1: Run DDL Migrations
    print("[2/6] Applying DDL migrations (001_init, 002_cross_schema_integration, 003_add_status_column)...")
    migrations_dir = Path("migrations")
    for migration_file in sorted(migrations_dir.glob("*.sql")):
        print(f"  Applying {migration_file.name}...")
        sql = migration_file.read_text(encoding="utf-8")
        cur.execute(sql)
        conn.commit()

    # Step 2: Seed Users
    print("[3/6] Populating auth.users...")
    users = [
        ("+919876543210", "Priya Sharma", "expert", True),
        ("+919876543211", "Arjun Mehta", "technician", True),
        ("+919876543212", "Ravi Kumar", "technician", True),
        ("+919876543213", "System Admin", "admin", True),
        ("+919876543214", "Quality Inspector", "viewer", True),
    ]
    for phone, name, role, active in users:
        cur.execute("""
            INSERT INTO auth.users (phone, name, role, is_active)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (phone) DO UPDATE SET name=EXCLUDED.name, role=EXCLUDED.role
        """, (phone, name, role, active))
    conn.commit()

    # Step 3: Populate Assets & Domain Data (CV, Scrap, Expert Notes)
    print("[4/6] Ingesting and normalizing domain datasets...")

    # Core Assets
    assets = [
        ("M14", "CNC Lathe #14", "CNC Lathe", "Bay 2, Line A", "active", "Line A", "Bay 2"),
        ("M22", "Hydraulic Press #22", "Hydraulic Press", "Bay 4, Line B", "active", "Line B", "Bay 4"),
        ("M37", "Conveyor Belt #37", "Conveyor Belt", "Bay 1, Line C", "active", "Line C", "Bay 1"),
        ("SESSION_001", "CV Tracking Session 001", "cv_tracking", "Bay 2, Line A", "active", "Line A", "Bay 2"),
        ("SESSION_002", "Scrap Session 002", "scrap_measurement", "Bay 4, Line B", "active", "Line B", "Bay 4"),
        ("SESSION_003", "Scrap Session 003", "scrap_measurement", "Bay 3, Line A", "active", "Line A", "Bay 3"),
        ("SESSION_004", "Scrap Session 004", "scrap_measurement", "Bay 3, Line B", "active", "Line B", "Bay 3"),
        ("SESSION_005", "Scrap Session 005", "scrap_measurement", "Bay 1, Line C", "active", "Line C", "Bay 1"),
        ("BATCH1", "Scrap Batch 1", "scrap_batch", "Bay 2, Line A", "active", "Line A", "Bay 2"),
        ("BATCH2", "Scrap Batch 2", "scrap_batch", "Bay 4, Line B", "active", "Line B", "Bay 4"),
        ("BATCH3", "Scrap Batch 3", "scrap_batch", "Bay 3, Line A", "active", "Line A", "Bay 3"),
        ("BATCH4", "Scrap Batch 4", "scrap_batch", "Bay 3, Line B", "active", "Line B", "Bay 3"),
        ("BATCH5", "Scrap Batch 5", "scrap_batch", "Bay 1, Line C", "active", "Line C", "Bay 1"),
    ]
    for aid, name, atype, loc, status, line, zone in assets:
        cur.execute("""
            INSERT INTO core.assets (asset_id, name, type, location, status, line, zone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (asset_id) DO UPDATE SET
                name=EXCLUDED.name, type=EXCLUDED.type, location=EXCLUDED.location,
                status=EXCLUDED.status, line=EXCLUDED.line, zone=EXCLUDED.zone
        """, (aid, name, atype, loc, status, line, zone))
    conn.commit()

    # Migrate legacy SQLite if present
    if os.path.exists("facility.db"):
        print("  Migrating legacy SQLite facility.db records...")
        old = sqlite3.connect("facility.db")
        old.row_factory = sqlite3.Row
        for row in old.execute("SELECT * FROM assets"):
            cur.execute("""
                INSERT INTO core.assets (asset_id, name, type, location, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (asset_id) DO NOTHING
            """, (row["asset_id"], row["name"], row["type"], row["location"], str(row["created_at"]) if row["created_at"] else None))
        
        for row in old.execute("SELECT * FROM findings"):
            cur.execute("""
                INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, timestamp, raw_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (str(uuid.uuid4()), row["asset_id"], row["object"], row["condition"], row["confidence"],
                  row["source"] or "legacy_sqlite", str(row["timestamp"]) if row["timestamp"] else None, str(row["raw_json"]) if row["raw_json"] else None))
        
        for row in old.execute("SELECT * FROM expert_notes"):
            cur.execute("""
                INSERT INTO core.expert_notes (note_id, asset_id, comment, author)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (note_id) DO NOTHING
            """, (str(uuid.uuid4()), row["asset_id"], row["comment"], row["author"]))
        old.close()
        conn.commit()

    # Seed expert notes
    notes = [
        ("M14", "Bearing replacement scheduled for next maintenance window.", "+919876543210"),
        ("M14", "Crack on spindle housing flagged — monitor closely.", "+919876543211"),
        ("M22", "Hydraulic fluid topped up. Pressure drop persists — investigate cylinder seal.", "+919876543210"),
        ("M37", "Drive motor thermal trip recorded twice this week. Priority review.", "+919876543212"),
    ]
    for aid, comment, author in notes:
        cur.execute("""
            INSERT INTO core.expert_notes (note_id, asset_id, comment, author)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (str(uuid.uuid4()), aid, comment, author))
    conn.commit()

    # Ingest CV detections (M14, M22, M37 sample files)
    samples_dir = Path("data/samples")
    for mfile in ["M14.json", "M22.json", "M37.json"]:
        p = samples_dir / mfile
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            aid = data["asset_id"]
            ts = data.get("timestamp")
            for det in data.get("detections", []):
                cur.execute("""
                    INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, timestamp, raw_json)
                    VALUES (%s, %s, %s, %s, %s, 'cv_module', %s, %s)
                """, (str(uuid.uuid4()), aid, det.get("object"), det.get("condition"), det.get("confidence"), ts, json.dumps(det)))
    conn.commit()

    # Ingest CV annotations / tracks
    ann_file = samples_dir / "annotations.json"
    if ann_file.exists():
        data = json.loads(ann_file.read_text(encoding="utf-8"))
        sess_id = data.get("asset_id", "SESSION_001")
        cur.execute("""
            INSERT INTO cv.sessions (session_id, asset_id, source)
            VALUES (%s, %s, %s)
            ON CONFLICT (session_id) DO NOTHING
        """, (sess_id, "M14", "cv_tracking"))
        
        for k, v in data.items():
            if isinstance(v, dict) and k.startswith("track_"):
                cur.execute("""
                    INSERT INTO cv.tracks (track_pk, track_id, session_id, asset_id, label, category, class_name, frame_id, area, bbox, centroid, angle, notes, saved_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()), v.get("track_id"), sess_id, "M14",
                    v.get("label"), v.get("category"), v.get("class_name"),
                    v.get("frame_id"), v.get("area"), json.dumps(v.get("bbox")),
                    json.dumps(v.get("centroid")), v.get("angle"), v.get("notes"),
                    v.get("saved_at")
                ))
    conn.commit()

    # Ingest all datasets dynamically from data/processed
    processed_dir = Path("data/processed")
    print(f"[4/6] Ingesting and normalizing all datasets in {processed_dir}...")
    for json_file in sorted(processed_dir.glob("*.json")):
        print(f"  Processing {json_file.name}...")
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            
            # 1. Check if it's a CV detection file (contains "detections")
            if "detections" in data:
                aid = data["asset_id"]
                atype = data.get("asset_type")
                loc = data.get("location")
                ts = data.get("timestamp")
                
                # Ensure asset exists in core.assets
                cur.execute("""
                    INSERT INTO core.assets (asset_id, name, type, location)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (asset_id) DO UPDATE SET
                        type=COALESCE(EXCLUDED.type, core.assets.type),
                        location=COALESCE(EXCLUDED.location, core.assets.location)
                """, (aid, f"Asset {aid}", atype, loc))
                
                for det in data.get("detections", []):
                    cur.execute("""
                        INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, timestamp, raw_json)
                        VALUES (%s, %s, %s, %s, %s, 'cv_module', %s, %s)
                    """, (str(uuid.uuid4()), aid, det.get("object"), det.get("condition"), det.get("confidence"), ts, json.dumps(det)))
                print(f"    Loaded {len(data.get('detections', []))} CV detections for asset {aid}")

            # 2. Check if it's a tracking session (contains "track_*" keys or "source": "cv_tracking")
            elif any(k.startswith("track_") for k in data.keys()):
                sess_id = data.get("asset_id", "SESSION_001")
                # Default asset relation for tracking session
                aid = "M14"
                cur.execute("""
                    INSERT INTO cv.sessions (session_id, asset_id, source)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_id) DO NOTHING
                """, (sess_id, aid, "cv_tracking"))
                
                track_count = 0
                for k, v in data.items():
                    if isinstance(v, dict) and k.startswith("track_"):
                        cur.execute("""
                            INSERT INTO cv.tracks (track_pk, track_id, session_id, asset_id, label, category, class_name, frame_id, area, bbox, centroid, angle, notes, saved_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            str(uuid.uuid4()), v.get("track_id"), sess_id, aid,
                            v.get("label"), v.get("category"), v.get("class_name"),
                            v.get("frame_id"), v.get("area"), json.dumps(v.get("bbox")),
                            json.dumps(v.get("centroid")), v.get("angle"), v.get("notes"),
                            v.get("saved_at")
                        ))
                        track_count += 1
                print(f"    Loaded {track_count} tracks for session {sess_id}")

            # 3. Check if it's a scrap batch file (contains "batch_number")
            elif "batch_number" in data:
                bnum = data.get("batch_number")
                bid = f"BATCH{bnum}"
                aid = data.get("asset_id", bid)

                # Ensure asset exists in core.assets
                cur.execute("""
                    INSERT INTO core.assets (asset_id, name, type, location)
                    VALUES (%s, %s, 'scrap_batch', 'Batch Line')
                    ON CONFLICT (asset_id) DO NOTHING
                """, (aid, f"Batch {bnum} Asset"))

                scale = data.get("cm_per_pixel", 0.1)
                total = data.get("total_scraps", len(data.get("scraps", [])))

                cur.execute("""
                    INSERT INTO scrap.batches (batch_id, asset_id, batch_number, cm_per_pixel, total_scraps)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (batch_id) DO UPDATE SET cm_per_pixel=EXCLUDED.cm_per_pixel, total_scraps=EXCLUDED.total_scraps
                """, (bid, aid, bnum, scale, total))

                scrap_count = 0
                for scrap in data.get("scraps", []):
                    scrap_uuid = str(uuid.uuid4())
                    piece_name = scrap.get("piece_name", f"piece_{scrap.get('id')}")
                    stype = scrap.get("shape_type", "unknown")
                    vshape = str(scrap.get("verified_shape")) if "verified_shape" in scrap else None
                    vcount = scrap.get("vertices_count", 0)
                    area = scrap.get("area_cm2", 0.0)

                    cur.execute("""
                        INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (scrap_uuid, bid, piece_name, stype, vshape, vcount, area, json.dumps(scrap)))

                    # Vertices
                    verts = scrap.get("vertex_labels", {})
                    for vlabel, coords in verts.items():
                        if isinstance(coords, list) and len(coords) >= 2:
                            cur.execute("""
                                INSERT INTO scrap.vertices (scrap_id, label, x, y)
                                VALUES (%s, %s, %s, %s)
                            """, (scrap_uuid, vlabel, coords[0], coords[1]))

                    # Side lengths
                    sides = scrap.get("side_lengths_cm", {})
                    for slabel, length in sides.items():
                        cur.execute("""
                            INSERT INTO scrap.side_lengths (scrap_id, side_label, length_cm)
                            VALUES (%s, %s, %s)
                        """, (scrap_uuid, slabel, length))
                    scrap_count += 1
                print(f"    Loaded {scrap_count} scraps for batch {bid}")

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"  Warning loading {json_file.name}: {e}")

    # Step 4: Knowledge Correlations (core.cross_references)
    print("[5/6] Building knowledge correlation layer (core.cross_references)...")
    correlations = [
        ("core", "assets", "M14", "scrap", "batches", "BATCH1", "processed_scrap_batch", 0.95),
        ("core", "assets", "M14", "cv", "sessions", "SESSION_001", "monitored_by_cv_tracking", 1.00),
        ("core", "assets", "M22", "scrap", "batches", "BATCH2", "stamped_scrap_batch", 0.95),
        ("core", "assets", "M37", "scrap", "batches", "BATCH5", "transported_scrap_batch", 0.90),
    ]

    # Link detections to expert notes
    cur.execute("SELECT detection_id, asset_id, object, condition FROM cv.detections")
    det_rows = cur.fetchall()
    cur.execute("SELECT note_id, asset_id, comment FROM core.expert_notes")
    note_rows = cur.fetchall()

    for det_id, d_aid, d_obj, d_cond in det_rows:
        for note_id, n_aid, n_comment in note_rows:
            if d_aid == n_aid:
                kw = ["bearing", "crack", "spindle", "pressure", "cylinder", "motor", "thermal"]
                if any(k in (d_obj or "").lower() or k in (d_cond or "").lower() for k in kw) and \
                   any(k in n_comment.lower() for k in kw):
                    correlations.append((
                        "cv", "detections", str(det_id),
                        "core", "expert_notes", str(note_id),
                        "annotated_by_expert_note", 0.98
                    ))

    for src_s, src_t, src_id, tgt_s, tgt_t, tgt_id, rel, conf in correlations:
        cur.execute("""
            INSERT INTO core.cross_references
            (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'knowledge_correlator')
        """, (str(uuid.uuid4()), src_s, src_t, src_id, tgt_s, tgt_t, tgt_id, rel, conf))

    conn.commit()

    # Refresh Materialized Views
    print("  Refreshing materialized views (core.asset_summary, core.findings_search)...")
    cur.execute("SELECT core.refresh_cross_functional_views()")
    conn.commit()

    # Insert db update version with last updated timestamp feature
    print("  Recording DB build version and last updated timestamp...")
    cur.execute("""
        INSERT INTO core.schema_migrations (version, applied_at)
        VALUES ('db_build_v2_processed_sync', now())
        ON CONFLICT (version) DO UPDATE SET applied_at = EXCLUDED.applied_at
    """)
    conn.commit()

    conn.close()

    # Step 5: Export PostgreSQL .sql file
    print("[6/6] Exporting PostgreSQL relational database SQL dump file...")
    sql_out_path = Path("facility_knowledge_correlation.sql")

    cmd = [
        PG_DUMP_PATH,
        "--dbname=postgresql://postgres:Wegro26@localhost:5432/FACILITY1.DB",
        "--clean",
        "--if-exists",
        "--inserts",
        "--column-inserts",
        f"--file={sql_out_path.resolve()}"
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[SUCCESS] Exported PostgreSQL knowledge correlation SQL file: {sql_out_path.resolve()}")
        print(f"  SQL dump file size: {sql_out_path.stat().st_size / 1024:.2f} KB")
    else:
        print(f"[ERROR] pg_dump failed: {res.stderr}")

if __name__ == "__main__":
    build_database_and_export_sql()
