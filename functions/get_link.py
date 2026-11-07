from functions.music import music_queues
from classes.queue import Queue
from functions.get_youtube_info import get_youtube_info

async def get_link(client, message, content):
    if content != "":
        query = content.strip()
        songs = await get_youtube_info(query)
        if len(songs) == 0:
            return await message.channel.send("Nothing found.")
        song = songs[0]
        return await message.channel.send(song["webpage_url"])
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if queue.current_song is None:
        return await message.channel.send('Nothing is currently playing!')
    link = queue.current_song["webpage_url"]
    await message.channel.send(link)
    return