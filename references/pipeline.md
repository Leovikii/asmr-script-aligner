# Processing Pipeline

Use this procedure after reading the local project's `project.json` and current pipeline state.

## 1. Ingest

Inventory every PDF and supported audio file. Record size and a content hash, and obtain audio duration with an available local probe such as `ffprobe`. Assign stable ordered track IDs. Stop and report clearly if there is no readable PDF or no readable audio.

Acceptance checks:

- at least one PDF and one audio track exist;
- every source has a stable identity and no duplicate track ID;
- every audio duration is positive.

## 2. Extract PDF Text

Try embedded-text extraction first. Compare extracted character count and visible Japanese content page by page. Remove repeated headers, footers, page numbers, and layout-only spacing while keeping `work/script/raw.txt` as evidence. OCR only failed pages and record which pages used OCR.

Do not silently discard illustrations containing meaningful dialogue. Flag them if OCR is unavailable or unreliable.

Acceptance checks:

- extracted text is non-empty and predominantly plausible for the declared language;
- page order is preserved;
- normalization did not merge unrelated columns or scene blocks.

## 3. Segment the Script

Write `work/script/lines.jsonl` according to the data contract. Give each unit a stable sequential ID. Prefer natural utterances over printed line wraps. Keep punctuation that affects reading. Separate speaker labels and directions from spoken text; include them as metadata or non-dialogue units so later stages can exclude them without losing provenance.

For uncertain formatting, keep smaller units. Alignment may merge adjacent units later.

Acceptance checks:

- IDs are unique and ordered;
- every unit points back to a page or source location when available;
- spoken units contain original Japanese wording, not ASR substitutions.

## 4. Transcribe Audio

Use an available local Japanese-capable ASR engine that returns timestamps. Preserve the engine name, model, language setting, decoding settings, audio fingerprint, and runtime in pipeline state. Emit one `work/asr/<track-id>.jsonl` file per track.

ASR segmentation may be coarse because it provides anchors. Prefer reliable segment timestamps over word timestamps; do not spend time creating karaoke-grade timing.

Acceptance checks:

- segments are time-ordered and within track duration;
- detected text is plausibly Japanese speech;
- long silent regions and decode failures are visible rather than filled with fabricated text.

## 5. Align

Align script units to ASR spans with a global monotonic method. Compare normalized Japanese text while retaining original display text. Useful normalization can include Unicode width normalization, whitespace removal, conservative punctuation removal, and kana normalization for comparison only.

Permit these relationships when evidence supports them:

- one script unit to one ASR span;
- several adjacent script units to one ASR span;
- one script unit to several adjacent ASR spans;
- unmatched ASR as an ad-lib;
- unmatched script as omitted or unresolved.

Combine textual similarity with timing continuity and reasonable speaking duration. Do not force every line to match. Derive cue bounds from surrounding speech anchors, then add only modest configurable padding without crossing neighboring cues or track bounds.

Acceptance checks:

- cue order is monotonic;
- `0 <= start < end <= track duration` for timed cues;
- each scripted unit is matched once, explicitly unmatched, or excluded as non-spoken;
- low scores and suspicious durations are flagged.

## 6. Review and Lock Japanese Alignment

Write `review/alignment/<track-id>.tsv` with all aligned cues, not only failures. Sort review priority by error, then low confidence, unmatched content, excessive duration, large gap, and overlap. Let the user edit display text, start/end times, and decision fields.

Re-import review data without discarding row IDs. Treat `accepted` as an explicit decision, not as proof that the automated confidence was high. Preserve ad-libs only when the user wants them in the subtitle.

Acceptance checks:

- TSV round-trips as UTF-8 without losing tabs/newlines through escaping;
- every included cue has a final decision;
- unresolved items are summarized for the user.

After these checks pass, mark the Japanese alignment `locked`. Translation begins only from this locked timing master.

## 7. Translate

Translate each included locked cue into the configured target language, normally Simplified Chinese (`zh-Hans`). Keep the same cue ID, start, and end. Supply neighboring cues, speaker, scene, and glossary entries as translation context, but write only the current cue's translation to its record.

Translate meaning and performance tone rather than matching Japanese word order. Preserve intentional repetition, hesitation, honorific relationships, sound symbolism, and explicit adult meaning. Do not sanitize or intensify the content. Keep character names, recurring terms, and second-person address consistent through a project glossary.

If a natural Chinese sentence crosses cue boundaries, translate with cross-cue context but distribute the Chinese text across the existing cues. Change segmentation or timing only by reopening the Japanese alignment review; never create an independent Chinese timeline silently.

Acceptance checks:

- every included Japanese cue has one translated record or an explicit untranslated decision;
- translation records reuse source cue IDs and contain no independent timing;
- terminology and names follow the project glossary;
- empty, duplicated, or obviously truncated translations are flagged.

## 8. Review Translation

Write `review/translation/<language>/<track-id>.tsv`. Review accuracy, omissions, terminology, voice, and reading load. Alignment confidence and translation quality are separate fields: a well-timed cue can still need translation review.

Keep the locked Japanese text visible beside the translation. If the reviewer discovers a source segmentation or timing error, unlock and repair alignment, then mark translation and exports stale.

## 9. Export

Generate the formats requested in `project.json` from reviewed alignment. If `output.formats` is empty, do not guess: recommend a format using the intended consumer and obtain the user's selection before export.

For WebVTT, start with `WEBVTT`, then write blank-line-separated cues using `HH:MM:SS.mmm --> HH:MM:SS.mmm`. Do not emit styling, regions, voice tags, or per-word timestamps unless a target profile explicitly requires them. Recommend WebVTT for DLsite delivery, but keep that recommendation distinct from the user's final choice.

For LRC, use one `[mm:ss.xx]text` entry per cue start. Hours roll into minutes. Do not add per-word tags.

For SRT, use sequential integer indices and `HH:MM:SS,mmm --> HH:MM:SS,mmm`. Keep readable cue lengths; split only at natural boundaries and never reorder wording.

Validate:

- UTF-8 encoding;
- strictly nondecreasing cue order;
- SRT intervals are positive and do not overlap unless explicitly accepted;
- timestamps do not exceed audio duration;
- no blank subtitle events, internal IDs, confidence scores, or review markers leak into display text;
- reopening and regenerating from reviewed data produces equivalent output.

Export separate language-tagged files by default. A bilingual cue contains Japanese and Chinese on separate display lines only when requested and when reading load remains acceptable. Report the generated files per track, language, and any user-accepted exceptions.
