import asyncio
from urllib.parse import urlparse, parse_qs
import yt_dlp
import re

# 1. Base Configuration
YTDLP_OPTIONS = {
    'format': 'bestaudio/best',
    'extract_flat': False,
    'skip_download': True,
    'force_generic_extractor': False,
    'youtube_include_dash_manifest': False,
    'nocheckcertificate': True,
    'quiet': True,
    'js_runtimes': {
        'node': {}
    },
    'extractor_args': {
        'youtube': {
            'player_client': ['web'],
        }
    }
}

ydl_client = yt_dlp.YoutubeDL(YTDLP_OPTIONS)
ydl_playlist_client = yt_dlp.YoutubeDL({**YTDLP_OPTIONS, 'extract_flat': True})
ydl_search_client = yt_dlp.YoutubeDL({**YTDLP_OPTIONS, "playlist_items": "1"})

import re

async def resolve_single_stream(watch_url: str) -> str:
    """Extracts the underlying video ID regardless of how badly music.py sliced it."""
    watch_url = str(watch_url).strip()
    
    # 1. First, check if it's already a standard, clean YouTube URL
    if "watch?v=" in watch_url:
        id_match = re.search(r'v=([a-zA-Z0-9_-]{11})', watch_url)
        if id_match:
            video_id = id_match.group(1)
            watch_url = f"https://youtube.com{video_id}"
            
    # 2. If it is an ugly corrupted string like 'youtube.comcomayrybcg6'
    elif "youtube.com" in watch_url:
        # Strip out 'youtube.com' and any trailing junk, keeping the remaining trailing characters
        raw_tail = watch_url.split("youtube.com")[-1].strip("_")
        
        # If music.py accidentally ate the first two letters 'co' because they matched 'com',
        # we recover the ID from the tail of the broken domain string
        if raw_tail.startswith("com") and len(raw_tail) > 3:
            video_id = raw_tail[3:]  # Strip the duplicated 'com' slice
        else:
            video_id = raw_tail
            
        watch_url = f"https://youtube.com{video_id}"
        
    # 3. If it's a completely raw, naked ID string passed down
    elif not watch_url.startswith(("http://", "https://")):
        watch_url = f"https://youtube.com{watch_url}"

    def extract():
        return ydl_client.extract_info(watch_url, download=False, process=True)
    
    info = await asyncio.to_thread(extract)
    if not info:
        return watch_url
        
    stream_url = info.get("url")
    if not stream_url and info.get("formats"):
        audio_formats = [f for f in info["formats"] if f.get("vcodec") == "none"]
        stream_url = audio_formats[-1].get("url") if audio_formats else info["formats"][-1].get("url")
        
    return stream_url or watch_url

async def get_youtube_info(query: str):
    def extract():
        if query.startswith(("http://", "https://")):
            if "list=" in query:
                return ydl_playlist_client.extract_info(query, download=False)
            return ydl_client.extract_info(query, download=False, process=True)
        return ydl_search_client.extract_info(f"ytsearch1:{query}", download=False, process=True)

    info = await asyncio.to_thread(extract)
    if not info:
        return []

    if info.get("_type") == "playlist" and "entries" in info:
        entries = info["entries"]
        if not entries:
            return []
        
        if not query.startswith(("http://", "https://")):
            info = entries[0] # Grab first search result entry
        else:
            songs = []
            for entry in entries:
                if entry:
                    # FIX: Safely parse out the video ID and build a structurally correct watch URL
                    video_id = entry.get("id")
                    if video_id:
                        video_url = f"https://youtube.com{video_id}"
                    else:
                        video_url = entry.get("url") or entry.get("webpage_url")
                        
                    songs.append({
                        "url": video_url, 
                        "webpage_url": video_url,
                        "title": entry.get("title", "Unknown"),
                        "is_playlist_track": True
                    })
            return songs

    stream_url = info.get("url")
    if not stream_url and info.get("formats"):
        audio_formats = [f for f in info["formats"] if f.get("vcodec") == "none"]
        stream_url = audio_formats[-1].get("url") if audio_formats else info["formats"][-1].get("url")
    
    return [{
        "url": stream_url or info.get("webpage_url"),
        "webpage_url": info.get("webpage_url"),
        "title": info.get("title", "Unknown"),
        "is_playlist_track": False
    }]