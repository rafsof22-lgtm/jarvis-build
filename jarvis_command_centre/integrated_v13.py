from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from jarvis_model_router import RouterConfig
from jarvis_model_router.selector import build_model_catalogue, selector_surface_contract
from src.jarvis_evolution.panel_store_v1 import PanelRunStore
from src.jarvis_evolution.surface_controls_v1 import build_all_surface_payloads

from . import command_centre as legacy


def build_model_control_snapshot(config: RouterConfig | None = None, *, store: PanelRunStore | None = None) -> dict[str, Any]:
    active = config or RouterConfig.from_env()
    catalogue = build_model_catalogue(active)
    if store is None:
        temporary = PanelRunStore()
        try:
            metrics = temporary.metrics()
        finally:
            temporary.close()
    else:
        metrics = store.metrics()
    surfaces = build_all_surface_payloads(catalogue, metrics=metrics)
    return {
        "component": "JARVIS_COMMAND_CENTRE_MODEL_CONTROL_V13",
        "status": "INTEGRATED_STAGING",
        "model_selector": selector_surface_contract(catalogue),
        "connected_model_count": len(catalogue.models),
        "unresolved_route_count": len(catalogue.routes_without_model_inventory),
        "parallel_button_state": "ENABLED" if catalogue.parallel_enabled else "BLOCKED_NEEDS_TWO_CONNECTED_MODELS",
        "panel_evidence": metrics,
        "selector_surfaces": surfaces,
        "provider_calls_executed": False,
        "provider_execution": "POLICY_BUDGET_PRIVACY_CREDENTIAL_GATED",
        "truth_boundary": "The snapshot reports configured model IDs and local panel evidence. It never calls a provider while rendering.",
    }


def build_snapshot(live: bool = False, *, config: RouterConfig | None = None, store: PanelRunStore | None = None) -> dict[str, Any]:
    snapshot = legacy.build_snapshot(live=live)
    models = build_model_control_snapshot(config, store=store)
    snapshot["command_centre_version"] = "1.3.0"
    snapshot["model_control"] = models
    snapshot["selector_surface_state"] = {
        "registered": len(models["selector_surfaces"]),
        "surfaces": list(models["selector_surfaces"]),
        "state": "INTEGRATED_STAGING",
    }
    snapshot["panel_evidence"] = models["panel_evidence"]
    snapshot["summary"]["connected_models"] = models["connected_model_count"]
    snapshot["summary"]["unresolved_model_routes"] = models["unresolved_route_count"]
    commands = snapshot.setdefault("global_jarvis", {}).setdefault("commands", [])
    if "parallel thinking" not in commands:
        commands.append("parallel thinking")
    snapshot["safety"].update({
        "provider_calls_during_snapshot": False,
        "parallel_execution_default": "DISABLED",
        "cloud_execution_requires_explicit_approval": True,
        "unknown_cloud_cost_allowed": False,
    })
    return snapshot


def _model_panel(snapshot: dict[str, Any]) -> str:
    control = snapshot["model_control"]
    options = control["model_selector"]["selector_options"]
    option_html = "".join(
        f"<option value='{html.escape(item['selector_id'])}'>{html.escape(item['provider'])} · {html.escape(item['model_id'])}</option>"
        for item in options
    ) or "<option disabled>No concrete configured model IDs detected</option>"
    disabled = "" if control["parallel_button_state"] == "ENABLED" else " disabled"
    return (
        "<div class='section-head'><h2>Universal Model Control</h2>"
        "<small>2–8 models · raw evidence · verified consolidation</small></div>"
        "<section class='panel model-control'><p>Select concrete configured models. Rendering this page never calls a provider.</p>"
        f"<select id='jarvis-models' multiple size='8'>{option_html}</select>"
        f"<button id='parallel-thinking'{disabled}>Parallel Thinking · Up to 8 LLMs</button>"
        f"<p><small>Panel evidence: {control['panel_evidence'].get('panel_runs', 0)} runs · "
        f"{control['panel_evidence'].get('responses_captured', 0)} preserved responses · "
        f"state <code>{html.escape(control['parallel_button_state'])}</code></small></p></section>"
    )


def render_html(snapshot: dict[str, Any]) -> bytes:
    base = legacy._html(snapshot).decode("utf-8")
    extra_css = (
        "<style>.model-control select{width:100%;min-height:180px;background:#06101d;color:#dff8ff;"
        "border:1px solid #34769a;border-radius:12px;padding:10px}.model-control button{margin-top:12px;width:100%;"
        "padding:13px;border-radius:999px;border:1px solid #44e5ff;background:#0b2942;color:#dff8ff;font-weight:700}"
        ".model-control button:disabled{opacity:.45}.model-control code{color:#44e5ff}</style>"
    )
    base = base.replace("</head>", extra_css + "</head>", 1)
    marker = "<div class='section-head'><h2>System Federation</h2>"
    panel = _model_panel(snapshot)
    if marker in base:
        base = base.replace(marker, panel + marker, 1)
    else:
        base = base.replace("</main>", panel + "</main>", 1)
    return base.encode("utf-8")


def serve(host: str, port: int, live: bool, *, store_path: str = ":memory:") -> None:
    store = PanelRunStore(store_path)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            snapshot = build_snapshot(live=live, store=store)
            if self.path == "/api/v1/command-centre":
                content, media = json.dumps(snapshot, indent=2).encode(), "application/json"
            elif self.path == "/api/v1/model-control":
                content, media = json.dumps(snapshot["model_control"], indent=2).encode(), "application/json"
            elif self.path == "/api/v1/editor-surfaces":
                content, media = json.dumps(snapshot["model_control"]["selector_surfaces"], indent=2).encode(), "application/json"
            elif self.path == "/api/v1/progress-tracker":
                path = legacy.REGISTRY / "trackers" / "all_progress_tracker_reconciliation_v3.json"
                content = path.read_bytes() if path.exists() else b'{"state":"PENDING_TRACKER"}'
                media = "application/json"
            elif self.path == "/health":
                content, media = b'{"status":"ok","version":"1.3.0"}', "application/json"
            else:
                content, media = render_html(snapshot), "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", media)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_: Any) -> None:
            return

    try:
        ThreadingHTTPServer((host, port), Handler).serve_forever()
    finally:
        store.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis integrated Command Centre v1.3")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--store", default=":memory:")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.serve:
        serve(args.host, args.port, args.live, store_path=args.store)
        return
    store = PanelRunStore(args.store)
    try:
        rendered = json.dumps(build_snapshot(live=args.live, store=store), indent=2)
    finally:
        store.close()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
