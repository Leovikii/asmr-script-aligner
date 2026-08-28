# Data Contracts

All JSONL files are UTF-8, one JSON object per physical line, with times expressed as decimal seconds. Preserve unknown fields when rewriting records.

## Script units: `work/script/lines.jsonl`

Required fields:

```json
{"id":"s000001","order":1,"kind":"dialogue","text":"おかえりなさい。","source":{"file":"script.pdf","page":3}}
```

- `kind`: `dialogue`, `direction`, `speaker`, or `metadata`.
- `text` is the display-authority wording extracted from the PDF.
- Optional fields may include `speaker`, `scene`, `raw_text`, and extraction notes.

## ASR segments: `work/asr/<track-id>.jsonl`

Required fields:

```json
{"id":"a000001","start":1.24,"end":3.81,"text":"おかえりなさい","confidence":0.91}
```

`confidence` may be `null` if the engine does not expose a comparable score. Optional word timing may be retained, but downstream steps must not require it.

## Alignment: `work/alignment/<track-id>.jsonl`

Required fields:

```json
{"id":"c000001","script_ids":["s000001"],"asr_ids":["a000001"],"start":1.24,"end":3.81,"text":"おかえりなさい。","score":0.94,"status":"matched","flags":[]}
```

- `status`: `matched`, `unmatched_script`, `adlib`, or `excluded`.
- `score` is an alignment score from 0 to 1 or `null`; document how it was derived.
- `flags` may contain `low_confidence`, `long_cue`, `large_gap`, `overlap`, `boundary_uncertain`, or a documented project-specific value.
- `start` and `end` may be `null` only for unresolved/excluded records.

## Alignment review TSV: `review/alignment/<track-id>.tsv`

Use this fixed leading column order:

```text
id	include	start	end	text	status	score	flags	note
```

- `include` is `yes` or `no`.
- Escape embedded tabs and line breaks as `\\t` and `\\n`; reverse the escaping when importing.
- User edits to `text`, `start`, `end`, `include`, and `note` take precedence over automated candidates.
- Keep stable `id` values so a revised alignment can reconcile prior review decisions.

## Translation: `work/translation/<language>/<track-id>.jsonl`

Translation records reference the locked Japanese timing master rather than duplicating timing:

```json
{"cue_id":"c000001","source_language":"ja","target_language":"zh-Hans","source_text":"おかえりなさい。","text":"欢迎回来。","status":"translated","flags":[]}
```

- `cue_id` must match exactly one alignment record.
- `status`: `translated`, `untranslated`, or `excluded`.
- Optional `flags` include `needs_context`, `term_uncertain`, `reading_load`, and `source_issue`.
- Timing always comes from the locked alignment record. Translation records must not define independent `start` or `end` fields.

## Translation review TSV

Store it at `review/translation/<language>/<track-id>.tsv` with this fixed leading order:

```text
cue_id	include	source_text	text	status	flags	note
```

Keep source and translated text side by side. Escape tabs and line breaks using the same rules as alignment review TSV.

## Pipeline state: `work/pipeline.json`

The initializer creates every stage with `not_started`. On completion, record `updated_at`, relevant input hashes, tool/model settings, and output paths. A stage is reusable only when its recorded inputs still match current inputs.
