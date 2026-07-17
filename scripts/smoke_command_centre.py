from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_command_centre.command_centre import build_snapshot


def main() -> None:
    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((ROOT / "registry").glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))

    snapshot = build_snapshot(live=False)
    assert snapshot["command_centre_version"] == "1.0.0"
    assert snapshot["contract_version"] == "1.0.0"
    assert snapshot["summary"]["repositories"] == 5
    assert {item["repository_id"] for item in snapshot["repositories"]} == {
        "jarvis-build", "hub", "jarvis-health", "videotranscribe", "property-agent-mcp"
    }
    assert snapshot["summary"]["known_credit_balances"] == 0
    assert snapshot["summary"]["unknown_credit_balances"] >= 1
    assert all("blockers" in item for item in snapshot["repositories"])
    print("command-centre smoke checks passed")


if __name__ == "__main__":
    main()
