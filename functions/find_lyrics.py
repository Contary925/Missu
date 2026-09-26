import os
import aiohttp
import discord
from bs4 import BeautifulSoup as bs
import re
import html as html_lib
import json
from classes.queue import Queue
from functions.music import music_queues #for the np argument to work

GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

async def find_lyrics(client, message, content):
    if not GENIUS_TOKEN:
        await message.channel.send("Genius API token is not configured.")
        return
    if content.strip() == 'np':
        content = await get_np(message)
        while '[' in content and ']' in content.split('[', maxsplit=1)[1]:
            content = content.split('[', maxsplit=1)[0]+content.split(']', maxsplit=1)[1] 
            #removing square brackets and everything in them - 
            #since videos tend to have those and it ruins search on genius.com
    await message.channel.send('Searching for the song...')
    headers = {
        "Authorization": f"Bearer {GENIUS_TOKEN}"
    }
    params = {"q": content}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.genius.com/search",
            headers=headers,
            params={"q": content},
        ) as response:
            body = await response.text()
            if response.status != 200:
                print("Genius status:", response.status)
                print("Genius response:", body[:1000])
                await message.channel.send(
                    f"Genius API error: {response.status}"
                )
                return
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print("Genius returned invalid JSON:")
                print(body[:1000])

                await message.channel.send(
                    "Genius returned an unexpected response."
                )
                return
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print("Invalid JSON:", body[:1000])

                await message.channel.send(
                    "Couldn't parse Genius response."
                )
                return
    hits = data.get("response", {}).get("hits", [])
    if not hits:
        await message.channel.send("Nothing found on Genius.")
        return
    song = hits[0]["result"]
    embed = discord.Embed(
        title=song["title"],
        url=song["url"],
        description=(
            f"**Artist:** {song['primary_artist']['name']}\n"
            f"[Read lyrics on Genius]({song['url']})"
        ),
        color =0xE8D1EA,
    )
    link_message = await message.channel.send(embed=embed)
    await send_text(message, song)

async def get_lyrics(url: str) -> str | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as response:

            if response.status != 200:
                print(
                    f"Genius lyrics error: {response.status}"
                )
                return None

            html = await response.text()
    soup = bs(html, "html.parser")
    containers = soup.select(
        '[data-lyrics-container="true"]'
    )
    if not containers:
        print("Genius lyrics containers not found.")
        return None
    lyrics_parts = []
    for container in containers:
        # Preserve line breaks between lyrics lines.
        for br in container.find_all("br"):
            br.replace_with("\n")
        text = container.get_text(separator="")
        if text.strip():
            lyrics_parts.append(text.strip())
    lyrics = "\n".join(lyrics_parts)
    lyrics = html_lib.unescape(lyrics)  
    lyrics = re.sub(
        r"^\s*\d+\s+Contributors.*?\bLyrics\s*",
        "",
        lyrics,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    lyrics = lyrics.strip()
    if 'yrics' in lyrics:
        lyrics = lyrics.split('yrics', maxsplit=1)[1]
    # Normalize whitespace while preserving stanza breaks.
    lines = [line.strip() for line in lyrics.splitlines()]
    result = []
    previous_empty = False
    for line in lines:
        if not line:
            if result and not previous_empty:
                result.append("")

            previous_empty = True
        else:
            result.append(line)
            previous_empty = False

    lyrics = "\n".join(result).strip()
    return lyrics or None

async def send_text(message, song):
    lyrics = await get_lyrics(song["url"])

    if not lyrics:
        await message.channel.send(
            "Couldn't retrieve lyrics from Genius."
        )
    while lyrics:
        if len(lyrics) <= 1900:
            chunk = lyrics
            lyrics = ""
        else:
            split_at = lyrics.rfind("\n", 0, 1900)
            if split_at == -1:
                split_at = 1900
            chunk = lyrics[:split_at]
            lyrics = lyrics[split_at:].lstrip("\n")
        await message.channel.send(f"```{chunk}```")

async def get_np(message):
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    song = queue.current_song
    if song == None:
        return await message.channel.send('❌ Nothing is currently playing!')
    return song['title']