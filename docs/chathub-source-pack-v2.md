# ChatHub Source Pack V2

## Verified source

The owner upload `Chathub INst Prmpt.txt` is treated as a controlling ChatHub extraction specification plus a raw multi-model source corpus. Its exact bytes remain available through the authorised upload pointer and are measured in the source registry by filename, SHA-256, byte count, line count and word count.

## V2 parsing contract

The V2 parser recognises explicit role markers such as `**user**:` and `**cloud-mistral-large**:`. It does not split ordinary Markdown headings that merely resemble labels. Every message records role, model, exact content, start/end lines, word count, SHA-256 and duplicate lineage.

Exact duplicates remain in the evidence manifest. An optional reproduction view may suppress only byte-identical repeats from the same role/model while retaining a pointer to the first occurrence.

## Instruction handling

The extraction prompt is preserved as source evidence. Operational rules derived from it are stored separately. Future filenames containing `ChatHub` or `Chat Hub` are routed automatically through:

1. immutable source accounting;
2. role-aware message extraction;
3. exact response and user-prompt manifests;
4. duplicate and fragment review;
5. separate consolidation;
6. requirement and capability routing;
7. progress and open-loop tracking.

No source wording is silently corrected, abbreviated or overwritten.

## Cross-module integration

Applicable requirements are mapped to existing owners for the control plane, Knowledge Fabric, model router, finance/CFO, trading research, legal/tax, health, digital income, Apollo/property, video intelligence, automation, security, UX and capability scouting. Mapping is not treated as implementation proof.

## Truth boundary

This tranche completes measured ingestion and routing for the supplied file. It does not prove that every domain module, external provider, credential, staging service or production deployment is complete. Those remain separately gated by implementation, tests, runtime evidence and owner approvals.
