#!/usr/bin/env python3
"""Normalize ChatGPT JSONL exports and reconcile attachment references safely.

This is a narrow preprocessor for ``chatgpt_kb_intake_v1.py``. It preserves the
raw JSONL and ZIP inputs, rejects unsafe ZIP members, produces a normalized
``conversations.json``, inventories attachment members with hashes, and emits
reference/linkage ledgers. It does not publish raw message or attachment bodies.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator

SCHEMA_VERSION = "1.0.0"
ATTACHMENT_KEYS = ("asset_pointer", "file_id", "upload_id", "image_asset_pointer")
FILENAME_KEYS = ("filename", "file_name", "name")
EXECUTABLE_SUFFIXES = {
    ".exe", ".dll", ".so", ".dylib", ".bat", ".cmd", ".com", ".msi",
    ".scr", ".ps1", ".sh", ".app", ".jar", ".apk", ".deb", ".rpm",
}


class PreprocessError(RuntimeError):
    """Raised for unsafe, empty, malformed, or unsupported input."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_stream(handle: Any) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def safe_member_name(name: str) -> str:
    candidate = PurePosixPath(name.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise PreprocessError(f"unsafe archive member path: {name!r}")
    if ":" in candidate.parts[0]:
        raise PreprocessError(f"unsafe drive-qualified archive member: {name!r}")
    if Path(candidate.name).suffix.lower() in EXECUTABLE_SUFFIXES:
        raise PreprocessError(f"unexpected executable payload: {name!r}")
    return str(candidate)


def expand_json_value(value: Any, line_number: int) -> Iterator[dict[str, Any]]:
    if isinstance(value, list):
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                raise PreprocessError(
                    f"JSONL line {line_number} list item {index} is not an object"
                )
            yield item
        return
    if not isinstance(value, dict):
        raise PreprocessError(f"JSONL line {line_number} is not an object or list")
    conversations = value.get("conversations")
    if isinstance(conversations, list):
        yield from expand_json_value(conversations, line_number)
        return
    conversation = value.get("conversation")
    if isinstance(conversation, dict):
        yield conversation
        return
    yield value


def iter_jsonl_conversations(path: Path) -> Iterator[dict[str, Any]]:
    if not path.is_file():
        raise PreprocessError(f"JSONL source does not exist: {path}")
    if path.stat().st_size == 0:
        raise PreprocessError("JSONL source is zero bytes; upload is incomplete or empty")
    yielded = 0
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise PreprocessError(
                    f"invalid JSON on JSONL line {line_number}: {exc.msg} at column {exc.colno}"
                ) from exc
            for conversation in expand_json_value(value, line_number):
                yielded += 1
                yield conversation
    if yielded == 0:
        raise PreprocessError("JSONL source contains no conversation objects")


def normalize_jsonl(source: Path, destination: Path) -> tuple[int, list[dict[str, Any]]]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    references: list[dict[str, Any]] = []
    count = 0
    with destination.open("w", encoding="utf-8") as handle:
        handle.write("[\n")
        first = True
        for conversation in iter_jsonl_conversations(source):
            if not first:
                handle.write(",\n")
            handle.write(json.dumps(conversation, ensure_ascii=False, sort_keys=True))
            first = False
            references.extend(extract_attachment_references(conversation, count))
            count += 1
        handle.write("\n]\n")
    return count, references


def walk_reference_values(value: Any, path: str = "") -> Iterator[tuple[str, Any, dict[str, Any]]]:
    if isinstance(value, dict):
        context = {key: value.get(key) for key in FILENAME_KEYS if value.get(key) not in (None, "")}
        if value.get("mime_type") not in (None, ""):
            context["mime_type"] = value.get("mime_type")
        for key, child in value.items():
            child_path = f"{path}/{key}" if path else key
            if key in ATTACHMENT_KEYS and child not in (None, ""):
                yield child_path, child, context
            yield from walk_reference_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}/{index}" if path else str(index)
            yield from walk_reference_values(child, child_path)


def extract_attachment_references(conversation: dict[str, Any], index: int) -> list[dict[str, Any]]:
    conversation_id = str(conversation.get("id") or conversation.get("conversation_id") or f"missing-id-{index}")
    title = str(conversation.get("title") or "Untitled")
    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return []
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for node_id, node in mapping.items():
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        message_id = str(message.get("id") or node_id)
        content = message.get("content")
        for json_path, raw_value, context in walk_reference_values(content):
            reference_value = str(raw_value)
            reference_key = json_path.rsplit("/", 1)[-1]
            signature = (message_id, reference_key, reference_value, json_path)
            if signature in seen:
                continue
            seen.add(signature)
            filename = next((str(context[key]) for key in FILENAME_KEYS if context.get(key)), "")
            rows.append({
                "conversation_id": conversation_id,
                "conversation_title": title,
                "node_id": str(node_id),
                "message_id": message_id,
                "reference_key": reference_key,
                "reference_value": reference_value,
                "filename": filename,
                "mime_type": str(context.get("mime_type") or ""),
                "json_path": json_path,
                "source_pointer": f"conversation:{conversation_id}/mapping:{node_id}/message:{message_id}/{json_path}",
            })
    return rows


def inspect_attachment_zip(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not path.is_file():
        raise PreprocessError(f"attachment ZIP does not exist: {path}")
    rows: list[dict[str, Any]] = []
    hash_groups: dict[str, list[str]] = defaultdict(list)
    seen_paths: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise PreprocessError(f"attachment ZIP CRC failure: {bad_member}")
        for info in archive.infolist():
            member_path = safe_member_name(info.filename)
            if member_path in seen_paths:
                raise PreprocessError(f"duplicate archive output path: {member_path}")
            seen_paths.add(member_path)
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise PreprocessError(f"symbolic link member rejected: {member_path}")
            if info.is_dir():
                continue
            with archive.open(info, "r") as member_handle:
                member_hash = sha256_stream(member_handle)
            posix = PurePosixPath(member_path)
            row = {
                "member_path": member_path,
                "basename": posix.name,
                "top_level_folder": posix.parts[0] if len(posix.parts) > 1 else "",
                "extension": Path(posix.name).suffix.lower(),
                "size_bytes": info.file_size,
                "compressed_size_bytes": info.compress_size,
                "crc32": f"{info.CRC:08x}",
                "sha256": member_hash,
            }
            rows.append(row)
            hash_groups[member_hash].append(member_path)
    duplicate_groups = [
        {"sha256": digest, "copy_count": len(paths), "member_paths": sorted(paths)}
        for digest, paths in sorted(hash_groups.items()) if len(paths) > 1
    ]
    return rows, duplicate_groups


def normalized_tokens(value: str) -> set[str]:
    tokens = {value.strip(), Path(value.strip()).name}
    for prefix in ("file-service://", "sandbox:/mnt/data/", "attachment://"):
        if value.startswith(prefix):
            tokens.add(value[len(prefix):])
            tokens.add(Path(value[len(prefix):]).name)
    return {token.lower() for token in tokens if token}


def reconcile_references(
    references: list[dict[str, Any]], members: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for reference in references:
        ref_tokens = normalized_tokens(str(reference.get("reference_value") or ""))
        filename_tokens = normalized_tokens(str(reference.get("filename") or ""))
        conversation_id = str(reference.get("conversation_id") or "").lower()
        identifier_matches: list[dict[str, Any]] = []
        filename_matches: list[dict[str, Any]] = []
        folder_matches: list[dict[str, Any]] = []
        for member in members:
            member_path = str(member["member_path"]).lower()
            basename = str(member["basename"]).lower()
            top_level = str(member["top_level_folder"]).lower()
            if ref_tokens and any(token == basename or token in member_path for token in ref_tokens):
                identifier_matches.append(member)
            if filename_tokens and basename in filename_tokens:
                filename_matches.append(member)
            if conversation_id and top_level == conversation_id:
                folder_matches.append(member)
        candidates = identifier_matches or filename_matches or folder_matches
        if not candidates:
            status = "UNMATCHED"
        elif len(candidates) > 1:
            status = "AMBIGUOUS"
        elif identifier_matches:
            status = "EXACT_IDENTIFIER"
        elif filename_matches:
            status = "EXACT_FILENAME"
        else:
            status = "CONVERSATION_FOLDER_CANDIDATE"
        selected = candidates[0] if len(candidates) == 1 else {}
        results.append({
            **reference,
            "linkage_status": status,
            "candidate_count": len(candidates),
            "matched_member_path": selected.get("member_path", ""),
            "matched_member_sha256": selected.get("sha256", ""),
            "review_required": status in {"AMBIGUOUS", "CONVERSATION_FOLDER_CANDIDATE", "UNMATCHED"},
        })
    return results


def prepare(source: Path, out: Path, attachments: Path | None = None) -> dict[str, Any]:
    source = source.resolve()
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    raw_hash = sha256_file(source) if source.is_file() else None
    normalized_path = out / "normalized_conversations.json"
    conversation_count, references = normalize_jsonl(source, normalized_path)
    write_jsonl(out / "attachment_reference_ledger.jsonl", references)

    members: list[dict[str, Any]] = []
    duplicate_groups: list[dict[str, Any]] = []
    linkage_rows: list[dict[str, Any]] = []
    attachment_meta: dict[str, Any] | None = None
    if attachments is not None:
        attachments = attachments.resolve()
        members, duplicate_groups = inspect_attachment_zip(attachments)
        linkage_rows = reconcile_references(references, members)
        attachment_meta = {
            "path": str(attachments),
            "size_bytes": attachments.stat().st_size,
            "sha256": sha256_file(attachments),
            "member_count": len(members),
            "duplicate_group_count": len(duplicate_groups),
        }
        write_csv(
            out / "attachment_member_inventory.csv",
            members,
            ["member_path", "basename", "top_level_folder", "extension", "size_bytes", "compressed_size_bytes", "crc32", "sha256"],
        )
        write_json(out / "duplicate_attachment_groups.json", duplicate_groups)
        write_csv(
            out / "attachment_linkage.csv",
            linkage_rows,
            [
                "conversation_id", "conversation_title", "node_id", "message_id",
                "reference_key", "reference_value", "filename", "mime_type", "json_path",
                "source_pointer", "linkage_status", "candidate_count", "matched_member_path",
                "matched_member_sha256", "review_required",
            ],
        )

    status_counts: dict[str, int] = defaultdict(int)
    for row in linkage_rows:
        status_counts[str(row["linkage_status"])] += 1
    report = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "status": "PASS_WITH_REVIEW" if any(row.get("review_required") for row in linkage_rows) else "PASS",
        "jsonl_source": {
            "path": str(source),
            "size_bytes": source.stat().st_size,
            "sha256": raw_hash,
            "raw_preserved": True,
        },
        "normalized_conversations_path": str(normalized_path),
        "normalized_conversations_sha256": sha256_file(normalized_path),
        "conversation_count": conversation_count,
        "attachment_reference_count": len(references),
        "attachment_archive": attachment_meta,
        "linkage_status_counts": dict(sorted(status_counts.items())),
        "next_command": (
            "python scripts/chatgpt_kb_intake_v1.py ingest "
            f"{normalized_path} --out <current-output>"
        ),
        "truth_boundary": (
            "This preprocessor proves JSONL normalization and bounded attachment candidate linkage only. "
            "Project classification, delta reconciliation, sensitive-content review, runtime state and owner acceptance remain separate gates."
        ),
    }
    write_json(out / "jsonl_preflight_report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_jsonl", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--attachments", type=Path)
    args = parser.parse_args(argv)
    try:
        report = prepare(args.source_jsonl, args.out, args.attachments)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (PreprocessError, json.JSONDecodeError, zipfile.BadZipFile, OSError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
