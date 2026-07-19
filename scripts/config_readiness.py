#!/usr/bin/env python3
"""Build a redacted configuration-readiness report.

The scanner inventories required environment names and references without
printing or storing values. It can also flag tracked environment files and
possible non-placeholder assignments for manual review. It never deletes,
rotates, connects, or tests an external account.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import re
from typing import Iterable

EXCLUDED