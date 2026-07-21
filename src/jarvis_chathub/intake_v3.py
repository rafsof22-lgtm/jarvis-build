from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

ROLE_PATTERN = re.compile(r"(?m)^\*\*(user|system|cloud-[a-z0-9_.-]+|assistant|model)\*\*:\s?")
MODEL_ALIASES = {
    "cloud-mistral-large": "Mistral Large",
    "cloud-deepseek-v4": "DeepSeek V4",
    "cloud-tencent-hy3": "Tencent HY3",
    "cloud-qwen-3.8-max": "Qwen 3.8 Max",
    "cloud-pplx-sonar-online": "Perplexity Sonar",
    "cloud-kimi-k2.7-code": "Kimi K2.7 Code",
    "cloud-gpt-5-thinking": "GPT-5 Thinking",
}

DOMAIN_RULES = {
    "jarvis_control_plane": ("jarvis", "framework", "orchestrat", "agent", "skill", "workflow", "architecture"),
    "model_router": ("llm", "model", "chathub", "multi-model", "parallel", "consensus"),
    "health": ("health", "medical", "addiction", "spooky2", "frequency", "bioresonance", "treatment", "cure"),
    "apollo_property": ("apollo", "lead", "saved search", "people search", "csv", "export", "649,549", "650k"),
    "finance_trading": ("finance", "trading", "investment", "crypto", "stock", "cfo", "profit"),
    "legal_tax": ("legal", "lawyer", "barrister", "tax", "trust", "jurisdiction"),
    "digital_income": ("digital income", "passive income", "youtube", "affiliate", "saas"),
    "security_governance": ("security", "secret", "password", "approval", "audit", "compliance", "privacy"),
}

HIGH_RISK_PATTERNS = {
    "medical_execution_or_guarantee": re.compile(r"(?i)\b(inevitable cure|100% heal|cure.*inevitable|general anesthesia|ibogaine|crispr|deep brain stimulation|stem cell|exosome|ketamine.*mg|mdma.*mg|psilocybin.*mg)\b"),
    "financial_guarantee": re.compile(r"(?i)\b(guaranteed profit|99% profitable|guaranteed return|zero risk)\b"),
    "access_control_bypass": re.compile(r"(?i)\b(bypass (?:apollo|paywall|rate limit|export limit)|scrape unlimited|avoid.*platform limits)\b"),
    "credential_exposure": re.compile(r"(?i)\b(password|seed phrase|private key|api key)\s*[:=]\s*\S+"),
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


@dataclass(frozen=True)
class MessageRecord:
    ordinal: int
    role: str
    model: str | None
    start_line: int
    end_line: int
    word_count: int
    sha256: str
    exact_duplicate_of: int | None
    domains: tuple[str, ...]
    risk_flags: tuple[str, ...]
    disposition: str
    authority: str


class ChatHubTextParserV3:
    """Zero-loss role parser plus full-accounting applicability and safety disposition."""

    def parse(self, text: str) -> dict[str, Any]:
        matches = list(ROLE_PATTERN.finditer(text))
        records: list[MessageRecord] = []
        seen: dict[tuple[str, str], int] = {}
        for index, match in enumerate(matches, start=1):
            token = match.group(1)
            start = match.end()
            end = matches[index].start() if index < len(matches) else len(text)
            content = text[start:end]
            role = "user" if token == "user" else "system" if token == "system" else "assistant"
            model = MODEL_ALIASES.get(token, token) if role == "assistant" else None
            digest = sha256_bytes(content.encode("utf-8"))
            duplicate_key = (token, digest)
            duplicate_of = seen.get(duplicate_key)
            if duplicate_of is None:
                seen[duplicate_key] = index
            domains = self.classify_domains(content)
            risks = self.risk_flags(content)
            authority = "USER_REQUIREMENT" if role == "user" else "SYSTEM_SOURCE" if role == "system" else "ASSISTANT_PROPOSAL_NOT_APPROVED"
            if duplicate_of is not None:
                disposition = "DUPLICATE_WITH_LINEAGE"
            elif risks:
                disposition = "QUARANTINED_FOR_REVIEW"
            elif role == "user":
                disposition = "ROUTE_AS_REQUIREMENT_CANDIDATE"
            else:
                disposition = "REFERENCE_AND_DELTA_REVIEW"
            records.append(MessageRecord(
                ordinal=index,
                role=role,
                model=model,
                start_line=line_number(text, match.start()),
                end_line=line_number(text, end),
                word_count=word_count(content),
                sha256=digest,
                exact_duplicate_of=duplicate_of,
                domains=domains,
                risk_flags=risks,
                disposition=disposition,
                authority=authority,
            ))
        dispositions: dict[str, int] = {}
        for record in records:
            dispositions[record.disposition] = dispositions.get(record.disposition, 0) + 1
        return {
            "schema_version": "3.0.0",
            "message_count": len(records),
            "response_count": sum(r.role == "assistant" for r in records),
            "user_prompt_count": sum(r.role == "user" for r in records),
            "system_instruction_count": sum(r.role == "system" for r in records),
            "models": sorted({r.model for r in records if r.model}),
            "assistant_word_count": sum(r.word_count for r in records if r.role == "assistant"),
            "exact_duplicate_message_count": sum(r.exact_duplicate_of is not None for r in records),
            "disposition_counts": dispositions,
            "all_messages_accounted": sum(dispositions.values()) == len(records),
            "messages": [asdict(record) for record in records],
            "raw_content_storage": "EXTERNAL_IMMUTABLE_SOURCE_POINTER",
            "truth_boundary": "User messages are requirement candidates. Assistant messages remain proposals or source claims until separately verified and approved.",
        }

    @staticmethod
    def classify_domains(content: str) -> tuple[str, ...]:
        lowered = content.lower()
        matches = [domain for domain, terms in DOMAIN_RULES.items() if any(term in lowered for term in terms)]
        return tuple(matches or ["general_unclassified"])

    @staticmethod
    def risk_flags(content: str) -> tuple[str, ...]:
        return tuple(name for name, pattern in HIGH_RISK_PATTERNS.items() if pattern.search(content))


def build_source_accounting(paths: Iterable[str | Path], *, pointer_prefix: str) -> dict[str, Any]:
    files = []
    totals = {"bytes": 0, "lines": 0, "words": 0, "messages": 0, "responses": 0, "user_prompts": 0}
    for raw_path in paths:
        path = Path(raw_path)
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
        parsed = ChatHubTextParserV3().parse(text)
        entry = {
            "source_id": f"chathub-{sha256_bytes(raw)[:16]}",
            "filename": path.name,
            "pointer": f"{pointer_prefix}{path.name}",
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
            "lines": text.count("\n") + 1,
            "words": word_count(text),
            "status": "READY_EXTERNAL_RAW_POINTER",
            "parsed": parsed,
        }
        files.append(entry)
        totals["bytes"] += entry["bytes"]
        totals["lines"] += entry["lines"]
        totals["words"] += entry["words"]
        totals["messages"] += parsed["message_count"]
        totals["responses"] += parsed["response_count"]
        totals["user_prompts"] += parsed["user_prompt_count"]
    return {
        "schema_version": "3.0.0",
        "source_count": len(files),
        "totals": totals,
        "files": files,
        "all_files_hashed": all(bool(item["sha256"]) for item in files),
        "all_messages_accounted": all(item["parsed"]["all_messages_accounted"] for item in files),
        "raw_sources_committed": False,
        "reason": "Raw uploads may contain personal, health and third-party content. Immutable upload pointers and exact hashes preserve provenance while derived metadata is committed separately.",
    }


def build_applicability_register(accounting: dict[str, Any]) -> dict[str, Any]:
    routes: dict[str, dict[str, Any]] = {}
    quarantined = []
    for source in accounting["files"]:
        for message in source["parsed"]["messages"]:
            pointer = f"{source['pointer']}#L{message['start_line']}-L{message['end_line']}"
            for domain in message["domains"]:
                record = routes.setdefault(domain, {"message_count": 0, "user_requirement_candidates": 0, "assistant_proposals": 0, "pointers": []})
                record["message_count"] += 1
                record["user_requirement_candidates"] += int(message["authority"] == "USER_REQUIREMENT")
                record["assistant_proposals"] += int(message["authority"] == "ASSISTANT_PROPOSAL_NOT_APPROVED")
                record["pointers"].append(pointer)
            if message["risk_flags"]:
                quarantined.append({
                    "source": source["filename"],
                    "pointer": pointer,
                    "message_sha256": message["sha256"],
                    "risk_flags": message["risk_flags"],
                    "disposition": message["disposition"],
                })
    module_owner = {
        "jarvis_control_plane": "jarvis-build",
        "model_router": "jarvis-build",
        "health": "Jarvis-Health",
        "apollo_property": "property-agent-mcp",
        "finance_trading": "jarvis-build",
        "legal_tax": "jarvis-build",
        "digital_income": "jarvis-build",
        "security_governance": "jarvis-build",
        "general_unclassified": "jarvis-build",
    }
    return {
        "schema_version": "3.0.0",
        "source_manifest_sha256": sha256_bytes(json.dumps(accounting, sort_keys=True).encode("utf-8")),
        "routes": [
            {"module": domain, "owner_repository": module_owner[domain], **record, "state": "MAPPED_FOR_DELTA_REVIEW"}
            for domain, record in sorted(routes.items())
        ],
        "quarantined_claims": quarantined,
        "assistant_output_rule": "Assistant responses are preserved as proposals and never silently promoted to approved requirements or executable protocols.",
        "coverage_rule": "Every parsed message has a disposition and at least one module route or explicit general classification.",
    }
