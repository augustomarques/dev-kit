"""Check that the current machine can run Dev Kit."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parents[3]


def run_version(command: str) -> tuple[bool, str]:
    executable = shutil.which(command)
    if executable is None:
        return False, f"{command} is not on PATH"
    result = subprocess.run([command, "--version"], check=False, text=True, capture_output=True)
    detail = (result.stdout or result.stderr).strip().splitlines()
    if result.returncode != 0:
        return False, detail[0] if detail else f"{command} --version failed"
    return True, detail[0] if detail else executable


def gh_authenticated() -> tuple[bool, str]:
    if shutil.which("gh") is None:
        return False, "gh is not on PATH"
    result = subprocess.run(["gh", "auth", "status"], check=False, text=True, capture_output=True)
    detail = (result.stderr or result.stdout).strip().splitlines()
    message = detail[0] if detail else "gh auth status failed"
    return result.returncode == 0, message


def python_supported(version: tuple[int, int, int] | None = None) -> tuple[bool, str]:
    info = version or sys.version_info[:3]
    label = f"Python {info[0]}.{info[1]}.{info[2]}"
    if info < (3, 10):
        return False, f"{label} is older than 3.10"
    return True, label


def plugin_files_present() -> tuple[bool, str]:
    required = [
        PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
        PLUGIN_ROOT / "skills" / "dev-kit-to-issues" / "SKILL.md",
        PLUGIN_ROOT / "skills" / "dev-kit-grill-me" / "SKILL.md",
        PLUGIN_ROOT / "skills" / "dev-kit-github" / "SKILL.md",
        PLUGIN_ROOT / "skills" / "dev-kit-develop" / "SKILL.md",
        PLUGIN_ROOT / "skills" / "dev-kit-git" / "SKILL.md",
        PLUGIN_ROOT / "skills" / "dev-kit" / "SKILL.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        return False, "missing plugin files: " + ", ".join(missing)
    return True, str(PLUGIN_ROOT)


def collect_report() -> dict[str, Any]:
    checks = {
        "python": python_supported(sys.version_info[:3]),
        "git": run_version("git"),
        "gh": run_version("gh"),
        "gh_auth": gh_authenticated(),
        "plugin_files": plugin_files_present(),
        "codex": run_version("codex"),
    }
    required = ("python", "git", "gh", "gh_auth", "plugin_files")
    failures = {name: detail for name, (ok, detail) in checks.items() if name in required and not ok}
    warnings = {name: detail for name, (ok, detail) in checks.items() if name not in required and not ok}
    return {
        "status": "PASS" if not failures else "FAIL",
        "checks": {name: {"ok": ok, "detail": detail} for name, (ok, detail) in checks.items()},
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    report = collect_report()
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{report['status']}: Dev Kit setup")
        for name, check in report["checks"].items():
            mark = "ok" if check["ok"] else "missing"
            print(f"- {name}: {mark} ({check['detail']})")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
