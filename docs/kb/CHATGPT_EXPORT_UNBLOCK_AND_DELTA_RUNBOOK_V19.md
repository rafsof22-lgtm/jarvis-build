# ChatGPT Export Unblock and Delta Runbook V19

**Status:** `IMPLEMENTED_NOT_INTEGRATED`  
**Scope:** ChatGPT export acquisition, secure intake, hashing, extraction, reconciliation, full-content classification candidates, delta processing and project-pack routing.  
**Truth boundary:** The intake system is ready and tested. The newest export archive bytes are not presently accessible, so no post-25-June conversation body has been claimed as processed.

## Smallest unblock action

Upload the newest **original ChatGPT data-export ZIP** generated after `2026-06-25`. Do not unzip, rename internal members, edit `conversations.json`, or include passwords, session cookies, API keys, MFA codes, recovery codes or private keys.

Accepted alternatives:

1. Upload `conversations.json` directly.
2. Upload the previously referenced `chatgpt-export-2026-06-12T06-47-34.7z` together with a newer export for a true delta comparison.
3. Upload explicit transcripts/source packs for the eight inaccessible shared conversations.

The original OpenAI ZIP is preferred because it preserves the provider archive structure and gives the strongest source-integrity evidence.

## Stage workflow

| Stage | Action | Evidence |
|---|---|---|
| 0 | Register source, size, format and proof limits | `source_manifest.json` |
| 1 | Hash raw source and inspect archive members | SHA-256 and member inventory |
| 2 | Reject traversal, absolute paths, symlinks, duplicate outputs and executable payloads | Failed intake with exact reason |
| 3 | Extract exactly one `conversations.json` | Extracted member name and hash |
| 4 | Extract conversation/message metadata and content | `conversation_index.*`, `messages.jsonl` |
| 5 | Reconcile role and message counts | `coverage_report.json` |
| 6 | Flag attachment references and secret-like text | Per-record flags; no secret values promoted |
| 7 | Generate full-content classification candidates | Primary project, confidence and cross-links |
| 8 | Compare against baseline by conversation ID and message hash | Delta CSVs and `delta_report.json` |
| 9 | Route ambiguous, removed/missing and high-risk records to review | Review and gap registers |
| 10 | Update packs, trackers and continuity only after reconciliation | PR, CI and evidence |

## Commands

### Create integrity-ledger templates

```bash
python scripts/create_kb_integrity_ledgers.py generated/kb/v19/ledgers
```

### Ingest a ZIP, JSON or supported 7z archive

```bash
python scripts/chatgpt_kb_intake_v1.py ingest \
  /path/to/chatgpt-export.zip \
  --out generated/kb/v19/current
```

For `.7z`, use an isolated environment with `py7zr`. If it is unavailable, the tool fails safely and instructs the operator to provide the original ZIP or `conversations.json`; it does not fall back to an unverified extractor.

### Compare a previous and current index

```bash
python scripts/chatgpt_kb_intake_v1.py delta \
  generated/kb/baseline/conversation_index.jsonl \
  generated/kb/v19/current/conversation_index.jsonl \
  --out generated/kb/v19/delta
```

## Required outputs

### Intake

- `source_manifest.json`
- `conversation_index.csv`
- `conversation_index.jsonl`
- `messages.jsonl`
- `extraction_gaps.json`
- `coverage_report.json`

### Delta

- `delta_new_chats.csv`
- `delta_changed_chats.csv`
- `delta_duplicate_review.csv`
- `delta_removed_or_missing_review.csv`
- `delta_project_pack_update_manifest.csv`
- `delta_gap_log.md`
- `delta_report.json`

## Classification rules

Classification uses full available content, not titles alone. It produces candidates for the Master ChatGPT KB projects and cross-links. `Ambiguous` and `Possible` records require review. Health, legal/tax, financial and credential-bearing records retain their specialist approval and privacy gates.

## Missing-conversation rule

A conversation present in the baseline but absent from the newest export is a **review item**, not evidence that it was deleted or superseded. Confirm account, workspace and export scope before making any archival decision.

## Baseline limitation

The verified historical denominator is `2,610 conversations / 357,835 messages`, but the corresponding raw archive is not currently available through the connected File Library or tracked repository. Therefore:

- a newer export can be fully indexed immediately;
- a true content delta requires either the prior raw archive or its preserved `conversation_index.jsonl`;
- if neither prior artifact can be recovered, the newer export becomes a new candidate baseline only after source accounting and owner acceptance;
- historical denominators remain preserved and are not silently replaced.

## Security and privacy

- Raw archives remain outside Git history unless an explicit private source-vault policy authorises storage.
- Derived message content must be reviewed before repository publication.
- Secret-like content is flagged and must be redacted or excluded.
- No raw health, legal, financial or personally identifying content enters public repository artifacts.
- Raw source, derived records, classification decisions and project packs retain separate lineage.

## Completion gate

This workstream is `DONE_VERIFIED` only when:

`Raw source -> SHA-256 -> safe extraction -> conversation/message reconciliation -> classification review -> delta reconciliation -> project-pack update -> tests -> evidence -> owner acceptance`
