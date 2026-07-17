from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
CONTRACT_VERSION = "1.0.0"


def _load(name: str) -> dict[str, Any]:
    with (REGISTRY / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _severity(status: str) -> str:
    return {
        "operational": "green", "proven": "green", "partial": "amber",
        "scaffold": "amber", "blocked": "red", "unknown": "grey",
        "retired": "grey",
    }.get(status, "grey")


def _poll(integration: dict[str, Any]) -> dict[str, Any] | None:
    env_name = integration.get("base_url_env")
    path = integration.get("capability_path") or integration.get("health_path")
    base = os.getenv(env_name or "") if env_name else None
    if not base or not path:
        return None
    token_name = (integration.get("secret_names") or [None])[0]
    token = os.getenv(token_name or "") if token_name else None
    headers = {"Accept": "application/json", "User-Agent": "Jarvis-Command-Centre/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    started = time.monotonic()
    try:
        with urlopen(Request(base.rstrip("/") + path, headers=headers), timeout=integration.get("timeout_seconds", 5)) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("contract_version") != CONTRACT_VERSION:
            raise ValueError("unsupported contract_version")
        payload["poll_latency_ms"] = round((time.monotonic() - started) * 1000)
        return payload
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        return {"contract_version": CONTRACT_VERSION, "health": {"status": "unknown", "readiness": "unknown", "latency_ms": None}, "blockers": [{"id": "poll-failed", "severity": "medium", "summary": str(exc)}]}


def build_snapshot(live: bool = False) -> dict[str, Any]:
    repositories = _load("repositories.json")["repositories"]
    integrations = _load("integrations.json")["integrations"]
    costs = _load("cost-credit-ledger.json")["accounts"]
    by_repo = {item["repository_id"]: item for item in repositories}
    live_contracts: dict[str, Any] = {}
    if live:
        for integration in integrations:
            result = _poll(integration)
            if result:
                live_contracts[integration["source_repository_id"]] = result

    cards = []
    for repo in repositories:
        contract = live_contracts.get(repo["repository_id"])
        status = repo["module_status"]
        health = (contract or {}).get("health", {}).get("status", "not-deployed" if not repo.get("contract_endpoint") else "unknown")
        blockers = list(repo.get("blockers", []))
        blockers.extend(item.get("summary", "") for item in (contract or {}).get("blockers", []) if item.get("summary"))
        cards.append({
            "repository_id": repo["repository_id"], "full_name": repo["full_name"],
            "role": repo["role"], "visibility": repo["visibility"], "status": status,
            "traffic_light": _severity(status), "health": health,
            "deployments": repo.get("deployment_ids", []), "blockers": blockers,
            "capabilities": [cap for integration in integrations if integration["source_repository_id"] == repo["repository_id"] for cap in integration.get("capabilities", [])],
        })

    known_balances = [x for x in costs if x["balance_status"] == "verified"]
    return {
        "command_centre_version": "1.0.0", "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "repositories": len(repositories), "green": sum(c["traffic_light"] == "green" for c in cards),
            "amber": sum(c["traffic_light"] == "amber" for c in cards), "red": sum(c["traffic_light"] == "red" for c in cards),
            "known_credit_balances": len(known_balances), "unknown_credit_balances": sum(x["balance_status"] == "unavailable" for x in costs),
            "open_blockers": sum(len(c["blockers"]) for c in cards),
        },
        "repositories": cards, "integrations": integrations, "cost_credit_ledger": costs,
    }


def _html(snapshot: dict[str, Any]) -> bytes:
    rows = "".join(f"<tr><td>{r['traffic_light']}</td><td>{r['full_name']}</td><td>{r['status']}</td><td>{r['health']}</td><td>{', '.join(r['deployments']) or 'none'}</td><td>{'<br>'.join(r['blockers']) or 'none'}</td></tr>" for r in snapshot["repositories"])
    body = f"""<!doctype html><meta charset='utf-8'><title>Jarvis Command Centre</title><style>body{{font-family:system-ui;margin:2rem}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:.5rem;text-align:left}}.meta{{margin-bottom:1rem}}</style><h1>Jarvis Command Centre v1</h1><div class='meta'>Generated {snapshot['generated_at']} | Repositories {snapshot['summary']['repositories']} | Blockers {snapshot['summary']['open_blockers']} | Unknown credit balances {snapshot['summary']['unknown_credit_balances']}</div><table><thead><tr><th>Light</th><th>Repository</th><th>Module status</th><th>Health</th><th>Deployments</th><th>Blockers</th></tr></thead><tbody>{rows}</tbody></table>"""
    return body.encode("utf-8")


def serve(host: str, port: int, live: bool) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            snapshot = build_snapshot(live=live)
            if self.path == "/api/v1/command-centre":
                content, media = json.dumps(snapshot, indent=2).encode(), "application/json"
            elif self.path == "/health":
                content, media = b'{"status":"ok","version":"1.0.0"}', "application/json"
            else:
                content, media = _html(snapshot), "text/html; charset=utf-8"
            self.send_response(200); self.send_header("Content-Type", media); self.send_header("Content-Length", str(len(content))); self.end_headers(); self.wfile.write(content)
        def log_message(self, *_: Any) -> None:
            return
    ThreadingHTTPServer((host, port), Handler).serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis five-repository command centre")
    parser.add_argument("--live", action="store_true", help="poll configured read-only federation endpoints")
    parser.add_argument("--serve", action="store_true", help="serve HTML and JSON API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.serve:
        serve(args.host, args.port, args.live)
        return
    rendered = json.dumps(build_snapshot(live=args.live), indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
