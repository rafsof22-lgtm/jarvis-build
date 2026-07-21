from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from uuid import NAMESPACE_URL, uuid5


def stable_id(namespace: str, *parts: object) -> str:
    canonical = "|".join(str(part).strip().lower() for part in parts)
    return str(uuid5(NAMESPACE_URL, f"jarvis:{namespace}:{canonical}"))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ChatHubImportRecord:
    source_id: str
    filename: str
    sha256: str
    bytes: int
    source_class: str
    raw_text_preserved: bool
    interpretation_separate: bool
    subscription_route: str
    api_status: str
    connector_lineage: tuple[str, ...]
    models: tuple[str, ...]
    response_count: int
    status: str


@dataclass(frozen=True)
class RepositoryCapabilityRecord:
    repository: str
    reviewed_ref: str
    licence: str
    capability_class: str
    integration_state: str
    risk_state: str
    evidence_pointer: str
    notes: str = ""


class ChatHubDetector:
    """Detects ChatHub sources by filename and preserves exact bytes separately."""

    FILENAME_PATTERN = re.compile(r"chat\s*hub|chathub", re.IGNORECASE)

    @classmethod
    def is_chathub_filename(cls, filename: str) -> bool:
        return bool(cls.FILENAME_PATTERN.search(Path(filename).name))

    def ingest_file(self, source: str | Path, vault_dir: str | Path) -> ChatHubImportRecord:
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(path)
        if not self.is_chathub_filename(path.name):
            raise ValueError("filename does not identify a ChatHub upload")

        raw = path.read_bytes()
        digest = sha256_bytes(raw)
        vault = Path(vault_dir)
        vault.mkdir(parents=True, exist_ok=True)
        raw_path = vault / f"{digest}__{path.name}"
        if not raw_path.exists():
            raw_path.write_bytes(raw)
        elif raw_path.read_bytes() != raw:
            raise RuntimeError("immutable raw source collision")

        parsed = MultiLLMConsolidator().parse_bytes(raw, path.suffix.lower())
        return ChatHubImportRecord(
            source_id=stable_id("chathub-source", digest, path.name),
            filename=path.name,
            sha256=digest,
            bytes=len(raw),
            source_class="CHATHUB_MULTI_LLM_UPLOAD",
            raw_text_preserved=True,
            interpretation_separate=True,
            subscription_route="PAID_CHATHUB_FRONTEND_AND_EXPORT_ASSISTED_INTAKE",
            api_status="NO_SUPPORTED_SERVER_API_PROVEN",
            connector_lineage=("owner_upload", "raw_source_vault", "chathub_parser", "requirement_registry"),
            models=tuple(parsed["models"]),
            response_count=len(parsed["responses"]),
            status="READY",
        )

    @staticmethod
    def write_record(record: ChatHubImportRecord, output: str | Path) -> None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(record), indent=2, sort_keys=True), encoding="utf-8")


class MultiLLMConsolidator:
    """Extracts parallel model outputs without changing their wording."""

    def parse_bytes(self, raw: bytes, suffix: str = "") -> dict[str, Any]:
        text = raw.decode("utf-8", errors="strict")
        if suffix == ".json" or text.lstrip().startswith(("{", "[")):
            try:
                return self.parse_json(json.loads(text))
            except json.JSONDecodeError:
                pass
        return self.parse_text(text)

    def parse_json(self, payload: Any) -> dict[str, Any]:
        models: list[str] = []
        responses: list[dict[str, str]] = []
        conversations = payload if isinstance(payload, list) else payload.get("conversations", [payload])
        for conversation in conversations:
            if not isinstance(conversation, dict):
                continue
            declared_models = conversation.get("models", [])
            if isinstance(declared_models, list):
                models.extend(str(model) for model in declared_models if model)
            messages = conversation.get("messages") or conversation.get("chat_history") or []
            for message in messages:
                if not isinstance(message, dict):
                    continue
                parallel = message.get("responses")
                if isinstance(parallel, list):
                    for index, content in enumerate(parallel):
                        model = str(declared_models[index]) if index < len(declared_models) else f"model_{index + 1}"
                        responses.append({"model": model, "content": str(content)})
                        models.append(model)
                elif message.get("role") in {"assistant", "model"}:
                    model = str(message.get("model") or "unknown_model")
                    content = message.get("content", message.get("text", ""))
                    responses.append({"model": model, "content": str(content)})
                    models.append(model)
        return {"models": sorted(set(models)), "responses": responses, "preserved_verbatim": True}

    def parse_text(self, text: str) -> dict[str, Any]:
        responses: list[dict[str, str]] = []
        pattern = re.compile(r"(?im)^\s*(?:model|llm|assistant)\s*[:#-]\s*([^\n]+)\s*$")
        matches = list(pattern.finditer(text))
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            responses.append({"model": match.group(1).strip(), "content": text[start:end].lstrip("\r\n")})
        return {
            "models": sorted({response["model"] for response in responses}),
            "responses": responses,
            "preserved_verbatim": True,
            "unparsed_text": text if not responses else "",
        }

    def consolidate_manifest(self, parsed: dict[str, Any], source_pointer: str) -> dict[str, Any]:
        responses = parsed.get("responses", [])
        return {
            "manifest_id": stable_id("multi-llm-manifest", source_pointer, json.dumps(responses, sort_keys=True)),
            "source_pointer": source_pointer,
            "models": parsed.get("models", []),
            "responses": responses,
            "response_count": len(responses),
            "preservation_rule": "Original model responses remain word-for-word. Any synthesis is a separate derived artifact.",
            "synthesis_status": "PENDING_SEPARATE_DERIVATION",
        }


def write_capability_registry(records: Iterable[RepositoryCapabilityRecord], output: str | Path) -> dict[str, Any]:
    rows = [asdict(record) for record in records]
    result = {
        "schema_version": "1.0.0",
        "records": rows,
        "count": len(rows),
        "routing_rule": "Discover broadly; quarantine by default; integrate only after licence, security, duplicate, cost and staging gates.",
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
