---
name: asmr-script-aligner
description: Initialize local projects from Japanese text-based PDF scripts and ASMR audio, build reviewed source-language timing, translate by cue when requested, and export non-karaoke WebVTT, SRT, or LRC subtitles. Use for script-to-audio subtitle projects; do not use for ordinary subtitle translation or video editing.
metadata:
  version: "1.0.0"
---

# ASMR Script Aligner

Build subtitles from a clean PDF script and Japanese ASMR audio. Treat the PDF as the wording authority and speech recognition as timing evidence. Keep source media, intermediate data, and exports in a user-selected local project directory, not in this skill directory.

## Start or Resume

For a new project, locate the PDF and audio paths supplied by the user. Choose a project name from the work title, PDF stem, or common source-folder name. Use the user's requested project root; if none was given, create a sibling project folder beside the supplied sources when that location is writable and unambiguous. Never initialize inside this skill repository. Resolve `scripts/init_project.py` relative to this `SKILL.md`; do not assume the current working directory is the skill directory. Then run one command that creates the project and copies the supplied sources:

```powershell
python <skill-directory>/scripts/init_project.py <project-directory> --name <project-name> --pdf <script.pdf> --audio <track.wav>
```

Repeat `--pdf` or `--audio` for multiple inputs. `--format vtt`, `--format srt`, and `--format lrc` are optional and repeatable when the user has already chosen. Explicit user choices win. When no format is stated, leave `output.formats` empty during initialization; recommend formats from the intended consumer before export rather than silently choosing one. For DLsite delivery recommend VTT, for broad interchange and manual inspection recommend SRT, and for audio players that specifically consume timestamped lyrics recommend LRC. The internal reviewed JSONL alignment remains the canonical timing master in every case.

The script must validate every supplied source before creating anything and must not overwrite an existing project or source file.

If source paths were not supplied, initialize the empty project and tell the user where to place PDFs and audio. If the inferred project location is ambiguous or would require writing outside a location the user placed in scope, ask for the desired parent folder before creating it.

For an existing project, read `project.json` and `work/pipeline.json`, inventory the declared source directories, and resume at the first incomplete stage whose inputs are valid. Run `<skill-directory>/scripts/project_status.py` using its resolved absolute path when the current state is unclear.

Read [references/project-layout.md](references/project-layout.md) when initializing, relocating, or repairing a project. Read [references/pipeline.md](references/pipeline.md) before executing or resuming processing. Read [references/data-contracts.md](references/data-contracts.md) when creating, consuming, or validating JSONL/TSV artifacts. Read [references/subtitle-style.md](references/subtitle-style.md) before translating or exporting subtitles.

## Operating Rules

- Never modify the original PDF or audio.
- Prefer embedded PDF text. Use OCR only for pages where embedded text is absent or unusable.
- Keep Japanese text in its original language. Normalize layout noise without paraphrasing spoken wording.
- Preserve monotonic order: later script lines cannot align to earlier audio unless the project explicitly marks a replay or alternate take.
- Use ASR to locate speech, not to replace clear scripted wording. Record genuine ad-libs separately.
- Flag uncertain, unmatched, overlapping, or implausibly long cues for review instead of inventing alignment.
- Keep processing local unless the user explicitly authorizes an external transcription or storage service.
- Produce cue-level subtitles only. WebVTT and SRT have one interval per cue; LRC has one timestamp per displayed line. Do not generate word-level or karaoke timing.
- Finish and review the Japanese timing master before translating. Translation reuses stable cue IDs and timing; it must not drive source alignment.
- Write UTF-8 output and retain enough provenance to regenerate exports after corrections.

## Pipeline

Run these stages in order, while allowing a completed valid stage to be reused:

1. **Ingest** — inventory PDFs and audio, record stable track IDs, durations, and source fingerprints.
2. **Extract** — extract embedded PDF text, clean headers/footers/page artifacts, and preserve a raw text copy.
3. **Segment** — split spoken text into ordered units; mark directions, speaker labels, and non-spoken notes rather than silently mixing them into dialogue.
4. **Transcribe** — create timestamped Japanese ASR segments per track using an available local engine.
5. **Align** — monotonically match script units to ASR spans, allowing controlled many-to-one and one-to-many matches.
6. **Review alignment** — materialize a human-editable Japanese TSV, resolve low-confidence or structurally suspicious rows, and lock the timing master.
7. **Translate** — when requested, translate locked cues with surrounding context and a project glossary, without changing cue IDs or timing.
8. **Review translation** — review meaning, terminology, tone, readability, and omissions independently of alignment confidence.
9. **Export** — confirm a format choice if none is configured, then render requested WebVTT, SRT, and/or LRC files per track and language and validate ordering, bounds, encoding, and cue readability.

Update `work/pipeline.json` only after a stage passes its acceptance checks. If an upstream artifact changes, mark all dependent later stages stale.

## Completion

A project is complete when every requested audio track has a locked Japanese timing master, requested translations have been reviewed, requested exports validate, and unresolved rows are either fixed or explicitly accepted by the user. Report output paths, languages, review exceptions, and the local tools/models used. Do not copy project artifacts back into this skill repository.
