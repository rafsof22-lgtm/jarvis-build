from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROLE_PATTERN = re.compile(r"(?m)^\*\*(user|system|cloud-[a-z0-9_.-]+|assistant|model)\*\*:\s?")
MODEL_ALIASES = {
    "cloud-mistral-large": "Mistral Large",
    "cloud-deepseek-v4": "DeepSeek V4",
    "cloud-tencent-hy3": "Tencent HY3",
    "cloud-qwen-3.8-max": "Qwen 3.8 Max",
    "cloud-pplx-sonar-online": "Perplexity Sonar",
    "cloud-kimi-k2.7-code": "Kimi K2.7 Code",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


@dataclass(frozen=True)
class ChatMessage:
    ordinal: int
    role: str
    model: str | None
    content: str
    start_line: int
    end_line: int
    word_count: int
    sha256: str
    exact_duplicate_of: int | None = None


class ChatHubTextParserV2:
    """Role-aware parser for ChatHub text exports.

    It preserves message bodies exactly as present between explicit role markers.
    It never treats ordinary headings as model boundaries.
    """

    def parse(self, text: str) -> dict[str, Any]:
        matches = list(ROLE_PATTERN.finditer(text))
        messages: list[ChatMessage] = []
        seen: dict[tuple[str, str], int] = {}
        for index, match in enumerate(matches, start=1):
            role_token = match.group(1)
            start = match.end()
            end = matches[index].start() if index < len(matches) else len(text)
            content = text[start:end]
            role = "user" if role_token == "user" else "system" if role_token == "system" else "assistant"
            model = None if role != "assistant" else MODEL_ALIASES.get(role_token, role_token)
            digest = sha256_bytes(content.encode("utf-8"))
            duplicate_key = (role_token, digest)
            duplicate_of = seen.get(duplicate_key)
            if duplicate_of is None:
                seen[duplicate_key] = index
            messages.append(
                ChatMessage(
                    ordinal=index,
                    role=role,
                    model=model,
                    content=content,
                    start_line=line_number(text, match.start()),
                    end_line=line_number(text, end),
                    word_count=word_count(content),
                    sha256=digest,
                    exact_duplicate_of=duplicate_of,
                )
            )
        models = sorted({m.model for m in messages if m.model})
        return {
            "schema_version": "2.0.0",
            "message_count": len(messages),
            "response_count": sum(m.role == "assistant" for m in messages),
            "user_prompt_count": sum(m.role == "user" for m in messages),
            "system_instruction_count": sum(m.role == "system" for m in messages),
            "models": models,
            "assistant_word_count": sum(m.word_count for m in messages if m.role == "assistant"),
            "exact_duplicate_message_count": sum(m.exact_duplicate_of is not None for m in messages),
            "messages": [asdict(m) for m in messages],
            "preservation_rule": "Content between explicit role markers is retained character-for-character.",
        }

    def parse_bytes(self, raw: bytes) -> dict[str, Any]:
        return self.parse(raw.decode("utf-8", errors="strict"))

    def reproduction_view(self, parsed: dict[str, Any], *, merge_exact_duplicates: bool = True) -> list[dict[str, Any]]:
        result = []
        for message in parsed["messages"]:
            if merge_exact_duplicates and message.get("exact_duplicate_of") is not None:
                continue
            result.append(message)
        return result


def build_source_manifest(path: str | Path, *, external_pointer: str) -> dict[str, Any]:
    source = Path(path)
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    parsed = ChatHubTextParserV2().parse(text)
    return {
        "schema_version": "2.0.0",
        "filename": source.name,
        "external_pointer": external_pointer,
        "sha256": sha256_bytes(raw),
        "bytes": len(raw),
        "lines": text.count("\n") + 1,
        "words": word_count(text),
        "status": "READY_EXTERNAL_RAW_POINTER",
        "raw_source_in_repository": False,
        "reason": "The immutable upload remains in the authorised ChatGPT file source; the repository stores its measured hash, coordinates and derived manifests without silently rewriting it.",
        "parsed_counts": {k: parsed[k] for k in ("message_count", "response_count", "user_prompt_count", "models", "assistant_word_count", "exact_duplicate_message_count")},
    }


def build_applicability_matrix(source_pointer: str) -> dict[str, Any]:
    routes = [
        ("control_plane", "jarvis-build", "orchestration, approvals, audit, continuity"),
        ("knowledge_fabric", "jarvis-build", "RAG, structured memory, provenance, source indexing"),
        ("model_router", "jarvis-build", "ChatHub panel intake, direct-provider routing, local/free-first models"),
        ("finance_cfo", "jarvis-build", "CFO analysis, valuation, risk-adjusted decision support"),
        ("trading_research", "jarvis-build", "backtests, paper trading, risk gates, kill switch"),
        ("legal_tax", "jarvis-build", "jurisdiction-tagged research and professional escalation"),
        ("health", "Jarvis-Health", "evidence grading, contraindications, practitioner escalation"),
        ("digital_income", "jarvis-build", "digital products, content workflows, measurable unit economics"),
        ("apollo_property", "property-agent-mcp", "lawful Apollo export, dedupe, privacy and outreach gates"),
        ("video_intelligence", "videotranscribe", "video/transcript source intake and evidence packs"),
        ("automation", "hub", "n8n/workflow integration, queues and adapters"),
        ("security_operations", "jarvis-build", "secrets, IAM, backup, restore, observability"),
        ("ux_command_centre", "jarvis-build", "plain-language status, approval packets and progress cards"),
        ("capability_scout", "jarvis-build", "GitHub/open-source discovery, licence/security quarantine"),
    ]
    return {
        "schema_version": "1.0.0",
        "source_pointer": source_pointer,
        "status": "ROUTED_NOT_FULLY_IMPLEMENTED",
        "routes": [
            {"module": module, "repository": repository, "applicable_scope": scope, "state": "MAPPED_FOR_DELTA_REVIEW"}
            for module, repository, scope in routes
        ],
        "non_duplication_rule": "Map requirements to existing owners; do not create a second competing framework when an owner already exists.",
        "truth_boundary": "Mapping proves applicability, not runtime completion. Each routed item still requires a delta, implementation, test and evidence chain.",
    }


def write_json(payload: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
