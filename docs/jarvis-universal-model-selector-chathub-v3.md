# Jarvis Universal Model Selector, Parallel Thinking and ChatHub Intake V3

## Outcome

This tranche upgrades the existing route-level model panel into a concrete per-model catalogue and shared selector contract. It also accounts for three supplied ChatHub text sources without treating model-generated proposals as approved requirements.

## Model selection

Each configured route may declare one default model and any number of additional models through `JARVIS_<ROUTE_NAME>_MODELS`. All concrete model IDs become selector options. Unknown model IDs are never fabricated.

The shared selector contract applies to Jarvis Pop, Command Centre, editors, builders, source analysis, evaluations and deployment configuration. A standalone Command Centre model-control panel renders the connected options and the `Parallel Thinking · Up to 8 LLMs` button.

## Parallel panel proof

A panel uses two to eight unique models. Every raw output is retained. The synthesis packet requires response hashes, claims, citations, contradictions, omissions and required-section coverage. The final verifier uses `selector_id + response_sha256`, so identical outputs from different models cannot be accidentally collapsed.

## Supplied ChatHub denominator

- `Chathub Health.txt`: 872,934 bytes; SHA-256 `2c1513e3d846055eabe0df8fd025f36251b1586201cc3b3f639d159841a97405`.
- `Chathub INst Prmpt(1).txt`: 804,767 bytes; SHA-256 `7073bfef49bedca84df4097bbd3b6eafff2399b1a86c66bb0349ffaec7c81d74`.
- `ChathubApolloSearch.txt`: 378,053 bytes; SHA-256 `65d52194d8bde549abd90562e8bf0ea464a3df39a32d61325f8798617e353c65`.

Total: 2,055,754 bytes, 43,776 parser-counted lines, 268,012 words, 143 explicit role messages, 72 user prompts and 71 model responses.

Every message is reproducibly assigned a source line range, message hash, role/authority, model identity when applicable, duplicate lineage, module routes, risk flags and disposition by the V3 parser.

## Safety and authority

User messages are requirement candidates. Model outputs are proposals until verified. Twenty-nine high-risk messages are quarantined for medical execution/guarantees, financial guarantees, access-control bypass or possible credential exposure.

Health source material may contribute evidence-grading, contraindication, red-flag, monitoring and professional-escalation requirements. Experimental dosing, invasive procedures, guaranteed cures and frequency-as-drug-simulation claims remain disabled.

Apollo source material contributes compliant API/native-export, exact-filter preservation, partitioning, checkpoint, deduplication and audit requirements. Bypass and unlimited-scraping claims remain disabled.

## Truth boundary

The source denominator is complete for the three supplied files. That does not prove all historical ChatGPT/ChatHub sources are present, all source claims are true, providers are connected, the selector is wired into every live UI, or production is deployed.
