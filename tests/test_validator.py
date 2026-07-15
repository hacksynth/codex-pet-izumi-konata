from __future__ import annotations

import json
from pathlib import Path

from codex_pet_validator.validator import (
    find_absolute_strings,
    validate_direction_semantics,
    validate_manifest,
    validate_repository,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_repository_passes() -> None:
    findings = validate_repository(repository_root())
    assert [item for item in findings if item.severity == "error"] == []


def test_manifest_rejects_inline_version(tmp_path: Path) -> None:
    manifest = {
        "id": "izumi-konata",
        "displayName": "泉此方",
        "description": "test",
        "spriteVersionNumber": 2,
        "spritesheetPath": "spritesheet.webp",
        "version": "1.0.0",
    }
    path = tmp_path / "pet.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    codes = {item.code for item in validate_manifest(path)}
    assert "manifest.version" in codes


def test_direction_semantics_require_evidence(tmp_path: Path) -> None:
    path = tmp_path / "direction-semantics.json"
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "directions": [
                    {
                        "direction": "000",
                        "expected": "up",
                        "observed": "up",
                        "verdict": "pass",
                        "horizontalEvidence": "",
                        "verticalEvidence": "high pupils",
                        "reason": "clear",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    codes = {item.code for item in validate_direction_semantics(path)}
    assert "directions.evidence" in codes
    assert "directions.order" in codes


def test_absolute_path_scanner_handles_windows_and_posix() -> None:
    value = {
        "portable": "spritesheet.webp",
        "windows": r"C:\Users\example\spritesheet.webp",
        "posix": "/tmp/spritesheet.webp",
    }
    assert find_absolute_strings(value) == ["$.windows", "$.posix"]
