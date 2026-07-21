from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "intelligence"
ASSET_DIR = REGISTRY / "assets"
ORCHESTRATOR_PATH = REGISTRY / "multi_asset_intelligence_orchestrator_v1.json"


@dataclass(frozen=True)
class AssetScanTask:
    profile_id: str
    asset: str
    asset_class: str
    source_budget_mode: str
    source_budget_minimum: int
    source_budget_maximum: int
    milestone_count: int
    dynamic_ceiling_enabled: bool
    source_families: tuple[str, ...]
    intelligence_layers: tuple[str, ...]
    workstreams: tuple[str, ...]
    knowledge_namespace: str
    execution_boundary: str


@dataclass(frozen=True)
class IntelligenceRunPlan:
    plan_version: str
    generated_at: str
    trigger: str
    requested_assets: tuple[str, ...]
    fan_out_mode: str
    simultaneous: bool
    source_budget_mode: str
    maximum_sources_per_asset: int
    tasks: tuple[AssetScanTask, ...]
    cross_asset_workstreams: tuple[str, ...]
    knowledge_fabric_export: dict[str, Any]
    truth_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AssetIntelligenceOrchestrator:
    """Load governed profiles and create non-executing, evidence-aware scan plans."""

    def __init__(self, registry_root: Path = REGISTRY) -> None:
        self.registry_root = registry_root
        self.asset_dir = registry_root / "assets"
        self.contract = self._load(registry_root / "multi_asset_intelligence_orchestrator_v1.json")
        self.profiles = self._load_profiles()

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_profiles(self) -> dict[str, dict[str, Any]]:
        profiles: dict[str, dict[str, Any]] = {}
        if not self.asset_dir.exists():
            return profiles
        for path in sorted(self.asset_dir.glob("*_asset_intelligence_v1.json")):
            profile = self._load(path)
            profiles[str(profile["primary_asset"]).upper()] = profile
        return profiles

    def active_assets(self) -> tuple[str, ...]:
        return tuple(sorted(self.profiles))

    def resolve_trigger(self, command: str) -> str:
        normalized = " ".join(command.strip().lower().replace("_", " ").split())
        aliases = self.contract["trigger_aliases"]
        matches: list[tuple[int, str]] = []
        for canonical, values in aliases.items():
            for value in (canonical, *values):
                candidate = " ".join(str(value).lower().replace("_", " ").split())
                if candidate and candidate in normalized:
                    matches.append((len(candidate), canonical))
        if not matches:
            return "UPDATE"
        return max(matches)[1]

    def resolve_assets(self, command: str, requested_assets: Iterable[str] | None = None) -> tuple[str, ...]:
        if requested_assets:
            selected = tuple(dict.fromkeys(str(asset).upper() for asset in requested_assets))
        else:
            text = command.upper()
            selected = tuple(asset for asset in self.active_assets() if asset in text)
        if selected:
            unknown = [asset for asset in selected if asset not in self.profiles]
            if unknown:
                raise ValueError(f"Inactive or unknown asset profiles: {', '.join(unknown)}")
            return selected
        return self.active_assets()

    def build_plan(self, command: str, requested_assets: Iterable[str] | None = None) -> IntelligenceRunPlan:
        trigger = self.resolve_trigger(command)
        selected_assets = self.resolve_assets(command, requested_assets)
        trigger_config = self.contract["trigger_execution"][trigger]
        source_mode = trigger_config["source_budget_mode"]
        source_budget = self.contract["source_budget_policy"][source_mode]
        maximum_sources = int(trigger_config.get("maximum_sources_per_asset_per_run", source_budget["maximum"]))
        tasks = tuple(
            self._build_asset_task(
                asset,
                source_mode=source_mode,
                source_minimum=int(source_budget["minimum"]),
                source_maximum=min(maximum_sources, int(source_budget["maximum"])),
                workstreams=tuple(trigger_config["simultaneous_workstreams"]),
            )
            for asset in selected_assets
        )
        return IntelligenceRunPlan(
            plan_version=self.contract["version"],
            generated_at=datetime.now(timezone.utc).isoformat(),
            trigger=trigger,
            requested_assets=selected_assets,
            fan_out_mode=str(trigger_config["fan_out"]),
            simultaneous=bool(trigger_config.get("run_independent_asset_workstreams_in_parallel", len(tasks) > 1)),
            source_budget_mode=source_mode,
            maximum_sources_per_asset=maximum_sources,
            tasks=tasks,
            cross_asset_workstreams=tuple(self.contract["required_output_layers"]),
            knowledge_fabric_export=self.contract["knowledge_fabric_export"],
            truth_boundary=(
                "PLAN_ONLY: source discovery, browsing, model calls, current-market verification and recommendations "
                "must be executed separately with evidence. Financial execution remains disabled."
            ),
        )

    def _build_asset_task(
        self,
        asset: str,
        *,
        source_mode: str,
        source_minimum: int,
        source_maximum: int,
        workstreams: tuple[str, ...],
    ) -> AssetScanTask:
        profile = self.profiles[asset]
        layers = profile.get("xrp_specific_intelligence_layers") or profile.get("hbar_specific_intelligence_layers") or profile.get("asset_specific_intelligence_layers", [])
        return AssetScanTask(
            profile_id=str(profile["profile_id"]),
            asset=asset,
            asset_class=str(profile["asset_class"]),
            source_budget_mode=source_mode,
            source_budget_minimum=source_minimum,
            source_budget_maximum=source_maximum,
            milestone_count=len(profile.get("fixed_milestones", [])),
            dynamic_ceiling_enabled=bool(profile.get("dynamic_milestones", {}).get("enabled")),
            source_families=tuple(profile.get("priority_source_families", [])),
            intelligence_layers=tuple(layers),
            workstreams=workstreams,
            knowledge_namespace=str(profile["knowledge_fabric_namespace"]),
            execution_boundary=str(profile["execution_boundary"]),
        )


def build_plan(command: str, requested_assets: Iterable[str] | None = None) -> dict[str, Any]:
    return AssetIntelligenceOrchestrator().build_plan(command, requested_assets).to_dict()
