"""Deterministic selection for approved self-hosted models.

This module does not download, install, load or execute a model. It selects from a
caller-supplied registry of already reviewed model profiles and an explicit host
capacity record. Unknown parameter counts remain unknown rather than inferred.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Iterable


LOCAL_RUNTIMES = {"ollama", "llama.cpp", "vllm"}
LOCAL_SELECTION_MODES = {
    "highest_parameter_local",
    "fast_local",
    "lowest_restriction",
    "local_sovereign",
    "offline_private",
    "free_first",
}


@dataclass(frozen=True)
class HostCapacity:
    """Explicit capacity available to an approved local-model runtime."""

    ram_gb: float
    vram_gb: float = 0.0
    maximum_context_tokens: int = 0

    @classmethod
    def from_env(cls) -> "HostCapacity":
        return cls(
            ram_gb=max(0.0, float(os.getenv("JARVIS_LOCAL_RAM_GB", "0"))),
            vram_gb=max(0.0, float(os.getenv("JARVIS_LOCAL_VRAM_GB", "0"))),
            maximum_context_tokens=max(0, int(os.getenv("JARVIS_LOCAL_MAX_CONTEXT", "0"))),
        )

    @property
    def total_memory_gb(self) -> float:
        return self.ram_gb + self.vram_gb


@dataclass(frozen=True)
class LocalModelProfile:
    """Version-specific metadata for one reviewed self-hosted model artifact."""

    model_id: str
    runtime: str
    approved: bool
    licence: str
    source: str
    reviewed_digest: str | None
    estimated_memory_gb: float
    context_tokens: int
    capabilities: frozenset[str] = field(default_factory=frozenset)
    total_parameters: int | None = None
    active_parameters: int | None = None
    quality_score: float = 0.0
    speed_score: float = 0.0
    restriction_score: float = 0.0

    def fits(self, capacity: HostCapacity, required_context: int = 0) -> bool:
        if self.runtime not in LOCAL_RUNTIMES or not self.approved:
            return False
        if self.estimated_memory_gb > capacity.total_memory_gb:
            return False
        if required_context and self.context_tokens < required_context:
            return False
        if capacity.maximum_context_tokens and required_context > capacity.maximum_context_tokens:
            return False
        return True


@dataclass(frozen=True)
class LocalModelDecision:
    model_id: str
    runtime: str
    mode: str
    reason: str
    total_parameters: int | None
    active_parameters: int | None
    estimated_memory_gb: float
    context_tokens: int


def select_local_model(
    profiles: Iterable[LocalModelProfile],
    capacity: HostCapacity,
    *,
    mode: str = "highest_parameter_local",
    required_capabilities: Iterable[str] = (),
    required_context: int = 0,
) -> LocalModelDecision:
    """Select one already approved model without downloading or executing it."""

    normalized_mode = mode.strip().lower()
    if normalized_mode not in LOCAL_SELECTION_MODES:
        raise ValueError(f"Unsupported local selection mode: {mode}")

    required = frozenset(required_capabilities)
    candidates = [
        profile
        for profile in profiles
        if profile.fits(capacity, required_context)
        and required.issubset(profile.capabilities)
    ]
    if not candidates:
        raise RuntimeError("No approved local model fits the declared host capacity and task requirements.")

    if normalized_mode == "highest_parameter_local":
        selected = max(
            candidates,
            key=lambda item: (
                item.total_parameters if item.total_parameters is not None else -1,
                item.active_parameters if item.active_parameters is not None else -1,
                item.quality_score,
                -item.estimated_memory_gb,
            ),
        )
        reason = "Largest officially recorded approved model that fits declared memory, context and capability requirements."
    elif normalized_mode == "fast_local":
        selected = max(candidates, key=lambda item: (item.speed_score, item.quality_score, -item.estimated_memory_gb))
        reason = "Fastest approved local model that satisfies the task requirements."
    elif normalized_mode == "lowest_restriction":
        selected = max(candidates, key=lambda item: (item.restriction_score, item.quality_score, item.total_parameters or -1))
        reason = "Least unnecessarily restrictive approved local model; Jarvis safety and approval controls remain active."
    else:
        selected = max(candidates, key=lambda item: (item.quality_score, item.speed_score, -item.estimated_memory_gb))
        reason = "Best evaluated approved local model for sovereign, offline or free-first execution."

    return LocalModelDecision(
        model_id=selected.model_id,
        runtime=selected.runtime,
        mode=normalized_mode,
        reason=reason,
        total_parameters=selected.total_parameters,
        active_parameters=selected.active_parameters,
        estimated_memory_gb=selected.estimated_memory_gb,
        context_tokens=selected.context_tokens,
    )
