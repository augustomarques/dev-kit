"""Validate a Dev Kit task bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tasklib import load_bundle, validate_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        bundle = load_bundle(args.bundle)
        errors, warnings = validate_bundle(bundle)
    except (TypeError, ValueError) as exc:
        errors, warnings = [str(exc)], []

    if args.format == "json":
        print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if not errors:
            print(f"Valid task bundle: {args.bundle}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
