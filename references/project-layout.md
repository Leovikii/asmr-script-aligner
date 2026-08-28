# Local Project Layout

The skill repository contains reusable instructions and scripts only. Each work belongs in a separate local project directory chosen by the user.

```text
<project>/
|-- project.json
|-- source/
|   |-- script/              Original PDF files
|   `-- audio/               Original audio tracks
|-- work/
|   |-- pipeline.json        Stage state and provenance
|   |-- script/
|   |   |-- raw.txt          Direct extraction before cleanup
|   |   `-- lines.jsonl      Ordered script units
|   |-- asr/                 One <track-id>.jsonl per audio track
|   |-- alignment/           Japanese timing master candidates
|   `-- translation/         One language folder, such as zh-Hans/
|-- review/
|   |-- alignment/           Japanese alignment TSV files
|   `-- translation/         Translation TSV files by language
|-- output/                  Final language-tagged .vtt/.srt/.lrc files
`-- logs/                    Tool logs and diagnostics
```

Do not add empty per-track placeholders. Create track artifacts only after a source track is discovered.

## Configuration

`project.json` is the stable user configuration. Keep paths relative to the project root when possible so the project can move as a unit. The initializer supplies conservative defaults:

- `language`: `ja`
- `script_authority`: `pdf`
- `output.formats`: initially empty unless explicitly chosen; selected from `vtt`, `srt`, `lrc`
- `output.karaoke`: `false`
- `translation.targets`: `zh-Hans` by default
- confidence and cue-duration thresholds used to prioritize review

Tool- or model-specific choices belong under `tools` only after selection. Do not make a particular ASR implementation mandatory when another installed local engine can emit timestamped Japanese segments.

`work/pipeline.json` is generated state, not user configuration. Each stage has `status`, `updated_at`, and `inputs`. Use `not_started`, `complete`, or `stale`; a running command may temporarily use `running`, but must replace it after success or failure.

## Source Handling

Never edit files under `source/`. If the user provides files elsewhere, either leave them in place and record explicit paths, or copy them into `source/` when the user wants a self-contained project. Do not silently move them.

Track IDs should be stable, filesystem-safe, and ordered, for example `01-main`, `02-bonus`. Derive them once and keep the mapping in project state even if display titles change.

## Re-running

Artifacts in `work/`, `review/`, and `output/` are reproducible but may include manual review decisions. Before replacing a review TSV, preserve accepted edits or write a new candidate beside it. An upstream change makes dependent stages stale:

```text
ingest -> extract -> segment -> transcribe -> align -> review_alignment
       -> translate -> review_translation -> export
```

PDF-only changes do not require re-transcription when audio fingerprints and ASR settings are unchanged. Audio or ASR-setting changes do.

## Output Names

Use language tags so source and translation never overwrite each other:

```text
output/<track-id>.ja.vtt
output/<track-id>.zh-Hans.vtt
output/<track-id>.ja.srt
output/<track-id>.zh-Hans.srt
```

Create a bilingual file such as `<track-id>.ja-zh-Hans.vtt` only when the user explicitly requests bilingual display. Separate monolingual files are the default.
