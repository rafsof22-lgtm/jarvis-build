from __future__ import annotations

import sqlite3
import time
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class BenchmarkDocument:
    document_id: str
    namespace: str
    title: str
    text: str
    permission: str
    freshness_epoch: int
    claim_group: str
    stance: str
    duplicate_of: str | None = None


@dataclass(frozen=True)
class BenchmarkQuery:
    query_id: str
    text: str
    namespace: str
    permission: str
    expected_ids: tuple[str, ...]
    require_contradiction: bool = False


class KnowledgeFabricBenchmarkV2:
    def __init__(self, documents: Iterable[BenchmarkDocument]) -> None:
        self.documents = tuple(documents)
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            "CREATE VIRTUAL TABLE docs USING fts5(document_id UNINDEXED, namespace UNINDEXED, title, text, permission UNINDEXED, freshness_epoch UNINDEXED, claim_group UNINDEXED, stance UNINDEXED, duplicate_of UNINDEXED)"
        )
        self.db.executemany(
            "INSERT INTO docs VALUES(:document_id,:namespace,:title,:text,:permission,:freshness_epoch,:claim_group,:stance,:duplicate_of)",
            [asdict(item) for item in self.documents],
        )

    def close(self) -> None:
        self.db.close()

    def search(self, query: BenchmarkQuery, *, limit: int = 5) -> list[dict]:
        rows = self.db.execute(
            """
            SELECT document_id,namespace,title,permission,freshness_epoch,claim_group,stance,duplicate_of,bm25(docs) AS lexical_score
            FROM docs
            WHERE docs MATCH ? AND namespace=? AND permission IN ('public',?) AND duplicate_of IS NULL
            ORDER BY lexical_score ASC, CAST(freshness_epoch AS INTEGER) DESC, document_id ASC
            LIMIT ?
            """,
            (query.text, query.namespace, query.permission, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def contradiction_pairs(self, claim_group: str, *, permission: str) -> list[tuple[str, str]]:
        rows = self.db.execute(
            "SELECT document_id,stance FROM docs WHERE claim_group=? AND permission IN ('public',?) AND duplicate_of IS NULL ORDER BY document_id",
            (claim_group, permission),
        ).fetchall()
        positive = [row[0] for row in rows if row[1] == "supports"]
        negative = [row[0] for row in rows if row[1] == "contradicts"]
        return [(left, right) for left in positive for right in negative]

    def run(self, queries: Iterable[BenchmarkQuery]) -> dict:
        started = time.perf_counter()
        results = []
        precision_hits = 0
        recall_hits = 0
        permission_failures = 0
        freshness_passes = 0
        contradiction_passes = 0
        query_count = 0
        for query in queries:
            query_count += 1
            rows = self.search(query)
            returned = [row["document_id"] for row in rows]
            expected = set(query.expected_ids)
            precision_hit = bool(returned) and returned[0] in expected
            recall_hit = expected <= set(returned)
            permission_ok = all(row["permission"] in {"public", query.permission} for row in rows)
            fresh_ok = all(rows[index]["freshness_epoch"] >= rows[index + 1]["freshness_epoch"] for index in range(len(rows) - 1)) if rows else False
            contradiction_ok = True
            if query.require_contradiction:
                groups = {row["claim_group"] for row in rows if row["claim_group"]}
                contradiction_ok = any(self.contradiction_pairs(group, permission=query.permission) for group in groups)
            precision_hits += int(precision_hit)
            recall_hits += int(recall_hit)
            permission_failures += int(not permission_ok)
            freshness_passes += int(fresh_ok)
            contradiction_passes += int(contradiction_ok)
            results.append({
                "query_id": query.query_id,
                "returned": returned,
                "expected": sorted(expected),
                "precision_hit": precision_hit,
                "recall_hit": recall_hit,
                "permission_ok": permission_ok,
                "freshness_ok": fresh_ok,
                "contradiction_ok": contradiction_ok,
            })
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        denominator = max(1, query_count)
        return {
            "backend": "sqlite_fts5_in_memory",
            "document_count": len(self.documents),
            "query_count": query_count,
            "top1_precision": precision_hits / denominator,
            "expected_set_recall": recall_hits / denominator,
            "permission_failures": permission_failures,
            "freshness_pass_rate": freshness_passes / denominator,
            "contradiction_pass_rate": contradiction_passes / denominator,
            "duplicate_documents_excluded": sum(item.duplicate_of is not None for item in self.documents),
            "elapsed_ms": elapsed_ms,
            "vector_backend": "NOT_EXECUTED_DEPENDENCY_NOT_SELECTED",
            "postgres_backend": "NOT_CONNECTED",
            "results": results,
        }
