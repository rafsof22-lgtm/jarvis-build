# Jarvis ChatGPT Attachment Intake Report

**Snapshot:** 22 July 2026 — Australia/Melbourne  
**Source:** Google Drive `chatgpt_exports/chatgpt-attachments.zip`  
**Archive SHA-256:** `9544b9cefe7651f95f59abcb47093f028b09670830c32c0e7080dccd12761445`

## Outcome

The new attachment archive has completed a safe, non-destructive metadata, CRC and content-hash pass. Raw archive bytes were preserved. No files were deleted or promoted to canonical status. Attachment-to-chat/message linkage remains blocked until the non-empty JSONL is available.

## Proven archive denominator

| Measure | Proven value | State |
|---|---:|---|
| ZIP members | 240 | PROVEN |
| Directories | 17 | PROVEN |
| Files | 223 | PROVEN |
| Attachment-bearing chat folders | 16 | PROVISIONAL_CHAT_STUBS |
| Uncompressed bytes | 941,083,665 | PROVEN |
| Unique content hashes | 182 | PROVEN |
| Exact duplicate groups | 30 | PROVEN |
| Redundant copies | 41 | PROVEN_PRESERVED |
| Estimated repeated uncompressed bytes | 340,494,190 | PROVEN |

## Safety tests

- ZIP CRC: **PASS**
- Unsafe/traversal paths: **0**
- Symlinks: **0**
- Executable payloads: **0**
- Member read/hash errors: **0**
- Nested ZIP CRC failures: **0**

## Content distribution

- Text/code: **95**
- Images: **108**
- Documents: **9**
- Partial `.raw` recovery copies: **5**
- Nested ZIP evidence packages: **5**
- Other/checksum: **1**

## Requirement and reconstruction evidence recovered

| Evidence register | Records | Current proof state |
|---|---:|---|
| Three-pass reconciliation matrix | 3,014 | All `SPEC_ONLY`; tests `NOT_RUN`; not independently verified |
| Historical promotion candidates | 2,719 | Proposed only |
| Expanded new-requirement review | 671 | 394 superseded-not-deleted; 156 spec-only; 121 blocked |
| Manual conflict resolutions | 174 | Resolved for canonical review, not runtime proof |

## Historical workspace archive evidence

The attachments include a prior manifest for `KIMI_WORKSPACE_RAW.7z`: **4,070 entries**, **3,314 streamed files**, **667 directories**, and **417,631,661 source bytes**. The five `folder0_partial.raw` files are exact duplicates of one 75 MB truncated mixed-content stream. One copy contains **1,505,531 lines** and ends mid-source-file; it is historical partial recovery evidence, not complete extraction.

## Claim reconciliation

A historical report states `100% COMPLETE` and `LIVE IN PRODUCTION`. That claim is not accepted as current truth. The machine-readable registers show 3,014 groups remain specification-only, with no tests run and no independent verification. Current state: `NEEDS_PROOF`.

## Nested evidence

Five nested ZIPs passed CRC inspection. The XRP/HBAR test evidence shows an earlier run at **19 pass / 3 fail** followed by **22 pass / 0 fail**. This proves bounded test improvement only; it does not prove production deployment.

## Privacy and quarantine

Contact datasets, tax/SMSF PDFs, personal/legal/health documents, and property documents/images were inventoried and hashed but not semantically read. Selected Jarvis governance, build and machine-register files were inspected.

## Exact blocker

`BLOCKED_AT_EXACT_STEP: ATTACHMENT_TO_CONVERSATION_AND_MESSAGE_LINKAGE`

The Google Drive JSONL is still zero bytes. When it becomes non-zero, the prepared workflow is: hash -> parse -> conversation/message index -> attachment reference matching -> 25 June delta -> Jarvis classification -> requirement traceability -> updated project packs.
