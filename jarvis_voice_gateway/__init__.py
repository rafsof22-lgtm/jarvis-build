"""Jarvis voice-command policy and deterministic risk routing.

The package processes text transcripts only. It does not access a microphone, camera,
operating-system permissions, external provider or production action surface.
"""

from .policy import VoiceGatewayPolicy
from .router import VoiceCommandDecision, classify_voice_command, redact_sensitive_text

__all__ = [
    "VoiceCommandDecision",
    "VoiceGatewayPolicy",
    "classify_voice_command",
    "redact_sensitive_text",
]
