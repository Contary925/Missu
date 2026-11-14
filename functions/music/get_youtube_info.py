import asyncio
from urllib.parse import urlparse, parse_qs
import yt_dlp

# 1. Base Configuration
YTDLP_OPTIONS = {
    'format': 'bestaudio/best',
    'extract_flat': False,
    'skip_download': True,
    'force_generic_extractor': False,
    'youtube_include_dash_manifest': False,
    'nocheckcertificate': False,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    },
    "cookiefile": "cookies.txt",
}

async def get_youtube_info(query: str):
    def extract():
        if query.startswith(("http://", "https://")):
            options = YTDLP_OPTIONS
        else:
            options = {
                **YTDLP_OPTIONS,
                "playlist_items": "1",
                "youtube_include_nsig_html": False,
            }
        with yt_dlp.YoutubeDL(options) as ydl:
            if query.startswith(("http://", "https://")):
                return ydl.extract_info(query, download=False)
            return ydl.extract_info(
                f"ytsearch1:{query}",
                download=False,
            )

    info = await asyncio.to_thread(extract)
    if not info:
        return []

    # Handle containers
    if info.get("_type") == "playlist" and "entries" in info:
        songs = []
        for entry in info["entries"]:
            if not entry:
                continue
            video_id = entry.get("id")
            webpage_url = (
                entry.get("webpage_url")
                or (
                    f"https://www.youtube.com/watch?v={video_id}"
                    if video_id else None
                )
            )
            if not webpage_url:
                continue
            songs.append({
                "url": entry.get("url"),
                "webpage_url": webpage_url,
                "title": entry.get("title", "Unknown"),
            })
        return songs

    stream_url = info.get("url")
    if not stream_url and info.get("formats"):
        audio_formats = [
            f for f in info["formats"]
            if f.get("vcodec") == "none" and f.get("url")
        ]
        formats = info.get("formats") or []
        if audio_formats:
            stream_url = audio_formats[-1]["url"]
        elif formats:
            stream_url = formats[-1].get("url")
    if not stream_url:
        return []
    return [{
        "url": stream_url,
        "webpage_url": info.get("webpage_url"),
        "title": info.get("title", "Unknown"),
    }]

async def search_youtube_multiple(query: str, limit: int = 5):
    def extract():
        opts = {
            **YTDLP_OPTIONS,
            "extract_flat": True,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(
                f"ytsearch{limit}:{query}",
                download=False,
            )
    info = await asyncio.to_thread(extract)
    if not info or not info.get("entries"):
        return []
    songs = []
    for entry in info["entries"]:
        if not entry:
            continue
        video_id = entry.get("id")
        webpage_url = (
            entry.get("webpage_url")
            or (
                f"https://www.youtube.com/watch?v={video_id}"
                if video_id else None
            )
        )
        if not webpage_url:
            continue
        songs.append({
            "title": entry.get("title", "Unknown"),
            "webpage_url": webpage_url,
            "duration": entry.get("duration"),
            "uploader": entry.get("uploader") or entry.get("channel"),
        })
    return songs