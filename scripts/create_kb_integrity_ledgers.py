#!/usr/bin/env python3
from pathlib import Path
import csv
import sys

SCHEMAS = {
    "per_request_kb_update_log.csv": ["request_id","request","prior_baseline","requirements_added","gaps_filled","files_changed","validation_status","replacement_package","rollback_package","installation_status","next_skill"],
    "archive_integrity_register.csv": ["archive_id","path","sha256","format","size_bytes","extraction_status","unsafe_entries","corruption_status","notes"],
    "source_lineage_register.csv": ["lineage_id","raw_source","raw_sha256","extracted_file","record_id","classification","instruction_candidate","accepted_output","proof_status"],
    "conversation_coverage_register.csv": ["conversation_id","title","message_count_expected","message_count_extracted","replica_status","classification_status","gap","review_status"],
    "classification_conflict_register.csv": ["record_id","candidate_projects","conflict_reason","evidence","decision","review_owner","status"],
    "privacy_retention_register.csv": ["item_id","data_class","pii_status","secret_status","redaction_required","retention_rule","deletion_rule","approval_status"],
    "baseline_rollback_register.csv": ["version_id","package","sha256","created_at","working_status","superseded_by","rollback_ready","installation_status"],
    "pack_reconciliation_register.csv": ["pack_id","source_files","extracted_files","conversation_records","message_records","classified_records","replicas","pack_files","reconciled","gap"],
    "next_action_queue.csv": ["action_id","priority","action","owner","approval_required","blocker","verification","status"],
}


def main() -> int:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    output.mkdir(parents=True, exist_ok=True)
    for name, fields in SCHEMAS.items():
        with (output / name).open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerow(fields)
    print(f"created {len(SCHEMAS)} ledgers in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
