import asyncio
from functions.get_youtube_info import search_youtube_multiple, get_youtube_info

NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def format_duration(seconds):
    if seconds is None:
        return "Unknown duration"
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"

async def select_youtube_song(client, message, query, select_limit = 5):
    process_message = await message.channel.send(
        "Searching for songs..."
    )
    if select_limit > 10:
        select_limit = 10
    candidates = await search_youtube_multiple(query, limit=select_limit)
    if not candidates:
        await process_message.edit(
            content="No results found. Try another search."
        )
        return []
    lines = []
    for i, song in enumerate(candidates):
        title = song["title"]
        uploader = song.get("uploader") or "Unknown artist"
        duration = format_duration(song.get("duration"))
        lines.append(
            f"**{i + 1}. [{title}](<{song['webpage_url']}>)**Channel: {uploader} ({duration})"
        )
    results_message = await process_message.edit(
        content=(
            "**Select a song by reacting below:**\n\n"
            + "\n".join(lines)
        )
    )
    for emoji in NUMBER_EMOJIS[:len(candidates)]:
        await results_message.add_reaction(emoji)
    def check(reaction, user):
        return (
            user.id == message.author.id
            and reaction.message.id == results_message.id
            and str(reaction.emoji) in NUMBER_EMOJIS[:len(candidates)]
        )
    try:
        reaction, user = await client.wait_for(
            "reaction_add",
            timeout=60.0,
            check=check,
        )
    except asyncio.TimeoutError:
        await results_message.edit(
            content="Song selection timed out."
        )
        return []
    index = NUMBER_EMOJIS.index(str(reaction.emoji))
    selected = candidates[index]
    await results_message.edit(
        content=f"Selected **{selected['title']}**."
    )
    songs = await get_youtube_info(selected["webpage_url"])
    if not songs:
        await results_message.edit(
            content="Failed to load the selected song."
        )
        return results_message, []
    return results_message, songs