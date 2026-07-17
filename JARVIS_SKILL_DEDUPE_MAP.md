# Jarvis Skill Dedupe Map

## Purpose

This file controls how Jarvis handles overlapping skills. It prevents startup bloat, duplicate routing, contradictory workflows, and accidental removal of useful project-specific skills.

Do not detach or replace skills until their actual contents have been inspected or the user explicitly approves removal.

## Dedupe Rules

- Prefer one lead skill path per task.
- Keep broad Jarvis core skills active, but route narrowly.
- Treat domain-specific skills as route-only unless they directly support Jarvis core build work.
- Merge overlapping instructions into durable files or uploaded Builder skills only after inspection.
- Archive before delete when uncertain.
- Do not remove project-specific skills just because they are not part of the Jarvis core.

## Classification Legend

- `core keep` — keep attached and route explicitly
- `merge candidate` — likely overlaps with another skill; inspect before consolidation
- `route-only` — keep but use only for matching domain tasks
- `defer` — do not prioritize now
- `remove candidate` — likely safe to detach after user approval
- `inspect required` — content must be read before decision

## Current Skill Classification

| Skill | Classification | Reason | Proposed Action |
|---|---|---|---|
| jarvis-session-orchestrator | core keep | Baseline selection and startup narrowing | Keep; use as brief preflight only |
| jarvis-build-orchestrator | core keep | Main Jarvis continuation/build workflow | Keep as primary build path |
| jarvis-verification-discrepancy | core keep | Proof, discrepancy, no-gap audits | Keep as verification path |
| jarvis-research-sourcing | core keep | Free/cheap/current sourcing | Keep as research path |
| jarvis-sovereign-builder | core keep | Full Jarvis sovereign build scope | Keep; route for large build/deploy work |
| universal-agent-autopilot-orchestrator | core keep | Cross-agent automation and minimal-human routing | Keep; avoid using alongside too many other skills |
| project-stack-access-mapper | core keep | Apps, APIs, credentials, access maps | Keep; route for app/deploy/secret planning |
| universal-sourcing-stack-scout | core keep | Cost and provider sourcing | Keep; route for sourcing/cost tasks |
| source-first-project-continuity | core keep | Source-first continuity and project preservation | Keep; route for source/archive work |
| skill-orchestrator-router | core keep | Skill routing and cleanup | Keep; route for skill work |
| jarvis-reconstruction | merge candidate | Overlaps with Jarvis build/reconstruction workflows | Inspect before merge/archive |
| apex-project-reconstruction-blueprint | merge candidate | Overlaps with source-first reconstruction and framework-building | Inspect before merge/archive |
| source-first-agent-framework-builder | merge candidate | Overlaps with Jarvis framework/build routing | Inspect before merge/archive |
| project-orchestrator-continuity | merge candidate | Overlaps with continuity/router skills | Inspect before merge/archive |
| master-chatgpt-kb | merge candidate | Overlaps with export/source hub workflows | Inspect before merge/archive |
| omni-project-memory-orchestrator | merge candidate | Overlaps with project memory/export continuity | Inspect before merge/archive |
| jason-sync | merge candidate | Overlaps with ChatGPT export and map sync | Inspect; keep if it has unique export parsing rules |
| github-railway-deploy-controller | route-only | Useful for Railway/GitHub deploys, but Jarvis default is GitHub + Oracle/cheap VPS | Keep route-only unless Railway is chosen |
| trading-bot-apex-orchestrator | route-only | Trading/market domain skill | Keep for trading modules only |
| undervalued-asset-scout | merge candidate | Overlaps with v2 asset scout | Inspect and keep best version |
| undervalued-asset-scout-v2 | route-only | Likely newer market research skill | Keep route-only pending comparison |
| xrp-hbar-apex-tracker | merge candidate | Duplicate skill name exists | Inspect both versions and keep/route one canonical version |
| xrp-hbar-apex-tracker duplicate | merge candidate | Duplicate skill name exists | Inspect before detach |
| pc-build-workstation-planner | merge candidate | Overlaps with agent-workstation-planner | Inspect and keep best/canonical version |
| agent-workstation-planner | route-only | Useful for hardware/local model planning | Keep route-only pending merge |
| universal-intelligence-gatherer | route-only | Broad research/intelligence route | Keep, but avoid duplicate use with research-sourcing unless needed |
| email-intelligence-orchestrator | route-only | Gmail/mailbox intelligence | Keep for mailbox modules |
| request-construction-planner | route-only | Improves complex request framing | Keep optional; avoid heavy use for simple commands |
| bill-cfo-ocr-source-intake | route-only | Finance/OCR/source intake domain | Keep for finance/tax/OCR tasks |
| cfo-audit-controller | route-only | Finance audit domain | Keep for CFO/tax tasks |
| vti-video-intelligence-builder | route-only | Video/social intelligence module | Keep for video intelligence tasks |
| landtax-source-first-victoria | route-only | Legal/property domain | Keep for Victorian land tax work |
| dream-home-estate-planner | route-only | Dream home/estate project domain | Keep only for that domain |
| ultimate-au-wiper-product-sourcing | route-only | Wiper product sourcing domain | Keep for sourcing project only |
| gemantria-cross-system-orchestrator | route-only | Symbolic/spiritual framework domain | Keep for that domain only |
| skill-creator | core utility | Needed when creating/updating skills | Keep as utility |
| example-skill | remove candidate | Test/demo skill, not useful to Jarvis | Remove after user approval |

## Immediate Dedupe Actions

1. Read actual contents of all merge candidates before detaching anything.
2. Pick one canonical XRP/HBAR tracker.
3. Pick one canonical PC/workstation planner.
4. Merge generic reconstruction/export-map logic into the Jarvis core files or one canonical skill.
5. Detach only after user approval and only after confirming no unique rules would be lost.

## Update Log

- Initial dedupe map created from current attached skill inventory and setup gap audit.
