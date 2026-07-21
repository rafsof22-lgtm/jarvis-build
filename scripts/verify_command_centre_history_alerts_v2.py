#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_command_centre.command_centre import build_snapshot
from jarvis_command_centre.history_alerts import list_open_alerts, list_recent_snapshots, persist_snapshot_and_alerts


def main() -> None:
    snapshot = build_snapshot(live=False)
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / "command-centre.sqlite3"
        first = persist_snapshot_and_alerts(db, snapshot)
        second = persist_snapshot_and_alerts(db, snapshot)
        assert first["secret_values_stored"] is False
        assert first["derived_alerts"] >= 1
        assert first["new_alerts"] >= 1
        assert second["new_alerts"] == 0
        assert len(list_recent_snapshots(db)) == 1
        assert len(list_open_alerts(db)) >= 1
    print("command-centre history and alert verification passed")


if __name__ == "__main__":
    main()
