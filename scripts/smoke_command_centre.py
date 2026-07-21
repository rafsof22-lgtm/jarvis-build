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
    assert snapshot["command_centre_version"] == "1.2.0"
    assert snapshot["contract_version"] == "1.0.0"
    assert snapshot["summary"]["repositories"] == 5
    assert {item["repository_id"] for item in snapshot["repositories"]} == {
        "jarvis-build", "hub", "jarvis-health", "videotranscribe", "property-agent-mcp"
    }
    assert snapshot["summary"]["known_credit_balances"] == 0
    assert snapshot["summary"]["unknown_credit_balances"] >= 1
    assert snapshot["summary"]["active_asset_profiles"] >= 2
    assert all("blockers" in item for item in snapshot["repositories"])
    assert "configuration_readiness" in snapshot
    assert "setup_actions" in snapshot
    assert "asset_intelligence" in snapshot
    assert set(snapshot["asset_intelligence"]["active_assets"]) >= {"XRP", "HBAR"}
    assert snapshot["asset_intelligence"]["apex_sources_per_asset_maximum"] == 100
    assert snapshot["asset_intelligence"]["simultaneous_all_asset_fanout"] is True
    assert snapshot["asset_intelligence"]["dynamic_ceiling_engine"] is True
    assert "global_jarvis" in snapshot
    assert snapshot["global_jarvis"]["available_on_every_page"] is True
    assert snapshot["global_jarvis"]["stop_mute_cancel_always_available"] is True
    assert snapshot["safety"]["secret_values_returned"] is False
    assert snapshot["safety"]["automatic_secret_deletion"] is False
    assert snapshot["safety"]["financial_execution"] is False
    assert snapshot["safety"]["voice_bypasses_approval"] is False
    print("command-centre v1.2 smoke checks passed")


if __name__ == "__main__":
    main()
