from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Alert:
    alert_id: str
    repository_id: str
    kind: str
    severity: str
    summary: str
    evidence_pointer: str
    created_at: str