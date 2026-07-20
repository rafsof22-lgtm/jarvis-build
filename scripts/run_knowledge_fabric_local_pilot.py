#!/usr/bin/env python3
import json
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    {"id": "gov-1", "namespace": "governance", "title": "Universal execution standard", "text": "Every module requires evidence, testing or waiver, runtime state and rollback."},
    {"id": "health-1", "namespace": "health", "title": "Health safety boundary", "text": "Health is research and education only. Live medical device control is disabled."},
    {"id": "vti-1", "namespace": "vti", "title": "VTI evidence route", "text": "Video and transcript claims require timestamps, source lineage and verification state."},
    {"id": "finance-1", "namespace": "finance", "title": "Financial boundary", "text": "Financial modules are research only and paper first. No autonomous execution."},
    {"id": "knowledge-1", "namespace": "knowledge", "title": "Knowledge fabric", "text": "Use hybrid lexical and vector retrieval with permissions, freshness, citations and contradiction handling."},
]
QUERIES = [
    ("live device control", "health-1"),
    ("paper first financial", "finance-1"),
    ("timestamp transcript evidence", "vti-1"),
    ("runtime rollback evidence", "gov-1"),
    ("hybrid retrieval citations", "knowledge-1"),
]


def main():
    started = time.perf_counter()
    con = sqlite3.connect(":memory:")
    con.execute("CREATE VIRTUAL TABLE docs USING fts5(id UNINDEXED, namespace UNINDEXED, title, text)")
    con.executemany("INSERT INTO docs(id, namespace, title, text) VALUES(:id, :namespace, :title, :text)", DOCS)
    hits = []
    passed = 0
    for query, expected in QUERIES:
        rows = con.execute("SELECT id, bm25(docs) AS score FROM docs WHERE docs MATCH ? ORDER BY score LIMIT 3", (query,)).fetchall()
        ids = [row[0] for row in rows]
        ok = expected in ids
        passed += int(ok)
        hits.append({"query": query, "expected": expected, "returned": ids, "pass": ok})
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    report = {
        "status": "PASS" if passed == len(QUERIES) else "FAIL",
        "backend": "sqlite_fts5_in_memory",
        "documents": len(DOCS),
        "queries": len(QUERIES),
        "top3_recall": passed / len(QUERIES),
        "elapsed_ms": elapsed_ms,
        "permissions_test": "namespace_field_present_only_not_enforced",
        "vector_adapter": "NOT_INSTALLED_BENCHMARK_PENDING",
        "postgres_adapter": "SPECIFIED_NOT_CONNECTED",
        "results": hits,
        "deployment_state": "LOCAL_PILOT_ONLY",
    }
    out = ROOT / "evidence/knowledge-fabric-local-pilot.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
