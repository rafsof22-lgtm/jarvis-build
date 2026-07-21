from __future__ import annotations

import re
from pathlib import Path

_TRACKER_PATTERN = re.compile(r"all_progress_tracker_reconciliation_v(?P<version>\d+)\.json$")


def latest_progress_tracker_path(registry: Path) -> Path | None:
    """Return the highest numbered reconciliation tracker, if one exists."""
    tracker_dir = registry / "trackers"
    candidates: list[tuple[int, Path]] = []
    if not tracker_dir.exists():
        return None
    for path in tracker_dir.glob("all_progress_tracker_reconciliation_v*.json"):
        match = _TRACKER_PATTERN.fullmatch(path.name)
        if match:
            candidates.append((int(match.group("version")), path))
    return max(candidates, default=(0, None), key=lambda item: item[0])[1]


def read_latest_progress_tracker(registry: Path) -> bytes:
    path = latest_progress_tracker_path(registry)
    return path.read_bytes() if path else b'{"state":"PENDING_TRACKER"}'
