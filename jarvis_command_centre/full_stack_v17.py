from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from src.jarvis_evolution.panel_store_v1 import PanelRunStore

from . import integrated_v13 as base

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE = ROOT / "registry" / "architecture" / "jarvis_full_stack_18_layer_reference_v1.json"
STAGING = ROOT / "registry" / "staging" / "full_stack_local_staging_v17.json"

TRAFFIC_LIGHT = {
    "DONE_VERIFIED": {"colour": "GREEN", "icon": "🟢", "rank": 4},
    "INTEGRATED_STAGING": {"colour": "AMBER", "icon": "🟡", "rank": 3},
    "IMPLEMENTED_NOT_INTEGRATED": {"colour": "AMBER", "icon": "🟡", "rank": 2},
    "SCAFFOLDED": {"colour": "BLUE", "icon": "🔵", "rank": 1},
    "SPEC_ONLY": {"colour": "BLUE", "icon": "🔵", "rank": 1},
    "BACKLOGGED": {"colour": "GREY", "icon": "⚪", "rank": 0},
    "BLOCKED": {"colour": "RED", "icon": "🔴", "rank": -1},
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_full_stack_surface() -> dict[str, Any]:
    architecture = _load(ARCHITECTURE)
    staging = _load(STAGING) if STAGING.exists() else {"state": "NOT_RUN", "connected_external_staging": False}
    layers = []
    colour_counts: dict[str, int] = {}
    gap_count = 0
    for row in architecture["layers"]:
        light = TRAFFIC_LIGHT.get(row["state"], {"colour": "GREY", "icon": "⚪", "rank": 0})
        colour_counts[light["colour"]] = colour_counts.get(light["colour"], 0) + 1
        gaps = list(row.get("open_gaps") or [])
        gap_count += len(gaps)
        layers.append({
            "order": row["order"], "layer_id": row["layer_id"], "name": row["name"],
            "state": row["state"], "traffic_light": light, "open_gaps": gaps,
            "existing_evidence": row.get("existing_evidence") or [],
        })
    return {
        "component": "JARVIS_COMMAND_CENTRE_FULL_STACK_V17",
        "state": "INTEGRATED_STAGING",
        "declared_layer_count": len(layers),
        "minimum_requested_layers": architecture["minimum_required_layers"],
        "traffic_light_counts": colour_counts,
        "open_gap_count": gap_count,
        "layers": layers,
        "local_staging": staging,
        "connected_external_staging": bool(staging.get("connected_external_staging", False)),
        "production_authorised": False,
        "truth_boundary": "Traffic lights reflect repository evidence and local staging simulation only; they do not prove connected external staging or production.",
    }


def build_snapshot(live: bool = False, *, config: Any = None, store: PanelRunStore | None = None) -> dict[str, Any]:
    snapshot = base.build_snapshot(live=live, config=config, store=store)
    full_stack = build_full_stack_surface()
    snapshot["command_centre_version"] = "1.4.0"
    snapshot["full_stack_architecture"] = full_stack
    snapshot["summary"]["full_stack_layers"] = full_stack["declared_layer_count"]
    snapshot["summary"]["full_stack_open_gaps"] = full_stack["open_gap_count"]
    snapshot["summary"]["external_staging_connected"] = full_stack["connected_external_staging"]
    return snapshot


def _full_stack_panel(surface: dict[str, Any]) -> str:
    cards = []
    for layer in surface["layers"]:
        gaps = "".join(f"<li>{html.escape(gap)}</li>" for gap in layer["open_gaps"])
        cards.append(
            "<article class='stack-layer'>"
            f"<h3>{layer['traffic_light']['icon']} {layer['order']:02d}. {html.escape(layer['name'])}</h3>"
            f"<p><code>{html.escape(layer['state'])}</code></p><details><summary>{len(layer['open_gaps'])} gaps</summary><ul>{gaps}</ul></details>"
            "</article>"
        )
    return (
        "<div class='section-head'><h2>Jarvis 18-Layer Full Stack</h2><small>Traffic lights · evidence state · open gaps</small></div>"
        f"<section class='panel full-stack'><p>{surface['declared_layer_count']} layers · {surface['open_gap_count']} open gaps · "
        f"external staging <code>{str(surface['connected_external_staging']).lower()}</code></p>"
        f"<div class='stack-grid'>{''.join(cards)}</div></section>"
    )


def render_html(snapshot: dict[str, Any]) -> bytes:
    page = base.render_html(snapshot).decode("utf-8")
    css = (
        "<style>.stack-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}"
        ".stack-layer{border:1px solid #244b65;border-radius:14px;padding:12px;background:#071522}"
        ".stack-layer h3{font-size:1rem;margin:0 0 8px}.stack-layer details{margin-top:8px}"
        ".stack-layer li{margin:4px 0}.full-stack code{color:#44e5ff}</style>"
    )
    page = page.replace("</head>", css + "</head>", 1)
    panel = _full_stack_panel(snapshot["full_stack_architecture"])
    marker = "<div class='section-head'><h2>Universal Model Control</h2>"
    page = page.replace(marker, panel + marker, 1) if marker in page else page.replace("</main>", panel + "</main>", 1)
    return page.encode("utf-8")


def serve(host: str, port: int, live: bool, *, store_path: str = ":memory:") -> None:
    store = PanelRunStore(store_path)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            snapshot = build_snapshot(live=live, store=store)
            if self.path == "/api/v1/full-stack":
                content, media = json.dumps(snapshot["full_stack_architecture"], indent=2).encode(), "application/json"
            elif self.path == "/api/v1/command-centre":
                content, media = json.dumps(snapshot, indent=2).encode(), "application/json"
            elif self.path == "/health":
                content, media = b'{"status":"ok","version":"1.4.0"}', "application/json"
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
    parser = argparse.ArgumentParser(description="Jarvis Command Centre v1.4 full-stack surface")
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
