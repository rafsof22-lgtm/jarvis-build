from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .runtime import CatalogueStore, CostInput, DeploymentController, PricingEngine, SourceReconstructor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jarvis-business")
    commands = parser.add_subparsers(dest="command", required=True)

    reconstruct = commands.add_parser("reconstruct-sources")
    reconstruct.add_argument("paths", nargs="+")
    reconstruct.add_argument("--output", required=True)

    catalogue = commands.add_parser("import-catalogue")
    catalogue.add_argument("input")
    catalogue.add_argument("--output", required=True)

    price = commands.add_parser("price")
    price.add_argument("input")

    deploy = commands.add_parser("deployment-plan")
    deploy.add_argument("business_id")
    deploy.add_argument("environment", choices=("local", "staging", "production"))
    deploy.add_argument("--owner-approved", action="store_true")
    deploy.add_argument("--required-env", action="append", default=[])

    args = parser.parse_args(argv)
    if args.command == "reconstruct-sources":
        service = SourceReconstructor()
        result = service.write_manifest(service.inventory(args.paths), args.output)
    elif args.command == "import-catalogue":
        items, exceptions = CatalogueStore().import_file(args.input)
        result = {"records": [asdict(item) for item in items], "exceptions": exceptions}
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    elif args.command == "price":
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        costs = CostInput(**{**payload, **{key: Decimal(str(payload[key])) for key in PricingEngine.COMPONENTS}, "observed_at": datetime.fromisoformat(payload["observed_at"])})
        result = PricingEngine().quote(costs)
    else:
        result = DeploymentController().plan(args.business_id, args.environment, owner_approved=args.owner_approved, required_env=args.required_env)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
