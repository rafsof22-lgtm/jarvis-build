# ChatGPT JSONL and Attachment Preprocessor V1

**State:** `IMPLEMENTED_TESTED_NOT_YET_RUN_ON_NONEMPTY_2026-07-22_JSONL`  
**Purpose:** Normalize a line-delimited ChatGPT export into `conversations.json`, inventory the separately supplied attachment ZIP, and produce privacy-safe linkage candidates before the existing V19 intake and delta engine runs.

## Why this exists

The V19 engine accepts JSON, ZIP and optional 7Z sources. The 22 July 2026 Drive delivery uses a separate `.jsonl` conversation ledger plus `chatgpt-attachments.zip`. This preprocessor handles that delivery format without weakening or duplicating the V19 engine.

## Command

```bash
python scripts/chatgpt_jsonl_attachment_preprocessor_v1.py \
  /path/to/chatgpt-export-2026-07-22T01-35-30.jsonl \
  --attachments /path/to/chatgpt-attachments.zip \
  --out generated/kb/v20/jsonl-preflight
```

Then run the canonical intake engine:

```bash
python scripts/chatgpt_kb_intake_v1.py ingest \
  generated/kb/v20/jsonl-preflight/normalized_conversations.json \
  --out generated/kb/v20/current
```

Then compare with the preserved baseline index:

```bash
python scripts/chatgpt_kb_intake_v1.py delta \
  generated/kb/baseline/conversation_index.jsonl \
  generated/kb/v20/current/conversation_index.jsonl \
  --out generated/kb/v20/delta
```

## Outputs

- `normalized_conversations.json`
- `jsonl_preflight_report.json`
- `attachment_reference_ledger.jsonl`
- `attachment_member_inventory.csv`
- `duplicate_attachment_groups.json`
- `attachment_linkage.csv`

## Safety and truth boundary

- Zero-byte and malformed JSONL inputs fail closed.
- ZIP path traversal, drive-qualified paths, symlinks, duplicate destinations, executable payloads and CRC failures are rejected.
- Raw inputs remain unchanged and outside Git history.
- Attachment matching is a candidate linkage, not proof of conversation membership unless identifiers reconcile unambiguously.
- No raw message or attachment body should be committed to GitHub.
- Full completion still requires intake reconciliation, baseline delta, project classification review, requirement traceability, tests, evidence, rollback and owner acceptance.
