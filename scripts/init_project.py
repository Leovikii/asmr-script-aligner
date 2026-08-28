#!/usr/bin/env python3
"""Create a local ASMR subtitle-alignment project without overwriting user data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
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
DIRECTORIES = (
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


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_directory", type=Path, help="Local directory to initialize")
    parser.add_argument("--name", help="Project display name; defaults to the directory name")
    parser.add_argument("--pdf", action="append", default=[], type=Path, help="PDF to copy; repeatable")
    parser.add_argument("--audio", action="append", default=[], type=Path, help="Audio file to copy; repeatable")
    parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        choices=("vtt", "srt", "lrc"),
        help="Output format; repeatable, left unset when omitted",
    )
    args = parser.parse_args()

    root = args.project_directory.expanduser().resolve()
    config_path = root / "project.json"
    state_path = root / "work" / "pipeline.json"

    managed_files = [path for path in (config_path, state_path) if path.exists()]
    if managed_files:
        joined = ", ".join(str(path) for path in managed_files)
        print(f"Refusing to overwrite existing project state: {joined}", file=sys.stderr)
        return 2

    if root.exists() and not root.is_dir():
        print(f"Project path is not a directory: {root}", file=sys.stderr)
        return 2

    sources = [(path.expanduser().resolve(), "source/script") for path in args.pdf]
    sources.extend((path.expanduser().resolve(), "source/audio") for path in args.audio)
    missing = [str(path) for path, _ in sources if not path.is_file()]
    if missing:
        print(f"Source file not found: {', '.join(missing)}", file=sys.stderr)
        return 2

    destinations = [root / relative / path.name for path, relative in sources]
    if len({str(path).casefold() for path in destinations}) != len(destinations):
        print("Two supplied sources would have the same destination name", file=sys.stderr)
        return 2
    existing_destinations = [str(path) for path in destinations if path.exists()]
    if existing_destinations:
        print(f"Refusing to overwrite source file: {', '.join(existing_destinations)}", file=sys.stderr)
        return 2

    root.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    project = {
        "schema_version": 1,
        "name": args.name or root.name,
        "language": "ja",
        "script_authority": "pdf",
        "paths": {
            "script_source": "source/script",
            "audio_source": "source/audio",
            "work": "work",
            "review": "review",
            "output": "output",
        },
        "translation": {"targets": ["zh-Hans"]},
        "output": {
            "profile": None,
            "formats": list(dict.fromkeys(args.formats or [])),
            "languages": ["ja", "zh-Hans"],
            "bilingual": False,
            "karaoke": False,
            "encoding": "utf-8",
        },
        "review": {
            "low_confidence_below": 0.72,
            "long_cue_seconds": 12.0,
            "large_gap_seconds": 8.0,
        },
        "tools": {},
    }
    pipeline = {
        "schema_version": 1,
        "created_at": now,
        "stages": {
            stage: {"status": "not_started", "updated_at": None, "inputs": {}}
            for stage in STAGES
        },
    }

    write_json(config_path, project)
    write_json(state_path, pipeline)
    for source, relative in sources:
        shutil.copy2(source, root / relative / source.name)
    print(f"Initialized ASMR subtitle project at {root}")
    if sources:
        print(f"Copied {len(args.pdf)} PDF(s) and {len(args.audio)} audio file(s).")
    else:
        print("Next: place PDFs in source/script and audio files in source/audio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
