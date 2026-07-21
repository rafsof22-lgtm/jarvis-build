from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis_command_centre.progress_tracker import latest_progress_tracker_path, read_latest_progress_tracker


class ProgressTrackerResolutionTests(unittest.TestCase):
    def test_highest_numeric_version_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory)
            tracker_dir = registry / "trackers"
            tracker_dir.mkdir()
            for version in (3, 10, 5):
                (tracker_dir / f"all_progress_tracker_reconciliation_v{version}.json").write_text(
                    json.dumps({"version": version}), encoding="utf-8"
                )
            self.assertEqual(latest_progress_tracker_path(registry).name, "all_progress_tracker_reconciliation_v10.json")
            self.assertEqual(json.loads(read_latest_progress_tracker(registry))["version"], 10)

    def test_unrelated_files_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory)
            tracker_dir = registry / "trackers"
            tracker_dir.mkdir()
            (tracker_dir / "all_progress_tracker_reconciliation_latest.json").write_text("{}")
            self.assertIsNone(latest_progress_tracker_path(registry))

    def test_missing_tracker_fails_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = json.loads(read_latest_progress_tracker(Path(directory)))
            self.assertEqual(payload["state"], "PENDING_TRACKER")


if __name__ == "__main__":
    unittest.main()
