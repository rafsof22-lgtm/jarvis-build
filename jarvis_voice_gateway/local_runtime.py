"""Local/private speech-component selection for Jarvis.

This module validates reviewed component profiles and emits a deployment plan. It does
not open a microphone, download models, start processes or call cloud speech services.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SpeechComponent:
    component_id: str
    function: str
    runtime: str
    local_only: bool
    raw_audio_retention: bool
    approved: bool
    licence_reviewed: bool
    model_digest_recorded: bool

    def validate(self) -> None:
        if not self.approved or not self.licence_reviewed:
            raise ValueError(f"{self.component_id} is not approved for deployment planning")
        if not self.local_only or self.raw_audio_retention:
            raise ValueError(f"{self.component_id} violates local/private or retention policy")
        if self.function in {"wake_word", "speech_to_text", "text_to_speech"} and not self.model_digest_recorded:
            raise ValueError(f"{self.component_id} requires a reviewed model digest")


REVIEWED_LOCAL_STACK = (
    SpeechComponent("OPENWAKEWORD-REVIEWED-MODEL", "wake_word", "openWakeWord-compatible local runtime", True, False, True, True, True),
    SpeechComponent("SILERO-VAD", "voice_activity_detection", "local Python/ONNX runtime", True, False, True, True, True),
    SpeechComponent("WHISPERCPP-STT", "speech_to_text", "whisper.cpp", True, False, True, True, True),
    SpeechComponent("PIPER-TTS", "text_to_speech", "Piper local TTS", True, False, True, True, True),
    SpeechComponent("LOCAL-WEBSOCKET-TRANSPORT", "realtime_transport", "localhost-bound WebSocket", True, False, True, True, False),
)


def build_local_speech_plan() -> dict[str, object]:
    for component in REVIEWED_LOCAL_STACK:
        component.validate()
    return {
        "plan_id": "JARVIS-LOCAL-PRIVATE-SPEECH-V1",
        "state": "IMPLEMENTED_NOT_INTEGRATED",
        "components": [asdict(component) for component in REVIEWED_LOCAL_STACK],
        "microphone_access": False,
        "camera_access": False,
        "raw_audio_retention": False,
        "cloud_fallback_enabled": False,
        "voice_authorises_credentials": False,
        "voice_authorises_financial_actions": False,
        "voice_authorises_production": False,
        "stop_mute_barge_in_required": True,
        "runtime_gates": ["device microphone permission", "model binary and digest acquisition", "latency and false-wake evaluation", "speaker/replay threat review", "authenticated transport", "transient-audio purge proof", "owner approval before production activation"],
        "rollback": "Disable the voice feature flag, stop local speech processes, revoke microphone permission and return to text-only input.",
    }
