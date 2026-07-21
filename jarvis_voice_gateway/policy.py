"""Default-deny policy for the Jarvis voice-command gateway."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceGatewayPolicy:
    """Voice controls that remain independent from speech-recognition providers."""

    wake_word_local_only: bool = True
    push_to_talk_supported: bool = True
    visible_recording_indicator: bool = True
    hardware_or_ui_mute_supported: bool = True
    barge_in_supported: bool = True
    emergency_stop_phrase: str = "stop jarvis"
    lock_screen_commands_enabled: bool = False
    raw_audio_retention: bool = False
    transcript_retention: bool = False
    speaker_verification_is_sole_auth: bool = False
    exact_readback_for_consequential_actions: bool = True
    replay_protection_required: bool = True
    microphone_permission_default: bool = False
    camera_permission_default: bool = False
    clipboard_permission_default: bool = False
    production_actions_from_voice: bool = False
    financial_actions_from_voice: bool = False
    clinical_device_actions_from_voice: bool = False

    def validate(self) -> None:
        if not self.visible_recording_indicator:
            raise ValueError("Voice capture requires a visible recording indicator.")
        if self.speaker_verification_is_sole_auth:
            raise ValueError("Speaker verification cannot be the sole authentication control.")
        if self.production_actions_from_voice:
            raise ValueError("Production actions cannot be authorised by voice alone.")
        if self.financial_actions_from_voice:
            raise ValueError("Financial actions cannot be authorised by voice alone.")
        if self.clinical_device_actions_from_voice:
            raise ValueError("Clinical or wellness-device actions cannot be authorised by voice.")
