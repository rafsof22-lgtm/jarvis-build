from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.jarvis_integrations.read_only_db_inspector_v1 import InspectorPolicy, QuerySpec, ReadOnlyDatabaseInspector


class ReadOnlyDatabaseInspectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "fixture.db"
        connection = sqlite3.connect(self.path)
        connection.execute("CREATE TABLE records(id INTEGER PRIMARY KEY, category TEXT, value INTEGER)")
        connection.executemany(
            "INSERT INTO records(category,value) VALUES(?,?)",
            [("a", 10), ("a", 20), ("b", 30), ("b", 40)],
        )
        connection.commit()
        connection.close()
        self.inspector = ReadOnlyDatabaseInspector(
            self.path,
            {
                "by_category": QuerySpec(
                    "by_category",
                    "SELECT id,category,value FROM records WHERE category=:category ORDER BY id",
                    frozenset({"category"}),
                ),
                "all_records": QuerySpec("all_records", "SELECT id,category,value FROM records ORDER BY id"),
            },
        )

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_named_parameter_query_succeeds(self):
        result = self.inspector.execute("by_category", {"category": "a"})
        self.assertEqual(result["row_count"], 2)
        self.assertEqual([row["value"] for row in result["rows"]], [10, 20])
        self.assertFalse(result["database_mutation_allowed"])

    def test_unknown_query_is_rejected(self):
        with self.assertRaises(KeyError):
            self.inspector.execute("arbitrary-sql")

    def test_unapproved_parameter_is_rejected(self):
        with self.assertRaises(ValueError):
            self.inspector.execute("by_category", {"category": "a", "tenant": "other"})

    def test_mutation_query_cannot_be_registered(self):
        with self.assertRaises(ValueError):
            QuerySpec("change", "UPDATE records SET value=0").validate()

    def test_row_limit_truncates_results(self):
        result = self.inspector.execute("all_records", policy=InspectorPolicy(maximum_rows=2, timeout_milliseconds=500))
        self.assertEqual(result["row_count"], 2)
        self.assertTrue(result["truncated"])

    def test_audit_contains_parameter_names_not_values(self):
        sensitive_value = "distinctive-parameter-value-not-for-audit"
        result = self.inspector.execute("by_category", {"category": sensitive_value})
        audit = result["audit"]
        self.assertEqual(audit["parameter_names"], ["category"])
        self.assertNotIn("parameters", audit)
        self.assertNotIn(sensitive_value, str(audit))
        self.assertEqual(len(audit["event_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
