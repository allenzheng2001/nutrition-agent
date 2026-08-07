#!/usr/bin/env python3
"""CLI: fetch metadata + transcripts for a list of YouTube video IDs, chunk them,
and write one normalized JSON file per video into data/corpus/youtube/.

Usage:
    python scripts/ingest_youtube.py --seeds data/seeds/youtube_videos.txt
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from nutrition_agent.ingestion.chunk import chunk_snippets
from nutrition_agent.ingestion.youtube import TranscriptUnavailable, fetch_video

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_seed_ids(seed_file: Path) -> list[str]:
    ids = []
    for line in seed_file.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            ids.append(line)
    return ids


def ingest_one(video_id: str, out_dir: Path) -> dict:
    record = fetch_video(video_id)
    chunks = chunk_snippets(record.snippets)

    doc = {
        "video_id": record.video_id,
        "title": record.title,
        "channel": record.channel,
        "channel_id": record.channel_id,
        "url": record.url,
        "upload_date": record.upload_date,
        "duration_s": record.duration_s,
        "transcript_language": record.transcript_language,
        "transcript_is_generated": record.transcript_is_generated,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "chunks": [dataclasses.asdict(c) for c in chunks],
    }

    out_path = out_dir / f"{video_id}.json"
    out_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
    return doc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seeds",
        type=Path,
        default=REPO_ROOT / "data" / "seeds" / "youtube_videos.txt",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "data" / "corpus" / "youtube",
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-fetch videos that already have output"
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    video_ids = read_seed_ids(args.seeds)

    results = {"ok": [], "skipped": [], "failed": []}
    for video_id in video_ids:
        out_path = args.out / f"{video_id}.json"
        if out_path.exists() and not args.force:
            print(f"skip  {video_id} (already fetched)")
            results["skipped"].append(video_id)
            continue

        try:
            doc = ingest_one(video_id, args.out)
            print(f"ok    {video_id}  {len(doc['chunks'])} chunks  {doc['title']!r}")
            results["ok"].append(video_id)
        except TranscriptUnavailable as e:
            print(f"FAIL  {video_id}  no transcript: {e}", file=sys.stderr)
            results["failed"].append({"video_id": video_id, "reason": str(e)})
        except Exception as e:
            print(f"FAIL  {video_id}  {type(e).__name__}: {e}", file=sys.stderr)
            results["failed"].append({"video_id": video_id, "reason": str(e)})

    manifest_path = args.out / "_manifest.json"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": results["ok"],
        "skipped": results["skipped"],
        "failed": results["failed"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(
        f"\n{len(results['ok'])} ok, {len(results['skipped'])} skipped, "
        f"{len(results['failed'])} failed"
    )
    return 1 if results["failed"] and not results["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
