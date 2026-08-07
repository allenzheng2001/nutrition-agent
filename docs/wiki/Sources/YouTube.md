# YouTube Fetcher

Up: [[Sources]]

**Status: done.**

Wraps two libraries:
- `yt-dlp` — video metadata (title, channel, upload date, duration,
  description), metadata-only (`skip_download`).
- `youtube-transcript-api` — caption fetch. Uses whatever transcript is
  available (auto-generated captions included); doesn't do audio
  transcription itself.

**Code:** `src/nutrition_agent/ingestion/youtube.py`
**CLI:** `scripts/ingest_youtube.py`, driven by `data/seeds/youtube_videos.txt`

Returns `VideoRecord` (metadata) + `list[TranscriptSnippet]`
(`text`, `start`, `duration` per caption fragment) — not yet the generic
`RawDocument`/`TextSegment` shape from [[Sources]]. See [[Known Gaps]].

## Seed corpus (current)

9 videos from Paul Saladino MD's own channel plus podcast appearances
(JRE #1551, Shawn Ryan Show, Ultimate Human Podcast, a Bo Nickal
interview), curated for long-form/substantive content over his recent
short-form haul & reaction videos, which are lower signal for a knowledge
corpus. Full list in `data/seeds/youtube_videos.txt`.

Output: one JSON file per video in `data/corpus/youtube/<video_id>.json`,
396 chunks total across ~16 hours of transcript, plus a `_manifest.json`
summarizing ok/skipped/failed per run.

## Known failure modes

- `TranscriptUnavailable` — captions disabled or don't exist for a video.
  The CLI logs and continues rather than aborting the whole run.
- Metadata fetch failures (deleted/private video) propagate as-is; not
  yet caught separately from transcript failures.
