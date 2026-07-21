"""Governed ChatHub and multi-LLM source intake for Jarvis."""
from .intake import ChatHubDetector, ChatHubImportRecord, MultiLLMConsolidator, RepositoryCapabilityRecord
from .intake_v2 import ChatHubTextParserV2, ChatMessage, build_applicability_matrix, build_source_manifest
from .intake_v3 import ChatHubTextParserV3, MessageRecord, build_applicability_register, build_source_accounting
__all__ = [
    "ChatHubDetector", "ChatHubImportRecord", "MultiLLMConsolidator",
    "RepositoryCapabilityRecord", "ChatHubTextParserV2", "ChatMessage",
    "build_applicability_matrix", "build_source_manifest", "ChatHubTextParserV3",
    "MessageRecord", "build_applicability_register", "build_source_accounting",
]
