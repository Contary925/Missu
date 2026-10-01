from functions.music import music_queues
from classes.queue import Queue

async def get_link(client, message, content):
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if queue.current_song is None:
        return await message.channel.send('Nothing is currently playing!')
    link = queue.current_song["webpage_url"]
    await message.channel.send(link)
    return