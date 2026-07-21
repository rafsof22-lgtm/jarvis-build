# Cost + $1 Auto Parts — Reconciled Build Plan

**Snapshot:** 21 July 2026 (Melbourne)

## Outcome

The exact project export, the new handoff pack and the current merged Jarvis business runtime are now reconciled. The old handoff blocker stating that the Jarvis repository was unavailable is superseded. The programme remains implementation-incomplete because most customer, supplier, accounting, logistics and physical-fulfilment functions are specification-only or externally gated.

## Verified source denominator

- Exact export lineage: 14 top-level Cost project conversations containing 14,602 messages.
- One additional mixed-lineage conversation contains Cost-tagged message metadata; the broad envelope therefore spans 15 conversations / 14,654 messages.
- Exactly 3,804 messages carry Cost project gizmo metadata.
- Cost handoff ZIP: 50 members; 13 bundled primary sources; one historical export intentionally excluded.
- Canonical handoff register: 18 requirements and 12 module rows.
- Both uploaded DOCX files exactly match their handoff members.
- `COST AUTO PARTS FINAL1.docx` is a substantially expanded version, not a byte/text duplicate of `COST AUTO PARTS FINAL.docx`; preserve both.
- The handoff's 84-chat WFW claim is not accepted because the included conversation, user and assistant ledgers are empty.

## Architecture decision

Use a **Jarvis-owned custom automotive domain core** with adapter interfaces. An optional Odoo adapter may later supply commodity ERP functions after evaluation, but Odoo must not own the canonical business rules. Xero remains the accounting ledger/export boundary, not the operational order/fitment/logistics source of truth. This keeps the system reversible, testable and free-first while avoiding lock-in.

## Build sequence

1. Define schemas and events for order, supplier, pickup, delivery, billing, warranty and Jenok catalogue workflows.
2. Implement SQLite-backed local reference runtime with idempotency, audit evidence and deterministic tests.
3. Add customer/member, trade, workshop and vehicle profiles.
4. Add quote, pricing-tier and membership rules while preserving the exact Cost + A$1 formula as a separate product/channel policy.
5. Add supplier adapter contract and CSV/email/manual fallbacks before any live API.
6. Add zone/run/locker/trolley allocation, scan checkpoints, discrepancy queue and proof of delivery.
7. Add Xero export adapter, direct-debit proposal interface and monthly-fee calculation with legal/accounting gates.
8. Add Command Centre cards and approval queues.
9. Run staging with synthetic data, load, accessibility, backup, restore and rollback tests.
10. Request owner/provider approvals only after evidence is complete.

## Principal unresolved decisions

- Trade pricing variants: 20%, 25%, Cost + A$1 and tiered markup remain separate candidate policies until an approved financial model selects channel-specific rules.
- Workshop compensation: labour-only, lead fee, margin share and rebate variants require unit economics and legal review.
- Physical locker geometry: latest 20-per-side / 40-side-locker plus centre-trolley correction controls specification, but engineering drawings and safety proof remain absent.
- Supplier terms, data rights, payment, GST, warranty and consumer-law treatment require current official and professional verification.

## Completion boundary

Repository-local schemas, code and tests can advance autonomously. Live suppliers, payments, Xero OAuth, production logistics, external communications, spending, legal acceptance and production promotion remain approval-gated.
