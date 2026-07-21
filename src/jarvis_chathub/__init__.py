"""Governed ChatHub and multi-LLM source intake for Jarvis."""

from .intake import (
    ChatHubDetector,
    ChatHubImportRecord,
    MultiLLMConsolidator,
    RepositoryCapabilityRecord,
)
from .intake_v2 import (
    ChatHubTextParserV2,
    ChatMessage,
    build_applicability_matrix,
    build_source_manifest,
)

__all__ = [
    "ChatHubDetector",
    "ChatHubImportRecord",
    "MultiLLMConsolidator",
    "RepositoryCapabilityRecord",
    "ChatHubTextParserV2",
    "ChatMessage",
    "build_applicability_matrix",
    "build_source_manifest",
]
