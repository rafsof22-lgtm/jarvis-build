#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

RISK_RULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "CRISIS_SIGNAL": ("CRITICAL", (r"\bsuicid(?:e|al)\b", r"\bself[- ]?harm\b", r"\boverdose\b", r"\bemergency services\b", r"\btriple zero\b")),
    "FREQUENCY_AS_DRUG_OR_CURE": ("HIGH", (r"\bfrequenc(?:y|ies)\b.{0,100}\b(?:cure|eradicate|replace|simulate|treat)\b", r"\brife\b.{0,100}\b(?:cure|eradicate|kill)\b")),
    "GUARANTEED_CURE_OR_INEVITABILITY": ("HIGH", (r"\b(?:guaranteed|certain|inevitable)\b.{0,60}\b(?:cure|remission|recovery)\b", r"\b100\s*%\b.{0,60}\b(?:cure|effective|success)\b")),
    "INVASIVE_EXPERIMENTAL_AS_ACTIONABLE": ("HIGH", (r"\b(?:crispr|gene edit(?:ing)?|deep brain stimulation|stem cell|exosome|histotripsy|hifu)\b", r"\b(?:peptide|dihexa|cerebrolysin|bpc[- ]?157)\b.{0,100}\b(?:dose|inject|protocol)\b")),
    "MEDICAL_DEVICE_CONTROL_SETTINGS": ("HIGH", (r"\b(?:hz|khz|mhz|tesla|gauss|pulse width|duty cycle|amplitude|intensity)\b", r"\b(?:pemf|tms|tdcs|spooky2|rife|laser|photobiomodulation)\b.{0,120}\b(?:setting|parameter|program|frequency|duration|power)\b")),
    "PRESCRIPTION_OR_MEDICATION_CHANGE": ("HIGH", (r"\b(?:stop|cease|discontinue|taper|reduce|increase|switch)\b.{0,100}\b(?:medication|medicine|drug|dose|antidepressant|stimulant)\b", r"\b(?:mg|mcg|milligram|microgram)s?\b.{0,80}\b(?:daily|dose|take)\b")),
    "PSYCHEDELIC_OR_CONTROLLED_DOSING": ("HIGH", (r"\b(?:psilocybin|ibogaine|ketamine|mdma|ayahuasca|dmt|lsd)\b.{0,120}\b(?:dose|mg|mcg|protocol|take)\b", r"\b(?:microdose|macrodose)\b")),
    "SPIRITUAL_CLAIM_AS_MEDICAL_FACT": ("MEDIUM", (r"\b(?:akashic|5d|quantum healing|chakra|ascension)\b.{0,120}\b(?:cure|disease|medical|treatment)\b",)),
    "UNSAFE_DETOX_OR_UNVERIFIED_BIOLOGIC": ("HIGH", (r"\b(?:mms|chlorine dioxide|turpentine|coffee enema|ozone therapy|chelation|colon cleanse)\b", r"\b(?:detox|cleanse)\b.{0,100}\b(?:heavy metal|mould|toxin|parasite|protocol|dose)\b")),
    "UNVERIFIED_PROVIDER_LEGAL_REGULATORY": ("MEDIUM", (r"\b(?:fda|tga|austrac|ato|asic|medical board)\b.{0,100}\b(?:approved|licensed|certified|legal|compliant)\b", r"\b(?:best|top|leading)\b.{0,80}\b(?:doctor|clinic|specialist|provider)\b")),
}
COMPILED = {risk: (priority, tuple(re.compile(p, re.I | re.S) for p in patterns)) for risk, (priority, patterns) in RISK_RULES.items()}


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def text_of(message: dict[str, Any]) -> str:
    parts = ((message.get("content") or {}).get("parts") or [])
    return "\n".join(part if isinstance(part, str) else str(part.get("text") or "") for part in parts if isinstance(part, (str, dict))).strip()


def conversations(path: Path) -> Iterable[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def merkle(values: list[str]) -> str:
    if not values:
        return sha("")
    level = [bytes.fromhex(v) for v in sorted(values)]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256(level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return level[0].hex()


def build(path: Path) -> dict[str, Any]:
    rows, seen, counts, roots = [], set(), Counter(), defaultdict(list)
    conv_count = assistant_count = flagged_count = 0
    for conv in conversations(path):
        conv_count += 1
        conv_ref = str(conv.get("conversation_id") or conv.get("id") or conv_count)
        for node_id, node in (conv.get("mapping") or {}).items():
            msg = (node or {}).get("message")
            if not isinstance(msg, dict) or ((msg.get("author") or {}).get("role") or "").lower() != "assistant":
                continue
            text = text_of(msg)
            if not text:
                continue
            assistant_count += 1
            claim_hash = sha(text)
            pointer_hash = sha(f"{conv_ref}|{msg.get('id') or node_id}|assistant")
            matches = [(risk, priority) for risk, (priority, patterns) in COMPILED.items() if any(p.search(text) for p in patterns)]
            flagged_count += bool(matches)
            for risk, priority in matches:
                if (claim_hash, risk) in seen:
                    continue
                seen.add((claim_hash, risk))
                item_hash = sha(f"{claim_hash}|{pointer_hash}|{risk}|{priority}")
                rows.append({"claim_sha256": claim_hash, "source_pointer_sha256": pointer_hash, "conversation_ref_sha256": sha(conv_ref), "risk_class": risk, "priority": priority, "item_sha256": item_hash})
                counts[risk] += 1
                roots[risk].append(item_hash)
    rows.sort(key=lambda row: (row["risk_class"], row["item_sha256"]))
    return {
        "schema_version": "1.0.0", "manifest_id": "HEALTH-CLAIM-REVIEW-HASH-MANIFEST-V17",
        "state": "DONE_VERIFIED_BOUNDED_LOCAL_SOURCE", "source_scope": "HEALTH_HANDOVER_194_KEYWORD_SELECTED_CONVERSATIONS",
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "conversation_count": conv_count,
        "assistant_message_count": assistant_count, "flagged_message_count": flagged_count, "flag_occurrence_count": len(rows),
        "category_counts": dict(sorted(counts.items())), "category_merkle_roots": {k: merkle(v) for k, v in sorted(roots.items())},
        "overall_merkle_root": merkle([r["item_sha256"] for r in rows]), "items": rows,
        "privacy_boundary": "Contains hashes, risk classes and priorities only. No raw claim text, titles, names, medical values or direct identifiers.",
        "truth_boundary": "Pattern-based triage for the older 194-conversation handover only; not clinical validation and not a replacement for the v14 latest-project denominator."
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("output", type=Path); parser.add_argument("--summary", type=Path)
    args = parser.parse_args(); manifest = build(args.input); args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if args.summary:
        summary = {k: v for k, v in manifest.items() if k != "items"}; summary["detailed_manifest_sha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
        args.summary.parent.mkdir(parents=True, exist_ok=True); args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
