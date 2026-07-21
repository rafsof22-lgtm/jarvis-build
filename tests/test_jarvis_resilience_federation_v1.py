import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.jarvis_completion.resilience_v1 import (
    DurableQueue,
    FederationExerciseRunner,
    KnowledgeFabricResilience,
    OperatorPack,
    ReleaseContinuityPack,
)
from src.jarvis_completion.runtime_v1 import DomainStagingFactory, KnowledgeFabric, TaskContract


class ResilienceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db_path = self.root / "fabric.db"
        self.fabric = KnowledgeFabric(self.db_path)
        self.fabric.db.execute("PRAGMA user_version=1")
        self.fabric.upsert_requirement(
            "RES-1", "backup exact", "backup", "resilience",
            implementation_path="src/jarvis_completion/resilience_v1.py",
            status="IMPLEMENTED_NOT_INTEGRATED",
        )
        self.fabric.add_evidence("RES-1", "src/jarvis_completion/resilience_v1.py", "tests/test_jarvis_resilience_federation_v1.py", "DONE_VERIFIED")
        self.fabric.db.commit()

    def tearDown(self):
        self.fabric.close()
        self.temp.cleanup()

    def test_atomic_backup_integrity_restore_and_schema(self):
        control = KnowledgeFabricResilience(self.db_path)
        manifest = control.create_backup(self.root / "backups")
        self.assertEqual(manifest.schema_version, 1)
        self.assertGreater(manifest.byte_count, 0)
        restored = control.restore(manifest, self.root / "restored.db", expected_schema_version=1)
        self.assertTrue(restored["restored"])
        self.assertIn("requirements", restored["tables"])
        connection = sqlite3.connect(self.root / "restored.db")
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM requirements").fetchone()[0], 1)
        finally:
            connection.close()

    def test_restore_rejects_digest_or_schema_mismatch(self):
        control = KnowledgeFabricResilience(self.db_path)
        manifest = control.create_backup(self.root / "backups")
        with self.assertRaises(ValueError):
            control.restore(manifest, self.root / "bad-version.db", expected_schema_version=2)
        Path(manifest.backup_path).write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            control.restore(manifest, self.root / "corrupt.db")

    def test_backup_retention(self):
        control = KnowledgeFabricResilience(self.db_path)
        directory = self.root / "backups"
        for _ in range(3):
            control.create_backup(directory)
        removed = control.enforce_retention(directory, keep=2)
        self.assertEqual(len(removed), 1)
        self.assertEqual(len(list(directory.glob("backup-*.sqlite3"))), 2)


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.queue = DurableQueue(Path(self.temp.name) / "queue.db")

    def tearDown(self):
        self.queue.close()
        self.temp.cleanup()

    def test_idempotent_enqueue_lease_and_success(self):
        first = self.queue.enqueue("test", {"x": 1}, "same")
        second = self.queue.enqueue("test", {"x": 2}, "same")
        self.assertEqual(first["job_id"], second["job_id"])
        leased = self.queue.lease("worker", now=100)
        self.assertEqual(leased["state"], "LEASED")
        result = self.queue.succeed(leased["job_id"], "worker", {"ok": True})
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertEqual(json.loads(result["result_json"]), {"ok": True})

    def test_retry_dead_letter_and_controlled_replay(self):
        job = self.queue.enqueue("failure", {}, "failure", max_attempts=2, available_at=10)
        self.queue.lease("worker", now=10)
        retry = self.queue.fail(job["job_id"], "worker", "outage", now=10, base_delay=1)
        self.assertEqual(retry["state"], "RETRY_WAIT")
        self.assertIsNone(self.queue.lease("worker", now=10))
        self.queue.lease("worker", now=11)
        dead = self.queue.fail(job["job_id"], "worker", "outage", now=11, base_delay=1)
        self.assertEqual(dead["state"], "DEAD_LETTER")
        with self.assertRaises(PermissionError):
            self.queue.replay(job["job_id"], approved=False, now=12)
        replayed = self.queue.replay(job["job_id"], approved=True, now=12)
        self.assertEqual(replayed["state"], "QUEUED")
        self.assertEqual(self.queue.dashboard()["dead_letters"][0]["replay_count"], 1)

    def test_stale_worker_recovery(self):
        job = self.queue.enqueue("stale", {}, "stale", available_at=5)
        self.queue.lease("lost-worker", now=5, lease_seconds=2)
        self.assertEqual(self.queue.recover_stale_leases(now=8), [job["job_id"]])
        self.assertEqual(self.queue.get(job["job_id"])["state"], "QUEUED")


class FederationAndOperatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.fabric = KnowledgeFabric(root / "fabric.db")
        self.queue = DurableQueue(root / "queue.db")
        self.root = root

    def tearDown(self):
        self.queue.close()
        self.fabric.close()
        self.temp.cleanup()

    @staticmethod
    def contract():
        return TaskContract(
            "exercise-1", "owner", "CFO research scenario",
            {"assets": 100.0, "liabilities": 20.0, "annual_cashflow": 10.0, "shock_pct": -0.1},
            ["evidence"], ["local"], ["live"], 2, ["production"], 1000, 0, 30, 2, "restore backup",
        )

    def test_complete_happy_path_and_failure_suite(self):
        runner = FederationExerciseRunner(self.fabric, self.queue)
        happy = runner.run_happy_path(
            self.contract(),
            lambda payload: DomainStagingFactory.cfo_scenario(**payload),
        )
        self.assertTrue(happy.passed)
        failures = runner.run_failure_suite()
        self.assertTrue(all(item.passed for item in failures))
        pack = OperatorPack.build(
            self.fabric, self.queue, [happy, *failures],
            [{"title": "Provider staging", "owner_action": "Configure approved endpoint", "evidence_required": ["deployment id"], "safe_retry": False}],
        )
        self.assertEqual(pack["traffic_light"], "GREEN")
        self.assertEqual(pack["button_truth"]["production"], "DISABLED_OWNER_APPROVAL_REQUIRED")
        self.assertEqual(pack["button_truth"]["live_trading"], "DISABLED")

    def test_release_continuity_pack_hashes_artifacts(self):
        artifact = self.root / "artifact.txt"
        artifact.write_text("verified evidence\n", encoding="utf-8")
        result = ReleaseContinuityPack.create(
            self.root / "release",
            release_id="local-resilience-v1",
            artifacts=[artifact],
            tests=["resilience", "queue", "federation"],
            risks=["connected staging unproven"],
            gaps=["owner acceptance"],
            rollback="revert merge",
            resume="continue connected staging proofs",
        )
        self.assertTrue(Path(result["manifest_path"]).exists())
        self.assertEqual(len(result["manifest_sha256"]), 64)
        manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_id"], "local-resilience-v1")
        self.assertIn("connected staging", manifest["truth_boundary"])


if __name__ == "__main__":
    unittest.main()
