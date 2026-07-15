from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CELL_SIZE = (192, 208)
SCALE = 2
PREVIEW_SIZE = (CELL_SIZE[0] * SCALE, CELL_SIZE[1] * SCALE)
LABEL_HEIGHT = 48
CHECKER_TILE = 16
MAX_GIF_BYTES = 2_000_000
MAX_TOTAL_GIF_BYTES = 8_000_000
CHECKER_COLORS = ((244, 244, 244, 255), (222, 222, 222, 255))
LOOK_DIRECTIONS = (
    "000 up",
    "022.5 up-right",
    "045 up-right",
    "067.5 up-right",
    "090 right",
    "112.5 down-right",
    "135 down-right",
    "157.5 down-right",
    "180 down",
    "202.5 down-left",
    "225 down-left",
    "247.5 down-left",
    "270 left",
    "292.5 up-left",
    "315 up-left",
    "337.5 up-left",
)


@dataclass(frozen=True)
class AnimationSpec:
    animation_id: str
    cells: tuple[tuple[int, int], ...]
    durations_ms: tuple[int, ...]
    labels: tuple[str, ...] | None = None

    @property
    def filename(self) -> str:
        return f"{self.animation_id}.gif"

    @property
    def output_size(self) -> tuple[int, int]:
        extra_height = LABEL_HEIGHT if self.labels is not None else 0
        return PREVIEW_SIZE[0], PREVIEW_SIZE[1] + extra_height


def row_cells(row: int, count: int) -> tuple[tuple[int, int], ...]:
    return tuple((row, column) for column in range(count))


STANDARD_SPECS = (
    AnimationSpec("idle", row_cells(0, 6), (280, 110, 110, 140, 140, 320)),
    AnimationSpec(
        "running-right", row_cells(1, 8), (120, 120, 120, 120, 120, 120, 120, 220)
    ),
    AnimationSpec(
        "running-left", row_cells(2, 8), (120, 120, 120, 120, 120, 120, 120, 220)
    ),
    AnimationSpec("waving", row_cells(3, 4), (140, 140, 140, 280)),
    AnimationSpec("jumping", row_cells(4, 5), (140, 140, 140, 140, 280)),
    AnimationSpec(
        "failed", row_cells(5, 8), (140, 140, 140, 140, 140, 140, 140, 240)
    ),
    AnimationSpec("waiting", row_cells(6, 6), (150, 150, 150, 150, 150, 260)),
    AnimationSpec("running", row_cells(7, 6), (120, 120, 120, 120, 120, 220)),
    AnimationSpec("review", row_cells(8, 6), (150, 150, 150, 150, 150, 280)),
)
LOOK_CELLS = row_cells(9, 8) + row_cells(10, 8)
LOOK_DURATIONS = (160,) * 16
ANIMATION_SPECS = (
    *STANDARD_SPECS,
    AnimationSpec("look-directions", LOOK_CELLS, LOOK_DURATIONS),
    AnimationSpec("look-directions-labeled", LOOK_CELLS, LOOK_DURATIONS, LOOK_DIRECTIONS),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkerboard(size: tuple[int, int]) -> Image.Image:
    image = Image.new("RGBA", size, CHECKER_COLORS[0])
    draw = ImageDraw.Draw(image)
    for top in range(0, size[1], CHECKER_TILE):
        for left in range(0, size[0], CHECKER_TILE):
            color = CHECKER_COLORS[(left // CHECKER_TILE + top // CHECKER_TILE) % 2]
            draw.rectangle(
                (
                    left,
                    top,
                    min(left + CHECKER_TILE - 1, size[0] - 1),
                    min(top + CHECKER_TILE - 1, size[1] - 1),
                ),
                fill=color,
            )
    return image


def crop_cell(atlas: Image.Image, row: int, column: int) -> Image.Image:
    width, height = CELL_SIZE
    return atlas.crop(
        (column * width, row * height, (column + 1) * width, (row + 1) * height)
    )


def render_frame(cell: Image.Image, label: str | None = None) -> Image.Image:
    sprite = cell.resize(PREVIEW_SIZE, Image.Resampling.NEAREST)
    composed = checkerboard(PREVIEW_SIZE)
    composed.alpha_composite(sprite)
    if label is None:
        return composed.convert("RGB")

    canvas = Image.new("RGB", (PREVIEW_SIZE[0], PREVIEW_SIZE[1] + LABEL_HEIGHT), "white")
    canvas.paste(composed.convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.line((0, PREVIEW_SIZE[1], PREVIEW_SIZE[0], PREVIEW_SIZE[1]), fill=(190, 190, 190))
    font = ImageFont.load_default(size=22)
    box = draw.textbbox((0, 0), label, font=font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    draw.text(
        ((PREVIEW_SIZE[0] - text_width) // 2, PREVIEW_SIZE[1] + (LABEL_HEIGHT - text_height) // 2),
        label,
        fill=(30, 30, 30),
        font=font,
    )
    return canvas


def save_gif(frames: list[Image.Image], durations: tuple[int, ...], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=list(durations),
        loop=0,
        disposal=2,
        optimize=True,
    )


def animation_manifest(spec: AnimationSpec, path: Path) -> dict[str, object]:
    return {
        "id": spec.animation_id,
        "file": f"previews/{spec.filename}",
        "cells": [{"row": row, "column": column} for row, column in spec.cells],
        "durationsMs": list(spec.durations_ms),
        "frameCount": len(spec.cells),
        "size": list(spec.output_size),
        "labeled": spec.labels is not None,
        "sha256": sha256_file(path),
    }


def generate_previews(root: Path, output_dir: Path | None = None) -> dict[str, object]:
    repository = root.resolve()
    source_path = repository / "spritesheet.webp"
    target = output_dir or repository / "previews"
    if not source_path.is_file():
        raise FileNotFoundError(f"Missing spritesheet: {source_path}")

    with Image.open(source_path) as opened:
        opened.load()
        if opened.size != (1536, 2288):
            raise ValueError(f"Expected a 1536x2288 atlas, found {opened.size}")
        atlas = opened.convert("RGBA")

    target.mkdir(parents=True, exist_ok=True)
    animations: list[dict[str, object]] = []
    for spec in ANIMATION_SPECS:
        frames = [
            render_frame(
                crop_cell(atlas, row, column),
                None if spec.labels is None else spec.labels[index],
            )
            for index, (row, column) in enumerate(spec.cells)
        ]
        output = target / spec.filename
        save_gif(frames, spec.durations_ms, output)
        animations.append(animation_manifest(spec, output))

    manifest: dict[str, object] = {
        "schemaVersion": 1,
        "source": {"file": "spritesheet.webp", "sha256": sha256_file(source_path)},
        "render": {
            "scale": SCALE,
            "cellSize": list(CELL_SIZE),
            "previewSize": list(PREVIEW_SIZE),
            "checkerTile": CHECKER_TILE,
            "checkerColors": [list(color[:3]) for color in CHECKER_COLORS],
            "loop": 0,
            "lookDurationMs": LOOK_DURATIONS[0],
        },
        "animations": animations,
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


def expected_preview_files() -> tuple[str, ...]:
    return *(spec.filename for spec in ANIMATION_SPECS), "manifest.json"


def validate_gif_contract(path: Path, spec: AnimationSpec) -> list[str]:
    failures: list[str] = []
    try:
        with Image.open(path) as opened:
            if opened.size != spec.output_size:
                failures.append(
                    f"previews/{path.name} has size {opened.size}, expected {spec.output_size}"
                )
            if opened.n_frames != len(spec.cells):
                failures.append(
                    f"previews/{path.name} has {opened.n_frames} frames, "
                    f"expected {len(spec.cells)}"
                )
            if opened.info.get("loop") != 0:
                failures.append(f"previews/{path.name} must loop forever")
            durations: list[int] = []
            for index in range(opened.n_frames):
                opened.seek(index)
                duration = opened.info.get("duration")
                durations.append(duration if isinstance(duration, int) else 0)
            if tuple(durations) != spec.durations_ms:
                failures.append(
                    f"previews/{path.name} durations {durations} do not match "
                    f"{list(spec.durations_ms)}"
                )
    except (OSError, ValueError) as exc:
        failures.append(f"Cannot decode previews/{path.name}: {exc}")
    if path.stat().st_size > MAX_GIF_BYTES:
        failures.append(
            f"previews/{path.name} is {path.stat().st_size} bytes; limit is {MAX_GIF_BYTES}"
        )
    return failures


def check_previews(root: Path) -> list[str]:
    repository = root.resolve()
    committed = repository / "previews"
    missing = [name for name in expected_preview_files() if not (committed / name).is_file()]
    if missing:
        return [f"Missing committed preview: previews/{name}" for name in missing]

    failures = [
        failure
        for spec in ANIMATION_SPECS
        for failure in validate_gif_contract(committed / spec.filename, spec)
    ]
    total_gif_bytes = sum((committed / spec.filename).stat().st_size for spec in ANIMATION_SPECS)
    if total_gif_bytes > MAX_TOTAL_GIF_BYTES:
        failures.append(
            f"Committed GIF previews use {total_gif_bytes} bytes; "
            f"limit is {MAX_TOTAL_GIF_BYTES}"
        )

    with tempfile.TemporaryDirectory(prefix="codex-pet-previews-") as temp:
        regenerated = Path(temp)
        generate_previews(repository, regenerated)
        for name in expected_preview_files():
            current_hash = sha256_file(committed / name)
            expected_hash = sha256_file(regenerated / name)
            if current_hash != expected_hash:
                failures.append(
                    f"previews/{name} is stale; run `generate-codex-previews .`"
                )
        return failures
