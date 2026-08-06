"""Validate the structure of a Conventional Commit message."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADER = re.compile(r"^(?P<type>[a-z][a-z0-9-]*)(?:\((?P<scope>[^()\r\n]+)\))?(?P<breaking>!)?: (?P<description>\S.*)$")


def validate(message: str) -> list[str]:
    errors: list[str] = []
    normalized = message.rstrip("\n")
    if not normalized:
        return ["commit message is empty"]
    lines = normalized.splitlines()
    match = HEADER.fullmatch(lines[0])
    if not match:
        errors.append("header must match <type>[optional scope][!]: <description>")
    else:
        if match.group("scope") and match.group("scope").strip() != match.group("scope"):
            errors.append("scope must not start or end with whitespace")
        if match.group("description").endswith("."):
            errors.append("description must not end with a period")
    if len(lines) > 1 and lines[1].strip():
        errors.append("body must be separated from the header by a blank line")
    for line in lines[2:]:
        if line.startswith("BREAKING-CHANGE:"):
            errors.append("use the exact footer token BREAKING CHANGE:")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--message")
    source.add_argument("--file", type=Path)
    args = parser.parse_args()

    if args.message is not None:
        message = args.message
    elif args.file is not None:
        message = args.file.read_text(encoding="utf-8")
    else:
        message = sys.stdin.read()

    errors = validate(message)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Valid Conventional Commit message")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
