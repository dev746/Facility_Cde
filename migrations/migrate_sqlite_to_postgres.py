import os
import sqlite3
import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:Wegro26@localhost:5432/FACILITY1.DB")

def run_migration():
    if not os.path.exists("facility.db"):
        print("facility.db not found, skipping SQLite migration.")
        return

    old = sqlite3.connect("facility.db")
    old.row_factory = sqlite3.Row
    new = psycopg.connect(DATABASE_URL)

    asset_count = 0
    for row in old.execute("SELECT * FROM assets"):
        new.execute(
            """INSERT INTO core.assets (asset_id, name, type, location, created_at)
               VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (row["asset_id"], row["name"], row["type"], row["location"], str(row["created_at"]) if row["created_at"] else None),
        )
        asset_count += 1

    finding_count = 0
    for row in old.execute("SELECT * FROM findings"):
        ts = str(row["timestamp"]) if row["timestamp"] else None
        raw = str(row["raw_json"]) if row["raw_json"] else None
        new.execute(
            """INSERT INTO cv.detections
               (detection_id, asset_id, object, condition, confidence, source, timestamp, raw_json)
               VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s)""",
            (row["asset_id"], row["object"], row["condition"], row["confidence"],
             row["source"] or "legacy_sqlite", ts, raw),
        )
        finding_count += 1

    new.commit()
    
    # Refresh views
    with new.cursor() as cur:
        cur.execute("SELECT core.refresh_cross_functional_views()")
    new.commit()

    new.close()
    old.close()
    print(f"Data migration complete: {asset_count} assets, {finding_count} legacy findings migrated to Postgres!")

if __name__ == "__main__":
    run_migration()
