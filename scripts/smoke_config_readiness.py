#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from config_readiness import scan


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".env.example").write_text("SERVICE_URL=\nSERVICE_API_KEY=\n", encoding="utf-8")
        (root / "app.py").write_text("import os\nos.getenv('SERVICE_API_KEY')\n", encoding="utf-8")
        report = scan(root)
        encoded = json.dumps(report)
        if "actual-value" in encoded:
            raise SystemExit("Readiness report emitted a value")
        if report["safety"]["values_emitted"]:
            raise SystemExit("Readiness report must be redacted")
        names = {item["name"] for item in report["configuration"]}
        if "SERVICE_API_KEY" not in names or "SERVICE_URL" not in names:
            raise SystemExit("Expected configuration names were not found")
        if report["summary"]["tracked_environment_files_for_review"] != 0:
            raise SystemExit("Template files must not be classified as unsafe environment files")
    print("Configuration readiness smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
