"""
api/graph.py — Relational graph and table endpoints for admin/developer use.

Surfaces the data relationships stored in core.cross_references as:
  GET /api/graph/data          → nodes + edges JSON (D3/Cytoscape format)
  GET /api/graph/table         → flat relationship table
  GET /api/graph/asset/{id}    → ego-graph for one asset (its neighbours)
  GET /api/graph/schema        → schema-level entity-relationship summary
  GET /api/graph/changes       → recent data version changes
"""
from fastapi import APIRouter, HTTPException, Depends, Header
import os

router = APIRouter()


def _check_api_key(x_api_key: str = Header(default="")):
    expected = os.getenv("API_KEY", "")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# ── Graph data ─────────────────────────────────────────────────

@router.get("/data")
def graph_data(limit: int = 200, _=Depends(_check_api_key)):
    """
    Returns nodes and edges in a format compatible with D3.js force graph,
    Cytoscape.js, or any graph visualisation tool.

    Nodes: assets from core.assets
    Edges: relationships from core.cross_references
    """
    from core.db import query

    # Assets as nodes
    try:
        assets = query(
            "SELECT asset_id, name, type, location, status FROM core.assets LIMIT %s",
            (limit,)
        )
    except Exception:
        assets = query(
            "SELECT asset_id, name, type, location, status FROM assets LIMIT ?",
            (limit,)
        )

    nodes = [
        {
            "id":       a["asset_id"],
            "label":    a["name"],
            "type":     a.get("type", "Unknown"),
            "location": a.get("location", ""),
            "status":   a.get("status", "active"),
            "group":    a.get("type", "Unknown"),
        }
        for a in assets
    ]

    # Cross-references as edges
    try:
        refs = query(
            """SELECT source_id, target_id, relationship_type, confidence
               FROM core.cross_references LIMIT %s""",
            (limit * 2,)
        )
    except Exception:
        refs = []

    edges = [
        {
            "source":       r["source_id"],
            "target":       r["target_id"],
            "relationship": r.get("relationship_type", "related"),
            "confidence":   float(r.get("confidence", 0.5)),
        }
        for r in refs
    ]

    # Also add implicit edges: findings → assets (findings have asset_id)
    try:
        finding_edges = query(
            """SELECT DISTINCT f.asset_id, f.source,
                  COUNT(*) as count,
                  AVG(f.confidence) as avg_conf
               FROM core.findings_unified f
               GROUP BY f.asset_id, f.source
               LIMIT %s""",
            (limit,)
        )
        for fe in finding_edges:
            source_node = f"src_{fe['source']}"
            # Add source as a node if not already present
            if not any(n["id"] == source_node for n in nodes):
                nodes.append({
                    "id":       source_node,
                    "label":    fe["source"],
                    "type":     "data_source",
                    "group":    "source",
                    "status":   "active",
                    "location": "",
                })
            edges.append({
                "source":       source_node,
                "target":       fe["asset_id"],
                "relationship": "provides_findings",
                "confidence":   float(fe.get("avg_conf") or 0.5),
                "weight":       int(fe.get("count") or 1),
            })
    except Exception:
        pass

    return {
        "status":     "ok",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes":      nodes,
        "edges":      edges,
    }


@router.get("/table")
def relationship_table(limit: int = 100, _=Depends(_check_api_key)):
    """
    Flat table of all known relationships across schemas.
    Easy to paste into a spreadsheet or display in a data grid.
    """
    from core.db import query

    rows = []

    # Cross-references
    try:
        refs = query(
            """SELECT cr.source_schema, cr.source_table, cr.source_id,
                      cr.target_schema, cr.target_table, cr.target_id,
                      cr.relationship_type, cr.confidence
               FROM core.cross_references cr
               LIMIT %s""",
            (limit,)
        )
        rows += [dict(r) for r in refs]
    except Exception:
        pass

    # Asset → findings summary
    try:
        af = query(
            """SELECT a.asset_id as source_id,
                      'assets' as source_table,
                      f.source as target_table,
                      COUNT(*) as finding_count,
                      MAX(f.confidence) as max_confidence
               FROM core.assets a
               JOIN core.findings_unified f ON f.asset_id = a.asset_id
               GROUP BY a.asset_id, f.source
               LIMIT %s""",
            (limit,)
        )
        for r in af:
            rows.append({
                "source_schema":    "core",
                "source_table":     "assets",
                "source_id":        r["source_id"],
                "target_schema":    r["target_table"],
                "target_table":     "findings",
                "target_id":        "*",
                "relationship_type": "has_findings",
                "confidence":       r.get("max_confidence"),
                "count":            r.get("finding_count"),
            })
    except Exception:
        pass

    return {
        "status": "ok",
        "count":  len(rows),
        "rows":   rows,
    }


@router.get("/asset/{asset_id}")
def asset_ego_graph(asset_id: str, _=Depends(_check_api_key)):
    """
    Returns the ego-graph for a single asset:
    the asset node + all directly connected nodes and edges.
    """
    from core.db import query

    aid = asset_id.upper()

    # Central node
    try:
        asset_rows = query("SELECT * FROM core.assets WHERE asset_id = %s", (aid,))
    except Exception:
        asset_rows = query("SELECT * FROM assets WHERE asset_id = ?", (aid,))

    if not asset_rows:
        raise HTTPException(status_code=404, detail=f"Asset {aid} not found")

    a = dict(asset_rows[0])
    nodes = [{
        "id":       a["asset_id"],
        "label":    a["name"],
        "type":     a.get("type", "Unknown"),
        "location": a.get("location", ""),
        "central":  True,
    }]
    edges = []

    # Cross-reference neighbours
    try:
        refs = query(
            """SELECT * FROM core.cross_references
               WHERE source_id = %s OR target_id = %s""",
            (aid, aid)
        )
        for r in refs:
            neighbour_id = r["target_id"] if r["source_id"] == aid else r["source_id"]
            nodes.append({"id": neighbour_id, "label": neighbour_id, "central": False})
            edges.append({
                "source":       r["source_id"],
                "target":       r["target_id"],
                "relationship": r.get("relationship_type", "related"),
            })
    except Exception:
        pass

    # Findings as connected nodes
    try:
        findings = query(
            "SELECT DISTINCT source FROM core.findings_unified WHERE asset_id = %s",
            (aid,)
        )
        for f in findings:
            src_node = f"src_{f['source']}"
            nodes.append({"id": src_node, "label": f["source"], "type": "data_source"})
            edges.append({"source": src_node, "target": aid, "relationship": "detected_in"})
    except Exception:
        pass

    # Expert notes authors
    try:
        authors = query(
            "SELECT DISTINCT author FROM core.expert_notes WHERE asset_id = %s",
            (aid,)
        )
        for auth in authors:
            auth_node = f"author_{auth['author'].replace(' ','_')}"
            nodes.append({"id": auth_node, "label": auth["author"], "type": "expert"})
            edges.append({"source": auth_node, "target": aid, "relationship": "annotated"})
    except Exception:
        pass

    return {
        "status":     "ok",
        "asset_id":   aid,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes":      nodes,
        "edges":      edges,
    }


@router.get("/schema")
def schema_summary(_=Depends(_check_api_key)):
    """
    Returns a high-level entity-relationship summary across all schemas.
    Useful for developers/admins understanding the data model.
    """
    return {
        "status": "ok",
        "schemas": {
            "core": {
                "tables": ["assets", "expert_notes", "cross_references",
                           "findings_unified (view)", "asset_summary (matview)"],
                "description": "Central repository. All other schemas link here via asset_id.",
            },
            "cv": {
                "tables": ["detections", "tracks", "sessions"],
                "description": "Computer vision outputs. detections and tracks both link to core.assets.",
            },
            "scrap": {
                "tables": ["batches", "scraps", "vertices", "side_lengths"],
                "description": "Scrap/batch measurement data. batches links to core.assets.",
            },
            "bim": {
                "tables": ["projects", "elements", "spatial_structure", "relationships"],
                "description": "BIM/IFC data. elements links to core.assets and bim.projects.",
            },
            "auth": {
                "tables": ["users", "groups", "group_members"],
                "description": "User registry and RBAC. phone is the primary key for users.",
            },
            "ingest": {
                "tables": ["files"],
                "description": "Ingestion audit log. One row per file processed.",
            },
        },
        "key_relationships": [
            "core.assets ← cv.detections (asset_id FK)",
            "core.assets ← cv.tracks (asset_id FK)",
            "core.assets ← scrap.batches (asset_id FK)",
            "core.assets ← bim.elements (asset_id FK)",
            "core.assets ← core.expert_notes (asset_id FK)",
            "core.assets ↔ core.cross_references (source_id / target_id)",
            "scrap.batches ← scrap.scraps (batch_id FK)",
            "scrap.scraps ← scrap.vertices (scrap_id FK)",
            "scrap.scraps ← scrap.side_lengths (scrap_id FK)",
            "bim.elements ↔ bim.relationships (source/target element_id FK)",
        ],
        "unified_views": {
            "core.findings_unified": "UNION of cv.detections + cv.tracks + scrap scraps + bim.elements",
            "core.asset_summary":    "Materialized view — pre-aggregated counts per asset",
        },
    }


@router.get("/changes")
def recent_changes(hours: int = 24, _=Depends(_check_api_key)):
    """
    Returns all data version changes in the last N hours.
    Shows what files were ingested, what changed, and which assets were affected.
    """
    from ingestion.version_tracker import get_change_summary
    rows = get_change_summary(since_hours=hours)
    return {
        "status":        "ok",
        "since_hours":   hours,
        "change_count":  len(rows),
        "changes":       rows,
    }
