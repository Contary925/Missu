import asyncio
import yt_dlp

YTDL_OPTS = {
    'format': 'bestaudio/best',
    'skip_download': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': False,
    'youtube_include_dash_manifest': False, 
    "cookiefile": "cookies.txt",
}

async def get_stream_url(youtube_url: str) -> str | None:
    def extract():
        try:
            with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
                data = ydl.extract_info(youtube_url, download=False)
                if not data:
                    return None
                return data.get('url')
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return None

    return await asyncio.to_thread(extract)