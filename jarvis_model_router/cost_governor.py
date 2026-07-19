"""Offline-first Jarvis cost governor.

No provider calls occur here. The governor estimates cost, enforces soft/hard
limits, selects the cheapest qualified route, records telemetry, and supports
cache/batch planning before any external model or API client is invoked.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from