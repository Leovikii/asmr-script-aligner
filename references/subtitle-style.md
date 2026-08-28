# Subtitle and Translation Style

## Source Timing Master

Japanese is the source-language timing master. Lock its text, cue order, and timestamps before translation. A cue should normally represent one natural spoken unit, not one printed PDF line and not one ASR segment.

- Preserve the PDF's intended spoken wording while removing layout artifacts.
- Exclude stage directions and speaker labels from display unless they are spoken or needed for comprehension.
- Keep meaningful hesitation, repetition, sentence-final particles, breaths, laughter, and sound effects when the project wants them represented.
- Do not add words merely because silence seems long.
- Prefer one or two readable display lines. Break at phrase boundaries, never in the middle of a tightly bound expression.
- Avoid overlapping cues. Use modest gaps where the audio supports them.

Timing is based on audible speech. Begin close to speech onset and end after the utterance without covering unrelated silence. Do not create word-level highlighting.

## Simplified Chinese Translation

Translate after alignment review so that translation cannot distort matching. Reuse each Japanese cue's ID and timing.

- Translate the intended meaning, relationship, and performance tone, not Japanese word order.
- Preserve explicit adult meaning faithfully; neither euphemize nor intensify it.
- Keep names, honorific relationships, pronouns, recurring body terms, commands, and onomatopoeia consistent through a glossary.
- Use natural Simplified Chinese punctuation. Avoid explanatory notes inside subtitle text.
- Read neighboring cues before translating ellipsis, omitted subjects, callbacks, and sentence fragments.
- Keep the Chinese concise enough for the locked cue duration. Do not delete important meaning solely to shorten it; flag excessive reading load for review.
- Do not translate non-lexical sounds mechanically when Chinese text would distract. Apply one project-wide convention.

Review factual meaning, tone, terminology, omissions, additions, and reading load separately from timing quality.

## Export Profiles

The reviewed alignment JSONL is the canonical source because it retains cue IDs, start and end times, confidence, provenance, and review decisions. Subtitle formats are disposable exports.

Choose by consumer:

| Need | Recommended format | Reason |
| --- | --- | --- |
| DLsite delivery | VTT | Matches the stated platform delivery format and retains cue end times |
| General exchange, editing, or broad player compatibility | SRT | Simple, widely supported, and easy to inspect manually |
| Audio player with lyric-file support | LRC | Convenient beside audio, but usually stores only cue starts |
| More than one downstream target | Export VTT and SRT from the same master | Regeneration is cheap and avoids converting one lossy subtitle format into another |

Do not select a format merely because it is technically available. If the consumer is unknown, explain these tradeoffs and ask before the export stage. LRC should not be the sole archival or interchange artifact because it lacks reliable cue ends.

### WebVTT for DLsite delivery

- File extension: `.vtt`
- First line: `WEBVTT`
- Encoding: UTF-8
- Timestamp: `HH:MM:SS.mmm --> HH:MM:SS.mmm`
- Blank line between cues
- No karaoke timestamps, CSS, regions, or metadata unless DLsite requirements for the specific delivery explicitly call for them
- Default files: `<track-id>.ja.vtt` and `<track-id>.zh-Hans.vtt`

### SRT

Use sequential integer cue numbers and comma milliseconds: `HH:MM:SS,mmm`. Keep separate language-tagged files by default.

### LRC

Use one `[mm:ss.xx]text` line per cue start. Hours roll into minutes. LRC has no reliable cue end time and is therefore a convenience export, not the timing master.

## Bilingual Output

Generate bilingual output only on request. Put Japanese first and Chinese second within each cue. Check reading load again because two-line bilingual cues may require longer display time. Never make bilingual display the only reviewed artifact; preserve separate Japanese and Chinese files.
