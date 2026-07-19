# Registry and Evidence Contracts

Minimum requirement row: requirement_id; verbatim_text; normalized_requirement; source_ids; source_pointers; classification; priority; owner; master_section; module_id; agent_ids; integration_ids; implementation_path; test_ids; evidence_ids; status; assumptions; risks; gaps; decision_ids; created_at; updated_at.

Minimum agent row: agent_id; name; purpose; owner; triggers; inputs; outputs; allowed_tools; denied_tools; data_scope; memory_policy; autonomy_level; approval_gate; token_limit; cost_limit; timeout; retry_limit; audit_events; health_signals; failure_modes; rollback; safe_stop; test_ids; status.

Minimum integration row: integration_id; provider; purpose; auth_type; scopes; secret_location; free_or_paid; estimated_cost; rate_limits; test_ping; sample_run; evidence_writes; failure_modes; rollback; health_check; owner; status.

Minimum instruction-applicability row: instruction_id; verbatim_source; normalized_rule; applicability_class; runtime_artifacts; chat_artifacts; module_ids; conflicts; tests; evidence; status; reason; created_at; updated_at.

Minimum source-intelligence row: finding_id; source_id; source_class; pointer; date; maintenance_status; claims; extracted_patterns; negative_lessons; confidence; cross_checks; applicability; affected_capabilities; disposition; pilot_id; evidence_ids; status.

Evidence contract: request_id; owner; scope; plan; agents; tools; sources; models/providers; cost; approvals; actions; outputs; tests; risks; rollback_point; timestamps; hashes/artifact_refs; final_status.

No-gaps gate: every source accounted for; every extractable unit extracted or failed with reason; every chunk linked or excluded; every applicable requirement mapped to master/module/implementation/test/evidence; every durable instruction classified; discrepancies/integrity reports exist; runtime truth reconciled; denominator and exclusions disclosed.