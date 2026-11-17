import discord
import asyncio
from classes.queue import Queue
from classes.user import User
from functions.cutword import cutword
from functions.music.get_youtube_info import get_youtube_info
from functions.music.select_youtube_song import select_youtube_song
from functions.check_confirmation import check_confirmation
import random
import tempfile
from functions.music.watchdog import (
    start_voice_watchdog, playback_text_channels, voice_recovery_channels, voice_disconnect_since, voice_retry_at, 
    voice_recovery_attempts, next_playback_generation, recovering_guilds, is_current_generation
)
music_queues = {} #warning: this is a global variable!
#it is, however, only being accessed and changed through guild_id keys.
#be careful when mutating it!
manual_skips = set()

async def play(client, message, content, pushing=False, pinning=False):
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    shuffle = content.casefold().endswith('-s')
    if shuffle:
        content = content[:-2].strip()
    select = '-select' in content.casefold()
    if select:
        query_lower, select_limit = content.casefold().split('-select', maxsplit=1)
        content = content[0:len(query_lower)]
        content = content.strip()
        select_limit = select_limit.strip()
        match select_limit.isdigit():
            case True:
                select_limit = int(select_limit)
                if select_limit < 1:
                    select_limit = 1
                if select_limit > 10:
                    select_limit = 10
            case False:
                select_limit = 5
    if content == "favlist":
        return await play_favlist(message, shuffle, pushing, pinning)
    if content.strip().casefold().startswith("everything") or content.strip().startswith("all"):
        excluded = (content.strip()+" ").split(" ", maxsplit=1)[1] #only cuts off an "everything" or an "all"
        #the extra space is to ensure splitting works. It's harmless because all excluded items will be further stripped
        return await play_all_saved_songs(client, message, excluded, shuffle, pushing, pinning)    
    process_message = None
    if select:
        process_message, songs = await select_youtube_song(
        client,
        message,
        content,
        select_limit
        )   
        if not songs: #error message already handled by select_youtube_song
            return
    else:
        match content.strip():
            case 'np':
                queue = music_queues.setdefault(message.guild.id, Queue())
                songs = [queue.current_song]
                if songs == [None]:
                    return await message.channel.send('❌ Nothing is currently playing!')
            case _:
                process_message = await message.channel.send("Searching for your song...")
                songs = await get_youtube_info(content)
        if not songs:
            await message.channel.send(
                f"❌ Couldn't find anything for **{content}**."
            )
            if process_message:
                await process_message.delete()
            return
    await add_and_play(message, songs, process_message, shuffle, pushing, pinning)



async def skip(client, message, auto=False):
    log_voice_state("before command", message.guild.voice_client)
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    if not auto:
        await message.channel.send("Skipping...")
    guild_id = message.guild.id
    if voice_client.is_playing() or voice_client.is_paused():
        manual_skips.add(guild_id)
    voice_client.stop()

async def stop(client, message, content):
    log_voice_state("before command", message.guild.voice_client)

    guild_id = message.guild.id
    voice_client = message.guild.voice_client
    queue = music_queues.get(guild_id)

    session_exists = (
        voice_client is not None
        or queue is not None
        or guild_id in recovering_guilds
        or guild_id in voice_recovery_channels
    )

    if not session_exists:
        await message.channel.send("❌ Currently not playing anything!")
        return

    # Invalidate all pending playback and recovery operations.
    next_playback_generation(guild_id)
    manual_skips.discard(guild_id)

    await message.channel.send("Stopping...")

    voice_client = message.guild.voice_client
    if voice_client is not None:
        await voice_client.disconnect(force=True)
    playback_text_channels.pop(guild_id, None)
    voice_recovery_channels.pop(guild_id, None)
    voice_disconnect_since.pop(guild_id, None)
    voice_retry_at.pop(guild_id, None)
    voice_recovery_attempts.pop(guild_id, None)
    music_queues.pop(guild_id, None)

async def queue(client, message, content):
    if content.startswith('remove'):
        content = cutword(content, 'remove').strip()
        match content:
            case 'last':
                index = 'last'
            case _:
                if not content.isdigit():
                    return
                index = int(content)
        guild_id = message.guild.id
        queue = music_queues.setdefault(guild_id, Queue())
        if index == 'last':
            index = len(queue.songs)+1
        if index < 1:
            return await message.channel.send(f"❌ Incorrect index!")
        if len(queue.songs)+1 < index:
            return await message.channel.send(f"❌ No song number **{index}** in the queue!")
        if index == 1:
            return await message.channel.send(f"❌ This song is already playing! You can use a skip command if you want to skip it.")
        queue.songs.pop(index-2)
        return await message.channel.send(f"✅ Removed song number **{index}** from the queue!")
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    page = 0
    total_songs = len(queue.songs) + (1 if queue.current_song is not None else 0)
    total_pages = (total_songs + 19) // 20
    text = queue.show(page)
    sent_message = await message.channel.send(text)
    if total_pages <= 1:
        return
    await sent_message.add_reaction('⬅️')
    await sent_message.add_reaction('➡️')
    def check(reaction, reactor):
        return (
            reactor.id == message.author.id
            and reaction.message.id == sent_message.id
            and str(reaction.emoji) in ('⬅️', '➡️')
        )
    while True:
        try:
            reaction, reactor = await client.wait_for(
                'reaction_add',
                timeout=60.0,
                check=check
            )
        except asyncio.TimeoutError:
            break
        if str(reaction.emoji) == '➡️':
            if page < total_pages - 1:
                page += 1
            else:
                page = 0
            await sent_message.edit(
                content=queue.show(page)
            )
        elif str(reaction.emoji) == '⬅️':
            if page > 0:
                page -= 1
            else:
                page = total_pages - 1

            await sent_message.edit(
                content=queue.show(page)
            )
        await sent_message.remove_reaction(
            reaction.emoji,
            reactor
        )

async def pause(client, message):
    log_voice_state("before command", message.guild.voice_client)
    voice_client = message.guild.voice_client
    if voice_client is None or not voice_client.is_playing():
        await message.channel.send("❌ Nothing is currently playing!")
        return
    voice_client.pause()
    await message.channel.send("✅ Paused.")

async def resume(client, message):
    log_voice_state("before command", message.guild.voice_client)
    voice_client = message.guild.voice_client
    if voice_client is None or not voice_client.is_paused():
        await message.channel.send("❌ Nothing is currently paused!")
        return
    voice_client.resume()
    await message.channel.send("✅ Resuming.")

async def shuffle(client, message):
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    queue.shuffle()
    return await message.channel.send("✅ Shuffled successfully!")

async def push(client, message, content, auto=False):
    if content.isdigit():
        index = int(content)
    else:
        match content:
            case 'last':
                index = 'last'
            case _:
                if auto:
                    return False
                await play(client, message, content, pushing=True)
                return True
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return False
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if index == 'last':
        index = len(queue.songs)+1
    if index < 1:
        await message.channel.send(f"❌ Incorrect index!")
        return False
    if len(queue.songs)+1 < index:
        await message.channel.send(f"❌ No song number **{index}** in the queue!")
        return False
    if index == 2 and not auto:
        await message.channel.send(f"❌ Song number **{index}** is already playing next!")
        return False
    if index == 1:
        await message.channel.send(f"❌ This song is already playing!")
        return False
    queue.push(index)
    if not auto:
        return await message.channel.send(f"✅ Pushed song number {index} to play next!")
    return True

async def playnum(client, message, content):
    pushed = await push(client, message, content, auto=True)
    if pushed:
        await skip(client, message, auto=True)

async def favlist(client, message, content):
    match content:
        case '':
            user = User(message.author.id)
            page = 0
            total_pages = (len(user.favlist) + 19) // 20
            text = user.show_favlist(page)
            sent_message = await message.channel.send(text)
            if total_pages <= 1:
                return
            await sent_message.add_reaction('⬅️')
            await sent_message.add_reaction('➡️')
            def check(reaction, reactor):
                return (
                    reactor.id == message.author.id
                    and reaction.message.id == sent_message.id
                    and str(reaction.emoji) in ('⬅️', '➡️')
                )
            while True:
                try:
                    reaction, reactor = await client.wait_for(
                        'reaction_add',
                        timeout=60.0,
                        check=check
                    )
                except asyncio.TimeoutError:
                    break
                if str(reaction.emoji) == '➡️':
                    if page < total_pages - 1:
                        page += 1
                        await sent_message.edit(
                            content=user.show_favlist(page)
                        )
                elif str(reaction.emoji) == '⬅️':
                    if page > 0:
                        page -= 1
                        await sent_message.edit(
                            content=user.show_favlist(page)
                        )
                await sent_message.remove_reaction(
                    reaction.emoji,
                    reactor
                )
        case 'clear':
            user = User(message.author.id)
            user.clear_favlist()
            return await message.channel.send('✅ Favlist cleared!')
    if content.startswith('add'):
        await add_to_favlist(message, cutword(content, 'add'))
    if content.startswith('remove'):
        await remove_from_favlist(message, cutword(content, 'remove'))
    if content.startswith('browse'):
        await view_users_favlist(client, message, cutword(content, 'browse'))

async def add_to_favlist(message, content):
    if content.strip() == 'np':
        guild_id = message.guild.id
        queue = music_queues.setdefault(guild_id, Queue())
        songs = [queue.current_song]
        if songs == [None]:
            return await message.channel.send('❌ Nothing is currently playing!')
    else:
        await message.channel.send("Searching for your song...")
        songs = await get_youtube_info(content)
    if not songs:
        await message.channel.send(
            f"❌ Couldn't find anything for **{content}**."
        )
        return
    song = songs[0]
    user = User(message.author.id)
    match user.add_to_favlist(
        {
            "url": song["webpage_url"],
            "title": song["title"]
        }
    ):
        case 0:
            return await message.channel.send('❌ The song is already in your favlist!')
        case 1:
            return await message.channel.send(f'✅ Added song **{song["title"].replace('*', '\\*')}** to your favlist!')

async def remove_from_favlist(message, content):
    if not content.isdigit():
        return await message.channel.send("❌ Incorrect index! Specify the index of the song in favlist which you want to remove.")
    index = int(content)
    user = User(message.author.id)
    removed = user.remove_from_favlist(index)
    match removed:
        case 'Song with index not found':
            return await message.channel.send("❌ Song with the specified index was not found!")
        case _:
            return await message.channel.send(f"✅ Removed the song **{removed}** from your favlist!")
    

async def play_favlist(message, shuffle=False, pushing=False, pinning=False):
    if " -s " in message.content or message.content.endswith(" -s"):
        shuffle=True
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    user = User(message.author.id)
    favlist = user.favlist
    if favlist == {}:
        return await message.channel.send('❌ Your favlist is empty!')
    process_message = await message.channel.send('Processing songs in background...')
    songs = []
    for song_url in favlist:
        songs.append({
           "title": favlist[song_url],
            "webpage_url": song_url 
        })
    await add_and_play(message, songs, process_message, shuffle, pushing, pinning)

async def repeat(message, content):
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if queue.current_song is None:
        return await message.channel.send("❌ Nothing is currently playing!")
    count = int(content) if content.strip().isdigit() and int(content) !=0 else 1
    if count > 20:
        await message.channel.send("Slow down a little...")
        count = 10
    for _ in range(count):
        queue.repeat_current()
    match count:
        case 1:
            return await message.channel.send("✅ The current song will play once again!")
        case _:
            return await message.channel.send(f"✅ The current song will play {count} more times!")

#helper functions


async def play_song(voice_client, song, queue, text_channel, refresh_attempted=False):
    if not song:
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(
            handle_song_finished(voice_client, queue, text_channel),
            loop
        )
        return
    guild_id = voice_client.guild.id
    playback_text_channels[guild_id] = text_channel
    generation = next_playback_generation(guild_id)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    FFMPEG_OPTIONS = {
        'before_options': (
            '-reconnect 1 '
            '-reconnect_streamed 1 '
            '-reconnect_delay_max 2 '
            f'-headers "User-Agent: {user_agent}\r\n" '
            '-rw_timeout 5000000 '
            '-max_delay 500000 '
            '-rtbufsize 15M'
        ),
        'options': (
            '-vn '
            '-b:a 192k '
        )
    }
    stderr_file = tempfile.TemporaryFile(mode="w+t", encoding="utf-8")
    try:
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                song["url"],
                stderr=stderr_file,
                **FFMPEG_OPTIONS
            ),
            volume=0.5
        )
    except Exception as e:
        stderr_file.close()
        print(f"Buffer initialization error: {e}")
        await text_channel.send(f"Error: {e}")

        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(
            handle_song_finished(
                voice_client,
                queue,
                text_channel,
                generation=generation
            ),
            loop
        )
        return
    loop = asyncio.get_running_loop()
    def playback_finished(error):
        if error:
            print(f"Playback error: {error}")
        # Read FFmpeg diagnostics after the process has finished.
        stderr_file.flush()
        stderr_file.seek(0)
        ffmpeg_output = stderr_file.read()
        stderr_file.close()
        asyncio.run_coroutine_threadsafe(
            handle_song_finished(
                voice_client,
                queue,
                text_channel,
                song,
                ffmpeg_output,
                refresh_attempted,
                generation
            ),
            loop
        )
    voice_client.play(source, after=playback_finished)
    if not refresh_attempted:
        await text_channel.send(
            f"Playing **{song.get('title', 'Unknown Title').replace('*', '\\*')}**"
        )



async def handle_song_finished(
    voice_client,
    queue,
    text_channel,
    song=None,
    ffmpeg_output="",
    refresh_attempted=False,
    generation=None
):
    guild_id = voice_client.guild.id
    if generation is not None and not is_current_generation(guild_id, generation):
        print(f"[MUSIC] Ignoring stale playback callback for guild {guild_id}")
        return
    # A user explicitly requested a skip.
    if guild_id in manual_skips:
        manual_skips.discard(guild_id)
    # Detect an expired or otherwise rejected YouTube stream URL.
    elif "403 Forbidden" in ffmpeg_output:
        if not refresh_attempted and song and song.get("webpage_url"):
            print(f"HTTP 403 detected for: {song.get('title')}")
            try:
                refreshed = await get_youtube_info(song["webpage_url"])
                if generation is not None and not is_current_generation(guild_id, generation):
                    print(f"[MUSIC] Playback generation changed during URL refresh")
                    return
            except Exception as e:
                print(f"Failed to refresh YouTube URL: {e}")
                refreshed = []
            if refreshed and refreshed[0].get("url"):
                song["url"] = refreshed[0]["url"]
                print(f"Successfully refreshed URL for: {song.get('title')}")
                await play_song(
                    voice_client,
                    song,
                    queue,
                    text_channel,
                    refresh_attempted=True
                )
                return
        # Refresh failed or the refreshed URL also returned 403.
        print(f"Unable to recover playback for: {song.get('title') if song else 'Unknown'}")
        await text_channel.send(
            "❌ Couldn't refresh the audio stream. Skipping this song."
        )
    if generation is not None and not is_current_generation(guild_id, generation):
        return
    # Continue with the next song.
    next_song = queue.next()
    if next_song is None:
        await text_channel.send("Leaving the voice channel.")
        await voice_client.disconnect()
        return
    queue.set_current(next_song)
    await play_song(
        voice_client,
        next_song,
        queue,
        text_channel
    )

async def get_all_songs(user_id, excluded=[]):
    songs = []
    user = User(user_id)
    for song_url in user.favlist:
        song = {
            'title': user.favlist[song_url],
            'webpage_url': song_url
        }
        songs.append(song)
    for playlist in sorted(user.playlists, key=len, reverse=True):
        if playlist in excluded:
            continue
        for song_url in user.playlists[playlist]:
            song = {
                'title': user.playlists[playlist][song_url],
                'webpage_url': song_url
            }
            songs.append(song)
    return songs

async def now_playing(client, message, content):
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    song = queue.current_song
    if song == None:
        return await message.channel.send('❌ Nothing is currently playing!')
    return await message.channel.send(f"Now playing: **{song["title"]}**\n\n[Listen on YouTube]({song["webpage_url"]})")

async def view_users_favlist(client, message, mention):
    self = User(message.author.id)
    mention = mention.strip().casefold()
    if mention in self.alias :
        mention = self.alias[mention]
    try:
        other_id = mention.split("<@")[1].split(">")[0]
    except Exception as e:
        await message.channel.send("Could not find this user! Correctly mention a user or use alias.")
        return 0
    other_info = await client.fetch_user(other_id)
    other_name = other_info.display_name 
    other = User(other_id, other_name)
    if not other.playlists_visibility:
        return await message.channel.send("This user has not allowed others to view their playlists!")
    else:
        if other.favlist == {}:
            return await message.channel.send("This user's favlist is empty!")
        page = 0
        total_pages = (len(other.favlist) + 19) // 20
        text = other.show_favlist(page)
        sent_message = await message.channel.send(text)
        if total_pages <= 1:
            return
        await sent_message.add_reaction('⬅️')
        await sent_message.add_reaction('➡️')
        def check(reaction, reactor):
            return (
                 reactor.id == message.author.id
                 and reaction.message.id == sent_message.id
                and str(reaction.emoji) in ('⬅️', '➡️')
            )
        while True:
            try:
                reaction, reactor = await client.wait_for(
                    'reaction_add',
                    timeout=60.0,
                    check=check
                )
            except asyncio.TimeoutError:
                break
            if str(reaction.emoji) == '➡️':
                if page < total_pages - 1:
                    page += 1
                    await sent_message.edit(
                        content=other.show_favlist(page)
                    )
            elif str(reaction.emoji) == '⬅️':
                if page > 0:
                    page -= 1
                    await sent_message.edit(
                        content=other.show_favlist(page)
                    )
            await sent_message.remove_reaction(
                reaction.emoji,
                reactor
            )

async def pin(client, message, content):
    if content.isdigit():
        index = int(content)
    else:
        match content:
            case 'last':
                index = 'last'
            case _:
                return await play(client, message, content, pushing=True, pinning=True)
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if index == 'last':
        index = len(queue.songs)+1
    if index < 1:
        return await message.channel.send(f"❌ Incorrect index!")
    if len(queue.songs)+1 < index:
        return await message.channel.send(f"❌ No song number **{index}** in the queue!")
    if index == 1:
        return await message.channel.send(f"❌ This song is already playing!")
    queue.pin(index)
    queue.push(index)
    return await message.channel.send(f"✅ Pinned song number {index}!")

async def unpin(client, message, content):
    if content.isdigit():
        index = int(content)
    else:
        match content:
            case 'last':
                index = 'last'
            case _:
                return await message.channel.send("Usage: uwu unpin [song index in queue]")
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if index == 'last':
        index = len(queue.songs)+1
    if index < 1:
        return await message.channel.send(f"❌ Incorrect index!")
    if len(queue.songs)+1 < index:
        return await message.channel.send(f"❌ No song number **{index}** in the queue!")
    if index == 1:
        return await message.channel.send(f"❌ This song is already playing!")
    queue.unpin(index)
    return await message.channel.send(f"✅ Unpinned song number {index}!")

async def play_all_saved_songs(client, message, excluded="", shuffle=False, pushing=False, pinning=False):
    if excluded != "":
        excluded = [part.strip() for part in excluded.split('-') if part.strip()]
    songs = await get_all_songs(message.author.id, excluded)
    process_message = await message.channel.send(f'Unleash the chaos? This will be **{len(songs)} songs.**')
    if not await check_confirmation(message, client, process_message):
        await process_message.delete()
        return
    await add_and_play(message, songs, process_message, shuffle, pushing, pinning)

#a DRY helper to play songs
async def add_and_play(message, songs, process_message=None, shuffle=False, pushing=False, pinning=False):
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if shuffle:
        random.shuffle(songs)
    counter = 0
    added_songs = []
    for song in songs:
        if process_message:
            await process_message.edit(content=f'Processing songs in background... {counter+1}/{len(songs)}')
        if not song.get('url'):
            result = await get_youtube_info(song['webpage_url'])
            if not result:
                await message.channel.send(f"❌ The song **{song['title']}** is unavailable.")
                continue
            song = result[0]
        if pinning:
            song["pinned"] = True
        if pushing or pinning: #pinning new songs means pushing them too!
            queue.insert(counter, song)    
        else:
            queue.add(song)
        added_songs.append(song)
        counter += 1 
        if voice_client.is_playing():
            continue
        next_song = queue.next()
        queue.set_current(next_song)
        await play_song(
            voice_client,
            next_song,
            queue,
            message.channel,
        )
    if counter == 0:
        await message.channel.send("❌ Couldn't add any songs.")
        return
    elif counter == 1:
        await message.channel.send(f"✅ Added **{added_songs[0]['title'].replace('*', '\\*')}** to the queue.")
    else:
        await message.channel.send(f"✅ Added **{counter} songs** to the queue.")
    if process_message:
        await process_message.delete()
    if voice_client.is_playing():
            return
    next_song = queue.next()
    queue.set_current(next_song)
    await play_song(
        voice_client,
        next_song,
        queue,
        message.channel,
    )



#debug helper
def log_voice_state(label, voice_client):
    if voice_client is None:
        print(f"[VOICE] {label}: VoiceClient is None")
        return
    try:
        print(
            f"[VOICE] {label}: "
            f"connected={voice_client.is_connected()}, "
            f"playing={voice_client.is_playing()}, "
            f"paused={voice_client.is_paused()}, "
            f"latency={voice_client.latency}, "
            f"average_latency={voice_client.average_latency}, "
            f"channel={voice_client.channel}"
        )
    except Exception as e:
        print(f"[VOICE] {label}: diagnostic error: {e}")