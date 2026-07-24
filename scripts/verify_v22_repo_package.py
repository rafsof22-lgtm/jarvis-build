from pathlib import Path
import csv, json, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()


def count(path):
    with (root / path).open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


assert count("registers/INSTRUCTION_REGISTER.csv") == 38
assert count("registry/runtime/MODULE_RUNTIME_RECONCILIATION_V22.csv") == 51
state = json.loads((root / "manifests/JARVIS_V22_COMPLETION_STATE.json").read_text())
assert state["instruction_records"] == 42994
assert state["production"] == "BLOCKED"
assert state["final_100_percent_acceptance"] == "BLOCKED"
print("V22_REPO_VALIDATION_PASS")
