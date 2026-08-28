#!/usr/bin/env python3
"""Validate a local project skeleton and summarize its pipeline state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


STAGES = (
    "ingest",
    "extract",
    "segment",
    "transcribe",
    "align",
    "review_alignment",
    "translate",
    "review_translation",
    "export",
)
REQUIRED_DIRECTORIES = (
    "source/script",
    "source/audio",
    "work/script",
    "work/asr",
    "work/alignment",
    "work/translation/zh-Hans",
    "review/alignment",
    "review/translation/zh-Hans",
    "output",
    "logs",
)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing {path.name}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_directory", type=Path)
    args = parser.parse_args()
    root = args.project_directory.expanduser().resolve()

    problems: list[str] = []
    try:
        project = load_json(root / "project.json")
        pipeline = load_json(root / "work" / "pipeline.json")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for relative in REQUIRED_DIRECTORIES:
        if not (root / relative).is_dir():
            problems.append(f"missing directory: {relative}")

    if project.get("schema_version") != 1:
        problems.append("unsupported project schema_version")
    stages = pipeline.get("stages")
    if not isinstance(stages, dict):
        problems.append("pipeline stages must be an object")
        stages = {}

    print(f"Project: {project.get('name', root.name)}")
    print(f"Root: {root}")
    output = project.get("output", {})
    formats = output.get("formats", []) if isinstance(output, dict) else []
    print(f"Output formats: {', '.join(formats) if formats else 'not selected'}")
    for stage in STAGES:
        entry = stages.get(stage, {})
        status = entry.get("status", "missing") if isinstance(entry, dict) else "invalid"
        print(f"{stage:19} {status}")
        if status not in {"not_started", "running", "complete", "stale"}:
            problems.append(f"invalid status for {stage}: {status}")

    script_count = len([path for path in (root / "source" / "script").glob("*") if path.is_file()])
    audio_count = len([path for path in (root / "source" / "audio").glob("*") if path.is_file()])
    print(f"Sources: {script_count} script file(s), {audio_count} audio file(s)")

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
