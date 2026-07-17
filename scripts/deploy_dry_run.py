#!/usr/bin/env python3
"""Deployment readiness check for Jarvis free-first runtime targets.

This script never deploys. It reports the exact host/secret inputs that must be
proven before a later deployment workflow can safely perform remote actions.
"""

from __future__ import annotations

import argparse
import os
from typing import Iterable


TARGET_REQUIREMENTS = {
    "oracle": (
        "ORACLE_HOST",
        "ORACLE_SSH_USER",
        "ORACLE_SSH_PRIVATE_KEY",
        "ORACLE_DEPLOY_PATH",
    ),
    "vps": (
        "VPS_HOST",
        "VPS_SSH_USER",
        "VPS_SSH_PRIVATE_KEY",
        "VPS_DEPLOY_PATH",
    ),
    "local": (),
}


def missing(names: Iterable[str]) -> list[str]:
    return [name for name in names if not os.getenv(name)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Jarvis deployment readiness without deploying.")
    parser.add_argument("--target", default=os.getenv("JARVIS_DEPLOY_TARGET", "oracle"), choices=sorted(TARGET_REQUIREMENTS))
    parser.add_argument("--require-host", action="store_true", help="Exit nonzero if the target host inputs are missing.")
    parser.add_argument("--check-only", action="store_true", help="Run as a CI-safe dry run.")
    args = parser.parse_args()

    required = TARGET_REQUIREMENTS[args.target]
    missing_values = missing(required)

    print(f"Jarvis deployment target: {args.target}")
    print("Mode: readiness check only; no remote command or live deployment will run.")

    if missing_values:
        print("Missing deployment inputs:")
        for name in missing_values:
            print(f"- {name}")
        if args.require_host:
            return 2
        print("Deployment remains blocked until these values exist as GitHub/provider secrets.")
    else:
        print("Required target inputs are present. A later approved workflow can add live deploy steps.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
