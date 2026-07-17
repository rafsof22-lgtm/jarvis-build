# Jarvis Other-Agent Unification Workflow

## Purpose

Use this workflow to consolidate similar ChatGPT agents into Jarvis without losing unique instructions, skills, files, examples, app patterns, or source evidence.

Other agents should not be treated as automatically authoritative. Treat them as evidence to compare, extract, merge, or archive.

## Workflow

1. Intake the other agent evidence:
   - instructions
   - exported files
   - attached skills
   - starter prompts
   - app/tool setup
   - example outputs
   - known gaps and failures

2. Classify the agent:
   - duplicate of Jarvis core
   - partial overlap
   - domain module
   - superior specialized workflow
   - deprecated/obsolete
   - unrelated

3. Map capabilities to Jarvis modules:
   - module name
   - overlapping Jarvis module
   - unique logic
   - superior rules
   - contradictions
   - missing evidence

4. Decide placement:
   - merge into Jarvis instructions
   - move into an agent file
   - create/update a Jarvis skill
   - implement as runtime module
   - keep as domain-specific route-only skill
   - archive as evidence
   - discard after user approval

5. Update durable records:
   - JARVIS_MODULE_REGISTRY.md
   - JARVIS_SKILL_DEDUPE_MAP.md
   - JARVIS_MASTER_SPEC.md when standing requirements change
   - JARVIS_FORENSIC_TASK_MAP.md when gaps/blockers change

6. Validate:
   - no duplicate instruction conflict
   - no source authority regression
   - no unsupported app/tool promise
   - no lost unique rule
   - no accidental replacement of Jarvis core behavior

## Merge Decision Matrix

| Finding | Action |
|---|---|
| Other agent has better wording for existing Jarvis rule | Merge into relevant file/instruction section |
| Other agent has unique reusable workflow | Convert to skill or module |
| Other agent has project-specific content | Keep as route-only or reference file |
| Other agent contradicts Jarvis source hierarchy | Record contradiction and preserve higher authority |
| Other agent duplicates existing skill | Mark merge/archive candidate |
| Other agent requires unavailable app/tool | Record setup gap, do not promise capability |

## Completion Output

For each imported agent, produce:

- summary
- overlap map
- unique value
- merge recommendations
- conflicts
- missing evidence
- files/skills/modules to update
- next action

## Safety

Do not delete or detach skills without user approval. Do not import secrets. Do not trust unsupported claims from another agent without evidence.
