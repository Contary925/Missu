import os
import aiohttp
import discord

GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

async def find_lyrics(client, message, content):
    if not GENIUS_TOKEN:
        await message.channel.send("Genius API token is not configured.")
        return

    headers = {
        "Authorization": f"Bearer {GENIUS_TOKEN}"
    }

    params = {"q": content}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.genius.com/search",
            headers=headers,
            params=params,
        ) as response:
            if response.status != 200:
                await message.channel.send(
                    f"Genius API error: {response.status}"
                )
                return

            data = await response.json()

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
        color=discord.Color.gold(),
    )

    await message.channel.send(embed=embed)