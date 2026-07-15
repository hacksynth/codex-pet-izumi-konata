from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .validator import Finding, validate_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a Codex v2 pet repository")
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def render_text(findings: Sequence[Finding]) -> str:
    if not findings:
        return "PASS: Codex v2 pet package and QA artifacts are valid."
    return "\n".join(f"{item.severity.upper()} {item.code}: {item.message}" for item in findings)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    findings = validate_repository(root)
    failed = any(item.severity == "error" for item in findings)

    if args.json_output:
        print(
            json.dumps(
                {
                    "ok": not failed,
                    "root": str(root),
                    "findings": [item.as_dict() for item in findings],
                },
                indent=2,
            )
        )
    else:
        print(render_text(findings))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
