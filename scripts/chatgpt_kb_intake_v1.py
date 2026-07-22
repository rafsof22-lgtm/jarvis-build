#!/usr/bin/env python3
"""Secure, deterministic ChatGPT export intake and delta scanner.

Preserves raw input unchanged, hashes sources and records, rejects unsafe archive
paths/executable payloads, extracts role-separated messages, and creates coverage,
lineage, classification-candidate, gap, and delta outputs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

SCHEMA_VERSION = "1.0.0"
EXECUTABLE_SUFFIXES = {
    ".exe", ".dll", ".so", ".dylib", ".bat", ".cmd", ".com", ".msi",
    ".scr", ".ps1", ".sh", ".app", ".jar", ".apk", ".deb", ".rpm",
}
SECRET_MARKERS = (
    "sk-proj-", "sk-live-", "api_key=", "api-key:", "private key-----",
    "begin private key", "seed phrase", "recovery code", "client_secret",
)
PROJECT_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("02_Jarvis_Build_AI_Agents_Automation", ("jarvis", "raf213g", "agent", "multi-agent", "n8n", "local llm", "app builder", "automation", "workflow", "api build")),
    ("03_Crypto_XRP_HBAR_Finance", ("xrp", "ripple", "hbar", "hedera", "crypto", "token", "wallet", "staking", "etf", "rlusd")),
    ("04_Finance_Tax_Active_Trust_SMSF", ("tax", "active trust", "smsf", "xero", "cfo", "accounting", "cash flow", "trust deed", "gst")),
    ("05_Property_Land_Tax_Heritage_Sale", ("property", "land tax", "heritage", "real estate", "buyer", "vendor", "development site")),
    ("06_Health_Psychology_Biohacking_Family", ("health", "doctor", "surgery", "psychology", "therapy", "longevity", "diagnostic", "supplement")),
    ("09_Spooky2_Frequency_Energy_Protocols", ("spooky2", "rife", "pemf", "pbm", "scalar", "frequency protocol")),
    ("10_Grow_Hydroponics_Cannabis", ("hydroponic", "dwc", "cannabis", "nutrient", "grow light", "seedling")),
    ("13_Business_Side_Hustles_Ecommerce", ("side hustle", "ecommerce", "ebay", "dropshipping", "vending", "micro-saas", "affiliate")),
]


class IntakeError(RuntimeError):
    pass


@dataclass(frozen=True)
class MessageRecord:
    conversation_id: str
    conversation_title: str
    message_id: str
    parent_id: str | None
    role: str
    create_time: float | None
    create_time_iso: str | None
    content_type: str
    content: str
    message_hash: str
    source_pointer: str
    secret_flag: bool


@dataclass(frozen=True)
class ConversationRecord:
    conversation_id: str
    title: str
    create_time: float | None
    update_time: float | None
    create_time_iso: str | None
    update_time_iso: str | None
    message_count: int
    user_message_count: int
    assistant_message_count: int
    system_message_count: int
    conversation_hash: str
    classification_primary: str
    classification_confidence: str
    classification_cross_links: tuple[str, ...]
    attachment_reference_count: int
    secret_flag_count: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iso_time(value: Any) -> str | None:
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        return None


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_member_name(name: str) -> str:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise IntakeError(f"unsafe archive member path: {name!r}")
    if ":" in path.parts[0]:
        raise IntakeError(f"unsafe drive-qualified archive member: {name!r}")
    if Path(path.name).suffix.lower() in EXECUTABLE_SUFFIXES:
        raise IntakeError(f"unexpected executable payload: {name!r}")
    return str(path)


def inspect_zip(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = safe_member_name(info.filename)
            if name in seen:
                raise IntakeError(f"duplicate archive output path: {name}")
            seen.add(name)
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise IntakeError(f"symbolic link member rejected: {name}")
            rows.append({
                "name": name,
                "size_bytes": info.file_size,
                "compressed_size_bytes": info.compress_size,
                "crc32": f"{info.CRC:08x}",
                "is_directory": info.is_dir(),
            })
    return rows


def extract_zip_member(path: Path, member_name: str, destination: Path) -> Path:
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo(member_name)
        safe_member_name(info.filename)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info, "r") as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target)
    return destination


def inspect_7z(path: Path) -> list[dict[str, Any]]:
    try:
        import py7zr  # type: ignore
    except ImportError as exc:
        raise IntakeError(
            "7z input detected but py7zr is not installed. Install py7zr in the isolated intake environment "
            "or provide the original OpenAI ZIP/conversations.json; do not use an unverified extractor."
        ) from exc
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    with py7zr.SevenZipFile(path, mode="r") as archive:
        for info in archive.list():
            name = safe_member_name(info.filename)
            if name in seen:
                raise IntakeError(f"duplicate archive output path: {name}")
            seen.add(name)
            if getattr(info, "is_symlink", False):
                raise IntakeError(f"symbolic link member rejected: {name}")
            rows.append({
                "name": name,
                "size_bytes": getattr(info, "uncompressed", None),
                "compressed_size_bytes": getattr(info, "compressed", None),
                "crc32": None,
                "is_directory": getattr(info, "is_directory", False),
            })
    return rows


def extract_7z_member(path: Path, member_name: str, destination: Path) -> Path:
    try:
        import py7zr  # type: ignore
    except ImportError as exc:
        raise IntakeError("py7zr is required for safe 7z extraction") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        with py7zr.SevenZipFile(path, mode="r") as archive:
            archive.extract(path=temporary, targets=[member_name])
        extracted = Path(temporary) / member_name
        if not extracted.is_file():
            raise IntakeError(f"7z member did not extract as a regular file: {member_name}")
        shutil.copy2(extracted, destination)
    return destination


def resolve_conversations_json(source: Path, workspace: Path) -> tuple[Path, dict[str, Any]]:
    source = source.resolve()
    if not source.is_file():
        raise IntakeError(f"source does not exist: {source}")
    suffix = source.suffix.lower()
    source_meta: dict[str, Any] = {
        "path": str(source),
        "size_bytes": source.stat().st_size,
        "sha256": sha256_file(source),
        "format": suffix.lstrip(".") or "unknown",
        "extraction_status": "NOT_REQUIRED",
        "member_inventory": [],
    }
    if suffix == ".json":
        return source, source_meta
    if suffix == ".zip":
        members = inspect_zip(source)
        source_meta["member_inventory"] = members
        candidates = [row["name"] for row in members if PurePosixPath(row["name"]).name == "conversations.json"]
        if len(candidates) != 1:
            raise IntakeError(f"expected exactly one conversations.json in ZIP, found {len(candidates)}")
        target = workspace / "extracted" / "conversations.json"
        extract_zip_member(source, candidates[0], target)
        source_meta.update({
            "extraction_status": "EXTRACTED_SAFE",
            "conversations_member": candidates[0],
            "conversations_sha256": sha256_file(target),
        })
        return target, source_meta
    if suffix == ".7z":
        members = inspect_7z(source)
        source_meta["member_inventory"] = members
        candidates = [row["name"] for row in members if PurePosixPath(row["name"]).name == "conversations.json"]
        if len(candidates) != 1:
            raise IntakeError(f"expected exactly one conversations.json in 7z, found {len(candidates)}")
        target = workspace / "extracted" / "conversations.json"
        extract_7z_member(source, candidates[0], target)
        source_meta.update({
            "extraction_status": "EXTRACTED_SAFE",
            "conversations_member": candidates[0],
            "conversations_sha256": sha256_file(target),
        })
        return target, source_meta
    raise IntakeError(f"unsupported source format: {suffix}; use .json, .zip, or .7z")


def content_to_text(content: dict[str, Any] | None) -> tuple[str, str, int]:
    if not content:
        return "unknown", "", 0
    content_type = str(content.get("content_type") or "unknown")
    parts = content.get("parts")
    attachment_refs = 0
    texts: list[str] = []
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, str):
                texts.append(part)
            elif isinstance(part, dict):
                if any(key in part for key in ("asset_pointer", "file_id", "upload_id", "image_asset_pointer")):
                    attachment_refs += 1
                texts.append(canonical_json(part))
            elif part is not None:
                texts.append(str(part))
    elif isinstance(content.get("text"), str):
        texts.append(content["text"])
    return content_type, "\n".join(texts).strip(), attachment_refs


def has_secret_marker(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in SECRET_MARKERS)


def classify(title: str, messages: list[MessageRecord]) -> tuple[str, str, tuple[str, ...]]:
    sample = " ".join([title] + [message.content for message in messages[:24]]).lower()
    scores: list[tuple[int, str]] = []
    for project, keywords in PROJECT_RULES:
        score = sum(sample.count(keyword) for keyword in keywords)
        if score:
            scores.append((score, project))
    if not scores:
        return "99_Miscellaneous_Mini_Projects", "Ambiguous", ()
    scores.sort(reverse=True)
    primary_score, primary = scores[0]
    cross_links = tuple(project for score, project in scores[1:] if score >= max(1, primary_score // 3))
    confidence = "Confirmed" if primary_score >= 8 else "Strong" if primary_score >= 4 else "Probable" if primary_score >= 2 else "Possible"
    return primary, confidence, cross_links


def ordered_nodes(conversation: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mapping = conversation.get("mapping") or {}
    if not isinstance(mapping, dict):
        return []
    rows = list(mapping.items())
    rows.sort(key=lambda item: (
        (item[1].get("message") or {}).get("create_time") is None,
        (item[1].get("message") or {}).get("create_time") or 0,
        item[0],
    ))
    return rows


def parse_export(path: Path) -> tuple[list[ConversationRecord], list[MessageRecord], list[dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise IntakeError("conversations.json root must be a list")
    conversations: list[ConversationRecord] = []
    all_messages: list[MessageRecord] = []
    gaps: list[dict[str, Any]] = []
    seen_conversation_ids: set[str] = set()
    seen_message_ids: set[str] = set()
    for index, conversation in enumerate(data):
        if not isinstance(conversation, dict):
            gaps.append({"type": "INVALID_CONVERSATION", "index": index, "reason": "not an object"})
            continue
        conversation_id = str(conversation.get("id") or conversation.get("conversation_id") or f"missing-id-{index}")
        if conversation_id in seen_conversation_ids:
            gaps.append({"type": "DUPLICATE_CONVERSATION_ID", "conversation_id": conversation_id, "index": index})
        seen_conversation_ids.add(conversation_id)
        title = str(conversation.get("title") or "Untitled")
        messages: list[MessageRecord] = []
        attachment_count = 0
        for node_id, node in ordered_nodes(conversation):
            message = node.get("message")
            if not isinstance(message, dict):
                continue
            message_id = str(message.get("id") or node_id)
            if message_id in seen_message_ids:
                gaps.append({"type": "DUPLICATE_MESSAGE_ID", "message_id": message_id, "conversation_id": conversation_id})
            seen_message_ids.add(message_id)
            role = str((message.get("author") or {}).get("role") or "unknown")
            content_type, text, attachments = content_to_text(message.get("content"))
            attachment_count += attachments
            create_time = message.get("create_time")
            digest = {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "parent_id": node.get("parent"),
                "role": role,
                "create_time": create_time,
                "content_type": content_type,
                "content": text,
            }
            record = MessageRecord(
                conversation_id=conversation_id,
                conversation_title=title,
                message_id=message_id,
                parent_id=node.get("parent"),
                role=role,
                create_time=float(create_time) if isinstance(create_time, (int, float)) else None,
                create_time_iso=iso_time(create_time),
                content_type=content_type,
                content=text,
                message_hash=sha256_bytes(canonical_json(digest).encode("utf-8")),
                source_pointer=f"conversation:{conversation_id}/mapping:{node_id}/message:{message_id}",
                secret_flag=has_secret_marker(text),
            )
            messages.append(record)
            all_messages.append(record)
        primary, confidence, cross_links = classify(title, messages)
        conversation_hash = sha256_bytes(canonical_json({
            "conversation_id": conversation_id,
            "title": title,
            "message_hashes": [message.message_hash for message in messages],
        }).encode("utf-8"))
        role_counts: dict[str, int] = {}
        for message in messages:
            role_counts[message.role] = role_counts.get(message.role, 0) + 1
        conversations.append(ConversationRecord(
            conversation_id=conversation_id,
            title=title,
            create_time=float(conversation["create_time"]) if isinstance(conversation.get("create_time"), (int, float)) else None,
            update_time=float(conversation["update_time"]) if isinstance(conversation.get("update_time"), (int, float)) else None,
            create_time_iso=iso_time(conversation.get("create_time")),
            update_time_iso=iso_time(conversation.get("update_time")),
            message_count=len(messages),
            user_message_count=role_counts.get("user", 0),
            assistant_message_count=role_counts.get("assistant", 0),
            system_message_count=role_counts.get("system", 0),
            conversation_hash=conversation_hash,
            classification_primary=primary,
            classification_confidence=confidence,
            classification_cross_links=cross_links,
            attachment_reference_count=attachment_count,
            secret_flag_count=sum(1 for message in messages if message.secret_flag),
        ))
    return conversations, all_messages, gaps


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def conversation_to_row(record: ConversationRecord) -> dict[str, Any]:
    row = asdict(record)
    row["classification_cross_links"] = "|".join(record.classification_cross_links)
    return row


def build_outputs(source: Path, out: Path) -> dict[str, Any]:
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    workspace = out / "_workspace"
    conversations_path, source_meta = resolve_conversations_json(source, workspace)
    conversations, messages, gaps = parse_export(conversations_path)
    conversation_rows = [conversation_to_row(record) for record in conversations]
    message_rows = [asdict(record) for record in messages]
    write_json(out / "source_manifest.json", {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "source": source_meta,
        "raw_preserved": True,
        "raw_copied": False,
        "proof_boundary": "Derived artifacts only; raw source remains at its original path and hash.",
    })
    fields = list(conversation_rows[0].keys()) if conversation_rows else list(ConversationRecord.__dataclass_fields__)
    write_csv(out / "conversation_index.csv", conversation_rows, fields)
    write_jsonl(out / "conversation_index.jsonl", conversation_rows)
    write_jsonl(out / "messages.jsonl", message_rows)
    write_json(out / "extraction_gaps.json", gaps)
    project_counts: dict[str, int] = {}
    for record in conversations:
        project_counts[record.classification_primary] = project_counts.get(record.classification_primary, 0) + 1
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_WITH_GAPS" if gaps else "PASS",
        "source_sha256": source_meta["sha256"],
        "conversation_count": len(conversations),
        "message_count": len(messages),
        "user_message_count": sum(record.user_message_count for record in conversations),
        "assistant_message_count": sum(record.assistant_message_count for record in conversations),
        "system_message_count": sum(record.system_message_count for record in conversations),
        "attachment_reference_count": sum(record.attachment_reference_count for record in conversations),
        "secret_flag_count": sum(record.secret_flag_count for record in conversations),
        "gap_count": len(gaps),
        "classification_counts": project_counts,
        "reconciled": sum(record.message_count for record in conversations) == len(messages),
        "truth_boundary": "Counts cover only the supplied parseable export. Classification is a deterministic candidate and requires review for ambiguous or high-risk domains.",
    }
    write_json(out / "coverage_report.json", report)
    shutil.rmtree(workspace, ignore_errors=True)
    return report


def load_index(path: Path) -> dict[str, dict[str, Any]]:
    if path.is_dir():
        path = path / "conversation_index.jsonl"
    rows: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows[row["conversation_id"]] = row
    return rows


def delta_scan(baseline_index: Path, current_index: Path, out: Path) -> dict[str, Any]:
    baseline = load_index(baseline_index)
    current = load_index(current_index)
    new_ids = sorted(set(current) - set(baseline))
    removed_ids = sorted(set(baseline) - set(current))
    common_ids = sorted(set(current) & set(baseline))
    changed_ids = [conversation_id for conversation_id in common_ids if current[conversation_id].get("conversation_hash") != baseline[conversation_id].get("conversation_hash")]
    unchanged_ids = [conversation_id for conversation_id in common_ids if conversation_id not in changed_ids]
    out.mkdir(parents=True, exist_ok=True)
    fields = [
        "conversation_id", "title", "create_time", "update_time", "create_time_iso", "update_time_iso",
        "message_count", "user_message_count", "assistant_message_count", "system_message_count",
        "conversation_hash", "classification_primary", "classification_confidence",
        "classification_cross_links", "attachment_reference_count", "secret_flag_count",
    ]
    write_csv(out / "delta_new_chats.csv", [current[item] for item in new_ids], fields)
    changed_rows = []
    for conversation_id in changed_ids:
        row = dict(current[conversation_id])
        row["baseline_conversation_hash"] = baseline[conversation_id].get("conversation_hash")
        row["baseline_message_count"] = baseline[conversation_id].get("message_count")
        changed_rows.append(row)
    write_csv(out / "delta_changed_chats.csv", changed_rows, fields + ["baseline_conversation_hash", "baseline_message_count"])
    write_csv(out / "delta_removed_or_missing_review.csv", [baseline[item] for item in removed_ids], fields)
    write_csv(out / "delta_duplicate_review.csv", [], ["conversation_id", "candidate_duplicate_id", "reason", "review_status"])
    pack_rows = []
    for conversation_id in new_ids + changed_ids:
        row = current[conversation_id]
        pack_rows.append({
            "conversation_id": conversation_id,
            "title": row.get("title"),
            "change_type": "NEW" if conversation_id in new_ids else "CHANGED",
            "target_project": row.get("classification_primary"),
            "confidence": row.get("classification_confidence"),
            "pack_status": "REVIEW_REQUIRED" if row.get("classification_confidence") in {"Ambiguous", "Possible"} else "READY_CANDIDATE",
        })
    write_csv(out / "delta_project_pack_update_manifest.csv", pack_rows, ["conversation_id", "title", "change_type", "target_project", "confidence", "pack_status"])
    gap_lines = [
        "# Delta Gap Log", "", f"- New conversations: {len(new_ids)}",
        f"- Changed conversations: {len(changed_ids)}",
        f"- Unchanged conversations: {len(unchanged_ids)}",
        f"- Missing/removed review: {len(removed_ids)}", "",
    ]
    gap_lines.append(
        "Missing conversations are review items, not deletions. Confirm export scope/account before any supersession decision."
        if removed_ids else "No baseline conversations are missing from the current supplied index."
    )
    (out / "delta_gap_log.md").write_text("\n".join(gap_lines) + "\n", encoding="utf-8")
    report = {
        "schema_version": SCHEMA_VERSION,
        "baseline_count": len(baseline),
        "current_count": len(current),
        "new_count": len(new_ids),
        "changed_count": len(changed_ids),
        "unchanged_count": len(unchanged_ids),
        "removed_or_missing_review_count": len(removed_ids),
        "status": "PASS",
        "truth_boundary": "Missing IDs are review candidates, not proof of deletion. Conversation-ID comparison is primary; message-hash fingerprint determines changed status.",
    }
    write_json(out / "delta_report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="Inspect and extract one ChatGPT export")
    ingest.add_argument("source", type=Path)
    ingest.add_argument("--out", required=True, type=Path)
    delta = commands.add_parser("delta", help="Compare two generated conversation indexes")
    delta.add_argument("baseline_index", type=Path)
    delta.add_argument("current_index", type=Path)
    delta.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_outputs(args.source, args.out) if args.command == "ingest" else delta_scan(args.baseline_index, args.current_index, args.out)
        print(json.dumps(report, indent=2))
        return 0
    except (IntakeError, json.JSONDecodeError, zipfile.BadZipFile, OSError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
