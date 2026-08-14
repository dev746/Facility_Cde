# Unified schema migration script
"""
This script runs all database schema migrations by calling schema.db_init(),
which applies every .sql file in the migrations/ directory in order.
"""
import os
import sys

# Ensure the project root is on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core import schema
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("[unified_schema] Running all schema migrations...")
    schema.db_init()
    print("[unified_schema] All migrations completed successfully.")
