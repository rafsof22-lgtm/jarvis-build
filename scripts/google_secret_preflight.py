#!/usr/bin/env python3
"""Classify Google-family GitHub secrets without exposing values.

This script is intended for GitHub Actions preflight use. It reads raw secret
values from environment variables, detects likely formats, and writes a summary
containing only secret names, key names, and format labels.
"""

from __future__ import annotations

import base64
import json
import os
import re
import shlex
from dataclasses import dataclass
from typing import Iterable

GOOGLE_KEYS = {
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_API_KEY",
    "GOOGLE_AI_API_KEY",
    "GOOGLE_GEMINI_API_KEY",
    "GMAIL_CLIENT_ID",
    "GMAIL_CLIENT_SECRET",
    "GMAIL_REFRESH_TOKEN",
    "GMAIL_API_KEY",
    "GOOGLE_DRIVE_CLIENT_ID",
    "GOOGLE_DRIVE_CLIENT_SECRET",
    "GOOGLE_CALENDAR_CLIENT_ID",
    "GOOGLE_CALENDAR_CLIENT_SECRET",
    "GOOGLE_CUSTOM_SEARCH_API_KEY",
    "GOOGLE_CUSTOM_SEARCH_CX",
    "YOUTUBE_API_KEY",
    "GOOGLE_VISION_API_KEY",
    "GOOGLE_SHEET_ID",
    "GOOGLE_DRIVE_FOLDER_ID",
}

SECRET_ENV_NAMES = [
    "GOOGLE",
    "GOOGLE2",
    "GMAIL",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GMAIL_CLIENT_ID",
    "GMAIL_CLIENT_SECRET",
    "GMAIL_REFRESH_TOKEN",
    "GMAIL_API_KEY",
    "GOOGLE_DRIVE_CLIENT_ID",
    "GOOGLE_DRIVE_CLIENT_SECRET",
    "GOOGLE_CALENDAR_CLIENT_ID",
    "GOOGLE_CALENDAR_CLIENT_SECRET",
]


@dataclass(frozen=True)
class Classification:
    source: str
    present: bool
    format_label: str
    detected_keys: tuple[str, ...]
    notes: tuple[str, ...] = ()


def add_mask(value: str) -> None:
    if value:
        print(f"::add-mask::{value}")


def mask_possible_values(raw: str) -> None:
    add_mask(raw)
    for value in parse_key_value_bundle(raw).values():
        add_mask(value)


def load_json_candidate(raw: str) -> object | None:
    value = raw.strip()
    if not value:
        return None
    candidates = [value]
    try:
        decoded = base64.b64decode(value, validate=True).decode("utf-8")
    except Exception:
        decoded = ""
    if decoded:
        candidates.append(decoded.strip())
    for candidate in candidates:
        if not candidate.startswith(("{", "[")):
            continue
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def parse_key_value_bundle(raw: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for line in lines:
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        key, value = clean.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        pairs[key.upper()] = value.strip().strip('"').strip("'")

    if pairs:
        return pairs

    # Fallback for one-line pasted content such as KEY=value KEY2="value two".
    try:
        tokens = shlex.split(raw, comments=True, posix=True)
    except Exception:
        tokens = []
    for token in tokens:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            pairs[key.upper()] = value
    return pairs


def classify_json(source: str, value: object) -> Classification:
    if isinstance(value, list):
        labels = []
        keys: set[str] = set()
        for item in value:
            item_class = classify_json(source, item)
            labels.append(item_class.format_label)
            keys.update(item_class.detected_keys)
        label = "JSON list bundle candidate"
        if labels:
            label += " containing " + ", ".join(sorted(set(labels)))
        return Classification(source, True, label, tuple(sorted(keys)))

    if not isinstance(value, dict):
        return Classification(source, True, "JSON candidate with unsupported top-level shape", ())

    keys = {str(key).upper() for key in value.keys()}
    lowered = {str(key).lower(): val for key, val in value.items()}

    if lowered.get("type") == "service_account" and {"client_email", "private_key"}.issubset(lowered.keys()):
        return Classification(
            source,
            True,
            "service-account JSON candidate",
            tuple(sorted({"GOOGLE_SERVICE_ACCOUNT_JSON", *keys})),
        )
    if {"client_id", "client_secret", "refresh_token"}.issubset(lowered.keys()):
        return Classification(
            source,
            True,
            "OAuth client/refresh-token bundle candidate",
            tuple(sorted({"GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN", *keys})),
        )
    if "api_key" in lowered or "key" in lowered:
        return Classification(source, True, "API-key JSON candidate", tuple(sorted(keys)))

    detected = sorted(keys & GOOGLE_KEYS)
    if detected:
        return Classification(source, True, "JSON key/value bundle candidate", tuple(detected))
    return Classification(source, True, "unknown Google JSON format", tuple(sorted(keys)))


def classify_raw(source: str, raw: str) -> Classification:
    if not raw.strip():
        return Classification(source, False, "missing", ())

    parsed_json = load_json_candidate(raw)
    if parsed_json is not None:
        return classify_json(source, parsed_json)

    kv = parse_key_value_bundle(raw)
    detected = sorted(set(kv.keys()) & GOOGLE_KEYS)
    if detected:
        return Classification(source, True, ".env/key-value pasted bundle candidate", tuple(detected))

    if "-----BEGIN PRIVATE KEY-----" in raw or "private_key" in raw:
        return Classification(source, True, "possible service-account/private-key pasted bundle", ())

    compact = raw.strip()
    if "\n" not in compact and len(compact) >= 20:
        return Classification(source, True, "single API-key/token candidate", ())

    return Classification(source, True, "unknown Google secret format", ())


def present_flag(name: str) -> bool:
    return os.getenv(f"HAS_{name}", "false").lower() == "true"


def write_summary(classifications: Iterable[Classification]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    rows = list(classifications)
    lines = [
        "# Secret preflight summary",
        "",
        "No secret values were printed, logged, deployed, sent, or tested against external APIs.",
        "",
        "## Runtime classification",
        "",
        "| Source secret | Status | Safe format label | Detected key names only |",
        "|---|---|---|---|",
    ]
    for item in rows:
        status = "present" if item.present else "missing"
        keys = ", ".join(f"`{key}`" for key in item.detected_keys) if item.detected_keys else "-"
        lines.append(f"| `{item.source}` | {status} | {item.format_label} | {keys} |")

    lines.extend([
        "",
        "## Direct secret-name presence",
        "",
        "| Secret name | Status |",
        "|---|---|",
    ])
    for name in SECRET_ENV_NAMES:
        status = "present" if present_flag(name) else "missing"
        lines.append(f"| `{name}` | {status} |")

    lines.extend([
        "",
        "## Safety boundary",
        "",
        "- This workflow distinguishes pasted secret formats without revealing values.",
        "- Presence and shape do not prove Google/Gmail/Drive/Calendar permission.",
        "- No deployment, paid API call, email send, Drive write, Calendar write, or destructive action ran.",
        "- GitHub stores repository secret names uppercase; a secret typed as `Google` is referenced as `GOOGLE`.",
    ])

    output = "\n".join(lines) + "\n"
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write(output)
    else:
        print(output)


def main() -> int:
    sources = {
        "GOOGLE": os.getenv("GOOGLE_SECRET_RAW", ""),
        "GOOGLE2": os.getenv("GOOGLE2_SECRET_RAW", ""),
    }
    for raw in sources.values():
        mask_possible_values(raw)

    classifications = [classify_raw(source, raw) for source, raw in sources.items()]
    write_summary(classifications)

    if not any(item.present for item in classifications) and not any(present_flag(name) for name in SECRET_ENV_NAMES):
        raise SystemExit(
            "No Google-family or conventional Google/Gmail/Drive/Calendar secret was present. "
            "Add GOOGLE, GOOGLE2, or explicit conventional Google secrets as GitHub Actions secrets."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
