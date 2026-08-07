"""Fetch video metadata and transcripts from YouTube."""

from __future__ import annotations

from dataclasses import dataclass, field

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript


@dataclass
class TranscriptSnippet:
    text: str
    start: float
    duration: float


@dataclass
class VideoRecord:
    video_id: str
    title: str
    channel: str
    channel_id: str
    url: str
    upload_date: str | None
    duration_s: int | None
    description: str
    transcript_language: str | None = None
    transcript_is_generated: bool | None = None
    snippets: list[TranscriptSnippet] = field(default_factory=list)


class TranscriptUnavailable(Exception):
    """Raised when a video has no fetchable transcript (captions disabled, etc.)."""


def fetch_metadata(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {"skip_download": True, "quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def fetch_transcript(video_id: str) -> tuple[list[TranscriptSnippet], str, bool]:
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id)
    except CouldNotRetrieveTranscript as e:
        raise TranscriptUnavailable(f"{video_id}: {e}") from e

    snippets = [
        TranscriptSnippet(text=s.text, start=s.start, duration=s.duration)
        for s in fetched
    ]
    return snippets, fetched.language_code, fetched.is_generated


def fetch_video(video_id: str) -> VideoRecord:
    """Fetch metadata + transcript for a single video. Raises TranscriptUnavailable
    if captions can't be retrieved; metadata fetch failures propagate as-is."""
    meta = fetch_metadata(video_id)
    snippets, lang, is_generated = fetch_transcript(video_id)

    return VideoRecord(
        video_id=video_id,
        title=meta.get("title", ""),
        channel=meta.get("channel") or meta.get("uploader") or "",
        channel_id=meta.get("channel_id", ""),
        url=f"https://www.youtube.com/watch?v={video_id}",
        upload_date=meta.get("upload_date"),
        duration_s=meta.get("duration"),
        description=meta.get("description", ""),
        transcript_language=lang,
        transcript_is_generated=is_generated,
        snippets=snippets,
    )
