from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .previews import check_previews, generate_previews


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic Codex pet GIF previews")
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check", action="store_true", help="Fail when committed previews are stale"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if args.check:
        failures = check_previews(root)
        if failures:
            for failure in failures:
                print(f"ERROR: {failure}")
            return 1
        print("PASS: committed GIF previews match spritesheet.webp and the preview contract.")
        return 0

    manifest = generate_previews(root)
    print(json.dumps({"ok": True, "output": str(root / "previews"), **manifest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
