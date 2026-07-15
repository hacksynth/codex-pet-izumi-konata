from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal, cast

from PIL import Image

from .previews import check_previews

Severity = Literal["error", "warning"]
JsonObject = dict[str, object]

ATLAS_SIZE = (1536, 2288)
CELL_SIZE = (192, 208)
EXPECTED_DIRECTIONS = [
    "000",
    "022.5",
    "045",
    "067.5",
    "090",
    "112.5",
    "135",
    "157.5",
    "180",
    "202.5",
    "225",
    "247.5",
    "270",
    "292.5",
    "315",
    "337.5",
]
USED_COLUMNS = {
    0: set(range(7)),  # six idle frames plus the dedicated neutral cell
    1: set(range(8)),
    2: set(range(8)),
    3: set(range(4)),
    4: set(range(5)),
    5: set(range(8)),
    6: set(range(6)),
    7: set(range(6)),
    8: set(range(6)),
    9: set(range(8)),
    10: set(range(8)),
}


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def error(code: str, message: str) -> Finding:
    return Finding("error", code, message)


def warning(code: str, message: str) -> Finding:
    return Finding("warning", code, message)


def load_json(path: Path) -> tuple[JsonObject | None, list[Finding]]:
    if not path.is_file():
        return None, [error("file.missing", f"Required file is missing: {path.name}")]
    try:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [error("json.invalid", f"Cannot read {path.name}: {exc}")]
    if not isinstance(raw, dict):
        return None, [error("json.shape", f"{path.name} must contain a JSON object")]
    return cast(JsonObject, raw), []


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def portable_path(value: str) -> bool:
    return not PurePosixPath(value).is_absolute() and not PureWindowsPath(value).is_absolute()


def validate_manifest(path: Path) -> list[Finding]:
    data, findings = load_json(path)
    if data is None:
        return findings

    required: dict[str, object] = {
        "id": "izumi-konata",
        "displayName": "泉此方",
        "spriteVersionNumber": 2,
        "spritesheetPath": "spritesheet.webp",
    }
    for key, expected in required.items():
        if data.get(key) != expected:
            findings.append(
                error("manifest.value", f"pet.json {key!r} must equal {expected!r}")
            )
    if not nonempty_string(data.get("description")):
        findings.append(error("manifest.description", "pet.json description must be non-empty"))
    if "version" in data:
        findings.append(
            error("manifest.version", "Pet versions come from Git tags; remove pet.json version")
        )

    pet_id = data.get("id")
    if isinstance(pet_id, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", pet_id) is None:
        findings.append(error("manifest.id", "pet.json id is not a stable lowercase slug"))
    sheet_path = data.get("spritesheetPath")
    if isinstance(sheet_path, str) and Path(sheet_path).name != sheet_path:
        findings.append(
            error("manifest.path", "spritesheetPath must be a repository-local filename")
        )
    return findings


def transparent_rgb_residue(rgba: Image.Image) -> int:
    raw = rgba.tobytes()
    return sum(
        1
        for offset in range(0, len(raw), 4)
        if raw[offset + 3] == 0 and any(raw[offset : offset + 3])
    )


def validate_spritesheet(path: Path) -> list[Finding]:
    if not path.is_file():
        return [error("file.missing", "Required file is missing: spritesheet.webp")]

    findings: list[Finding] = []
    try:
        with Image.open(path) as source:
            source.load()
            if source.format != "WEBP":
                findings.append(error("atlas.format", "spritesheet.webp must be WebP"))
            if source.size != ATLAS_SIZE:
                findings.append(
                    error("atlas.size", f"Atlas must be {ATLAS_SIZE[0]}x{ATLAS_SIZE[1]}")
                )
            if source.mode != "RGBA":
                findings.append(error("atlas.mode", "Atlas must decode as RGBA"))
            rgba = source.convert("RGBA")
    except (OSError, ValueError) as exc:
        return [error("atlas.invalid", f"Cannot decode spritesheet.webp: {exc}")]

    if rgba.size != ATLAS_SIZE:
        return findings

    residue = transparent_rgb_residue(rgba)
    if residue:
        findings.append(
            error("atlas.transparent-rgb", f"Found {residue} RGB-bearing zero-alpha pixels")
        )

    cell_width, cell_height = CELL_SIZE
    for row in range(11):
        for column in range(8):
            box = (
                column * cell_width,
                row * cell_height,
                (column + 1) * cell_width,
                (row + 1) * cell_height,
            )
            populated = rgba.crop(box).getchannel("A").getbbox() is not None
            expected = column in USED_COLUMNS[row]
            if expected and not populated:
                findings.append(error("cell.empty", f"Required cell r{row}c{column} is empty"))
            elif not expected and populated:
                findings.append(
                    error("cell.used", f"Unused cell r{row}c{column} is not transparent")
                )
    return findings


def validate_validation_snapshot(path: Path) -> list[Finding]:
    data, findings = load_json(path)
    if data is None:
        return findings
    expected: dict[str, object] = {
        "ok": True,
        "format": "WEBP",
        "mode": "RGBA",
        "columns": 8,
        "rows": 11,
        "sprite_version_number": 2,
        "width": ATLAS_SIZE[0],
        "height": ATLAS_SIZE[1],
        "transparent_rgb_residue_pixels": 0,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            findings.append(error("snapshot.value", f"validation.json {key!r} must be {value!r}"))
    snapshot_file = data.get("file")
    if not isinstance(snapshot_file, str) or not portable_path(snapshot_file):
        findings.append(
            error("snapshot.path", "validation.json file must be a portable relative path")
        )
    snapshot_errors = data.get("errors")
    if snapshot_errors != []:
        findings.append(error("snapshot.errors", "validation.json errors must be empty"))
    cells = data.get("cells")
    if not isinstance(cells, list) or len(cells) != 88:
        findings.append(error("snapshot.cells", "validation.json must describe all 88 cells"))
    return findings


def validate_direction_semantics(path: Path) -> list[Finding]:
    data, findings = load_json(path)
    if data is None:
        return findings
    if data.get("ok") is not True:
        findings.append(error("directions.ok", "direction-semantics.json must have ok=true"))
    raw_directions = data.get("directions")
    if not isinstance(raw_directions, list):
        return [*findings, error("directions.shape", "directions must be an array")]

    observed_order: list[str] = []
    required_text = (
        "expected",
        "observed",
        "horizontalEvidence",
        "verticalEvidence",
        "reason",
    )
    for index, raw_item in enumerate(raw_directions):
        if not isinstance(raw_item, dict):
            findings.append(error("directions.item", f"Direction item {index} must be an object"))
            continue
        item = cast(JsonObject, raw_item)
        direction = item.get("direction")
        if isinstance(direction, str):
            observed_order.append(direction)
        else:
            findings.append(error("directions.label", f"Direction item {index} needs a label"))
        verdict = item.get("verdict")
        if verdict not in {"pass", "warning"}:
            findings.append(
                error(
                    "directions.verdict",
                    f"Direction {direction!r} has invalid verdict {verdict!r}",
                )
            )
        for key in required_text:
            if not nonempty_string(item.get(key)):
                findings.append(
                    error("directions.evidence", f"Direction {direction!r} needs {key}")
                )
    if observed_order != EXPECTED_DIRECTIONS:
        findings.append(error("directions.order", "Direction labels are missing or out of order"))
    return findings


def find_absolute_strings(value: object, location: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, str) and not portable_path(value):
        failures.append(location)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            failures.extend(find_absolute_strings(item, f"{location}[{index}]"))
    elif isinstance(value, dict):
        for key, item in cast(dict[object, object], value).items():
            failures.extend(find_absolute_strings(item, f"{location}.{key}"))
    return failures


def validate_run_summary(path: Path) -> list[Finding]:
    data, findings = load_json(path)
    if data is None:
        return findings
    if data.get("ok") is not True or data.get("spriteVersionNumber") != 2:
        findings.append(error("summary.status", "run-summary.json must describe a passing v2 run"))
    absolute_locations = find_absolute_strings(data)
    if absolute_locations:
        findings.append(
            error(
                "summary.paths",
                "run-summary.json contains absolute paths at " + ", ".join(absolute_locations),
            )
        )
    package_files = data.get("packageFiles")
    if package_files != ["pet.json", "spritesheet.webp"]:
        findings.append(error("summary.package", "run-summary.json packageFiles are incorrect"))
    return findings


def validate_review_images(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for name in ("contact-sheet.png", "look-directions.png"):
        path = root / name
        if not path.is_file():
            findings.append(error("file.missing", f"Required file is missing: {name}"))
            continue
        try:
            with Image.open(path) as image:
                if image.format != "PNG":
                    findings.append(error("qa-image.format", f"{name} must be PNG"))
                image.verify()
        except (OSError, ValueError) as exc:
            findings.append(error("qa-image.invalid", f"Cannot decode {name}: {exc}"))
    return findings


def validate_repository(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(validate_manifest(root / "pet.json"))
    findings.extend(validate_spritesheet(root / "spritesheet.webp"))
    findings.extend(validate_validation_snapshot(root / "validation.json"))
    findings.extend(validate_direction_semantics(root / "direction-semantics.json"))
    findings.extend(validate_run_summary(root / "run-summary.json"))
    findings.extend(validate_review_images(root))
    findings.extend(error("previews.stale", message) for message in check_previews(root))
    return findings
