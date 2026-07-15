# Izumi Konata Codex Pet

An animated Codex pet based on Izumi Konata from *Lucky Star*.

## Install

Copy `pet.json` and `spritesheet.webp` into:

```text
~/.codex/pets/izumi-konata/
```

The package uses the Codex v2 pet format:

- 8 columns x 11 rows
- 192 x 208 pixel cells
- 1536 x 2288 pixel atlas
- 9 standard animation states
- 16 clockwise look directions
- `spriteVersionNumber: 2`

## Files

- `pet.json`: Codex pet manifest
- `spritesheet.webp`: installable animated sprite atlas
- `contact-sheet.png`: all animation frames
- `look-directions.png`: labeled look-direction review sheet
- `validation.json`: deterministic atlas validation
- `direction-semantics.json`: per-direction visual QA
- `run-summary.json`: generation and packaging summary

## Status

The atlas passes v2 geometry, transparency, standard animation, cardinal-direction, blind-direction, continuity, and final visual QA checks.

This is an unofficial fan-made project. Izumi Konata and *Lucky Star* belong to their respective rights holders. No affiliation or endorsement is implied.
