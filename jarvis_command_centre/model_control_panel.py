from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from jarvis_model_router import RouterConfig
from jarvis_model_router.selector import build_model_catalogue, selector_surface_contract


def build_model_control_snapshot(config: RouterConfig | None = None) -> dict[str, Any]:
    active = config or RouterConfig.from_env()
    catalogue = build_model_catalogue(active)
    contract = selector_surface_contract(catalogue)
    return {
        "component": "JARVIS_COMMAND_CENTRE_MODEL_CONTROL_V1",
        "status": "IMPLEMENTED_NOT_INTEGRATED",
        "model_selector": contract,
        "connected_model_count": len(catalogue.models),
        "parallel_button_state": "ENABLED" if catalogue.parallel_enabled else "BLOCKED_NEEDS_TWO_CONNECTED_MODELS",
        "provider_calls_executed": False,
        "safety": {
            "secret_values_exposed": False,
            "model_ids_only": True,
            "cost_preflight_required": True,
            "high_risk_qualified_review_required": True,
            "universal_zero_error_claim_allowed": False,
        },
    }


def render_model_control_html(snapshot: dict[str, Any]) -> str:
    options = snapshot["model_selector"]["selector_options"]
    option_html = "".join(
        f"<option value='{html.escape(item['selector_id'])}'>{html.escape(item['provider'])} · {html.escape(item['model_id'])}</option>"
        for item in options
    ) or "<option disabled>No concrete connected model IDs detected</option>"
    disabled = "" if snapshot["parallel_button_state"] == "ENABLED" else " disabled"
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Jarvis Model Control</title><style>
body{{font-family:system-ui;background:#040914;color:#dff8ff;margin:0;padding:24px}}main{{max-width:960px;margin:auto}}.panel{{border:1px solid #1d5575;border-radius:18px;padding:20px;background:#09182d}}select{{width:100%;min-height:240px;background:#06101d;color:#dff8ff;border:1px solid #34769a;border-radius:12px;padding:10px}}button{{margin-top:14px;width:100%;padding:14px;border-radius:999px;border:1px solid #44e5ff;background:#0b2942;color:#dff8ff;font-weight:700}}button:disabled{{opacity:.45}}small{{color:#8bb8ca}}code{{color:#44e5ff}}</style></head><body><main><h1>JARVIS UNIVERSAL MODEL SELECTOR</h1><section class='panel'><p>Select 2–8 concrete connected models. Every raw response is preserved before a separate consolidated response is created.</p><label for='models'>Connected models</label><select id='models' multiple size='8'>{option_html}</select><button id='parallel-thinking'{disabled}>Parallel Thinking · Up to 8 LLMs</button><p><small>State: <code>{html.escape(snapshot['parallel_button_state'])}</code>. This control does not call providers until policy, budget and approval preflight passes.</small></p></section></main></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    snapshot = build_model_control_snapshot()
    rendered = render_model_control_html(snapshot) if args.html else json.dumps(snapshot, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
