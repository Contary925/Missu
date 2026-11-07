from classes.user import User
from functions.get_youtube_info import get_youtube_info
from classes.queue import Queue
from functions.music import get_stream_url, play_song
import random
import asyncio
from functions.music import music_queues #warning: this is a global variable!
#it is, however, only being accessed and changed through guild_id keys.
#be careful when mutating it!

async def playlist(client, message, content):
    [command, args] = (content+' ').split(' ', maxsplit=1) #an extra space prevents breaking if there's only one space
    command = command.strip()
    args = args.strip()
    match command:
        case 'create':
            await playlist_create(client, message, args)
        case 'delete':
            await playlist_delete(client, message, args)
        case 'add' | '+':
            await add_to_playlist(client, message, args)
        case 'remove' | '-':
            await remove_from_playlist(client, message, args)
        case 'play':
            await play_playlist(client, message, args)
        case 'push':
            await push_playlist(client, message, args)
        case 'show':
            await show_playlist(client, message, args)
        case 'showall':
            await show_playlists(client, message)
        case 'visibility': 
            await set_playlists_visibility(message, args)
        case 'browse':
            await view_users_playlists(client, message, args)
        case 'copy':
            await copy_users_playlist(client, message, args)
        case _:
            await message.channel.send('Invalid syntax! Usage: uwu playlist [create/delete/add/remove/play] [arguments]. Example: uwu playlist create Three Days Grace')

async def playlist_default(client, message, content):
    user = User(message.author.id)
    if content.strip().startswith('set'): 
        user.default_playlist = content.split('set')[1].strip()
        user.data_update('default_playlist', content.split('set')[1].strip())  
        await message.channel.send(f'Done setting your default playlist to **{content.split('set')[1].strip()}**.')
    else:
        if user.default_playlist is None:
            return await message.channel.send('Default playlist not set!')
        if not user.default_playlist in user.playlists:
            return await message.channel.send(f'Playlist **{user.default_playlist}** is set as default but does not exist!')
        [command, args] = (content+' ').split(' ', maxsplit=1) #an extra space prevents breaking if there's only one space
        command = command.strip()
        args = args.strip()
        content = command + ' ' + user.default_playlist + ' ' + args
        await playlist(client, message, content)

async def playlist_create(client, message, args):
    user = User(message.author.id)
    match await user.playlist_create(args):
        case True:
            await message.channel.send(f'✅ Successfully created the playlist "{args}"!')
        case False:
            await message.channel.send(f'❌ A playlist "{args}" already exists!')

async def playlist_delete(client, message, args):
    user = User(message.author.id)
    match await user.playlist_delete(args):
        case True:
            await message.channel.send(f'✅ Successfully deleted the playlist "{args}"!')
        case False:
            await message.channel.send(f'❌ No playlist "{args}" found.')

async def add_to_playlist(client, message, args):
    user = User(message.author.id)
    song_name = None
    playlists = user.playlists
    for playlist in playlists:
        if args.startswith(playlist):
            song_name = args.split(playlist, maxsplit=1)[1]
            break
    if song_name is None:
        return await message.channel.send('❌ Incorrect playlist name!')
    if song_name.strip() == 'np':
        guild_id = message.guild.id
        queue = music_queues.setdefault(guild_id, Queue())
        songs = [queue.current_song]
        if songs == [None]:
            return await message.channel.send('❌ Nothing is currently playing!')
    else:
        song_name = song_name.strip()
        await message.channel.send('Searching for your song...')
        songs = await get_youtube_info(song_name)
    count = 0
    for song in songs:
        count += 1
        await user.add_to_playlist(playlist, song)
    match count:
        case 0:
            return await message.channel.send("❌ Couldn't find your song...")
        case 1:
            title = song["title"]
            return await message.channel.send(f'✅ Added the song **{title.replace('*', '\\*')}** to playlist **{playlist}**!')
        case _:
            return await message.channel.send(f'✅ Added {count} songs to playlist **{playlist}**!')

async def remove_from_playlist(client, message, args):
    user = User(message.author.id)
    index = None
    playlists = user.playlists
    for playlist in playlists:
        if args.startswith(playlist):
            index = args.split(playlist, maxsplit=1)[1]
            break
    if index is None:
        return await message.channel.send('❌ Incorrect playlist name!')
    index = index.strip()
    if (
        not index.isdigit()
        or int(index) < 1
        or int(index) > len(user.playlists[playlist])
    ):
        return await message.channel.send("❌ Invalid index!")
    song_title = await user.remove_from_playlist(playlist, int(index))
    return await message.channel.send(f'✅ Removed the song "{song_title.replace('*', '\\*')}" from the playlist "{playlist}"!')
    

async def play_playlist(client, message, args):
    shuffle = False
    if args.endswith('-s'):
        shuffle = True
        args = args[:-2].strip()
    user = User(message.author.id)
    if not args in user.playlists:
        return await message.channel.send(f'❌ Cannot find playlist "{args}"!')
    playlist = user.playlists[args]
    if playlist == {}:
        return await message.channel.send(f'❌ The playlist is empty!')
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if shuffle:
        songs = list(playlist.items())
        random.shuffle(songs)
        playlist = dict(songs)
    count = 0
    process_message = await message.channel.send('Processing songs in background...')
    for processed, song_url in enumerate(playlist, start=1):
        process_message = await process_message.edit(content=f'Processing songs in background... {processed}/{len(playlist)}')
        stream_url = await get_stream_url(song_url)
        if not stream_url:
            await message.channel.send(
                f"❌ Song unavailable: {playlist[song_url]}"
            )
            continue
        count += 1
        song = {
            "title": playlist[song_url],
            "url": stream_url,
            "webpage_url": song_url
        }
        queue.add(song)
        if count == 1:
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
    await process_message.delete()
    if count == 0:
        await message.channel.send("❌ Couldn't add any songs.")
        return
    elif count == 1:
        await message.channel.send("✅ Added one song to the queue.")
    else:
        await message.channel.send(
            f"✅ Added **{count} songs** to the queue."
        )
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

async def push_playlist(client, message, args):
    shuffle = False
    if args.endswith('-s'):
        shuffle = True
        args = args[:-2].strip()
    user = User(message.author.id)
    if not args in user.playlists:
        return await message.channel.send(f'❌ Cannot find playlist "{args}"!')
    playlist = user.playlists[args]
    if playlist == {}:
        return await message.channel.send(f'❌ The playlist is empty!')
    if message.author.voice is None:
        await message.channel.send(
            "❌ You must be in a voice channel to use this command!"
        )
        return
    channel = message.author.voice.channel
    voice_client = message.guild.voice_client
    if voice_client is not None:
        await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()
    guild_id = message.guild.id
    queue = music_queues.setdefault(guild_id, Queue())
    if shuffle:
        songs = list(playlist.items())
        random.shuffle(songs)
        playlist = dict(songs)
    count = 0
    process_message = await message.channel.send('Processing songs in background...')
    for processed, song_url in enumerate(playlist, start=1):
        process_message = await process_message.edit(content=f'Processing songs in background... {processed}/{len(playlist)}')
        stream_url = await get_stream_url(song_url)
        if not stream_url:
            await message.channel.send(
                f"❌ Song unavailable: {playlist[song_url]}"
            )
            continue
        count += 1
        song = {
            "title": playlist[song_url],
            "url": stream_url,
            "webpage_url": song_url
        }
        queue.insert(count-1, song)  
        if count == 1:
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
    await process_message.delete()
    if count == 0:
        await message.channel.send("❌ Couldn't add any songs.")
        return
    elif count == 1:
        await message.channel.send("✅ Added one song to the queue.")
    else:
        await message.channel.send(
            f"✅ Added **{count} songs** to the queue."
        )
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

async def show_playlist(client, message, args):
    user = User(message.author.id, message.author.display_name)
    if args not in user.playlists:
        return await message.channel.send(
            f'❌ Cannot find playlist "{args}"!'
        )
    playlist = user.playlists[args]
    if not playlist:
        return await message.channel.send(
            f'❌ The playlist "{args}" is empty!'
        )
    songs = list(playlist.values())
    total_pages = (len(songs) + 19) // 20
    page = 0
    def get_page(page):
        start = page * 20
        end = start + 20
        text = f"Showing {user.name}\'s playlist **{args.strip()}**\n"
        for index, title in enumerate(
            songs[start:end],
            start=start + 1
        ):
            text += f'{index}. {title}\n'
        return text
    sent_message = await message.channel.send(get_page(page))
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
            page = (page + 1) % total_pages
            await sent_message.edit(
                content=get_page(page)
            )
        elif str(reaction.emoji) == '⬅️':
            page = (page - 1) % total_pages
            await sent_message.edit(
                content=get_page(page)
            )
        await sent_message.remove_reaction(
            reaction.emoji,
            reactor
        )

async def show_playlists(client, message):
    user = User(message.author.id)
    text = ''
    count = 0
    for playlist in user.playlists:
        count += 1
        text += f'{count}. **{playlist}**\n'
    if count == 0:
        return await message.channel.send("❌ You don't have any playlists!")
    return await message.channel.send(text)

async def set_playlists_visibility(message, args):
    user = User(message.author.id)
    match args.casefold():
        case "on":
            await user.set_playlists_visibility(True)
            return await message.channel.send("Done! Now other users can view your playlists.")
        case "off":
            await user.set_playlists_visibility(False)
            return await message.channel.send("Done! Now other users cannot view your playlists.")
        case _:
            return await message.channel.send("Invalid syntax! Usage: uwu playlist visibility on/off.")

async def view_users_playlists(client, message, args):
    self = User(message.author.id)
    pl_name = ""
    if "=" in args:
        [mention, pl_name] = args.split("=", maxsplit=1)
        mention = mention.strip().casefold()
        pl_name = pl_name.strip()
    else:
        mention = args.strip().casefold()
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
        if pl_name == "": #"view all playlists" mode
            text = ''
            count = 0
            for playlist in other.playlists:
                count += 1
                text += f'{count}. **{playlist}**\n'
            if count == 0:
                return await message.channel.send("❌ This user doesn't have any playlists!")
            return await message.channel.send(text)
        else: #"view this playlist" mode
            if pl_name not in other.playlists:
                return await message.channel.send(
                    f'❌ Cannot find playlist "{pl_name}"!'
                )
            playlist = other.playlists[pl_name]
            if not playlist:
                return await message.channel.send(
                    f'❌ The playlist "{pl_name}" is empty!'
                )
            songs = list(playlist.values())
            total_pages = (len(songs) + 19) // 20
            page = 0
            def get_page(page):
                start = page * 20
                end = start + 20
                text = f"Showing {other.name}\'s playlist **{pl_name.strip()}**\n"
                for index, title in enumerate(
                    songs[start:end],
                    start=start + 1
                ):
                    text += f'{index}. {title}\n'
                return text
            sent_message = await message.channel.send(get_page(page))
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
                    page = (page + 1) % total_pages
                    await sent_message.edit(
                        content=get_page(page)
                    )
                elif str(reaction.emoji) == '⬅️':
                    page = (page - 1) % total_pages
                    await sent_message.edit(
                        content=get_page(page)
                    )
                await sent_message.remove_reaction(
                    reaction.emoji,
                    reactor
                )

async def copy_users_playlist(client, message, args):
    self = User(message.author.id)
    pl_name = ""
    pl_alias = "" #defaults to pl_name if not set
    if "=" in args:
        [mention, pl_name_and_alias] = args.split("=", maxsplit=1)
        mention = mention.strip().casefold()
        if " AS " in pl_name_and_alias:
            [pl_name, pl_alias] = pl_name_and_alias.split(" AS ", maxsplit=1)
            pl_name = pl_name.strip()
            pl_alias = pl_alias.strip()
        else:
            pl_name = pl_name_and_alias.strip()
            pl_alias = pl_name
    else:
        await message.channel.send("Invalid syntax! Usage: uwu playlist copy mention = playlist name.")
    if mention in self.alias :
        mention = self.alias[mention]
    try:
        other_id = mention.split("<@")[1].split(">")[0]
    except Exception as e:
        await message.channel.send("Could not find this user! Correctly mention a user or use alias.")
        return 0
    if pl_alias in self.playlists:
        return await message.channel.send(f"You already have a playlist **{pl_alias}**! Delete it or alias it as something else!")
    other_info = await client.fetch_user(other_id)
    other_name = other_info.display_name 
    other = User(other_id, other_name)
    if not other.playlists_visibility:
        return await message.channel.send("This user has not allowed others to view their playlists!")
    else:
        if pl_name not in other.playlists:
            return await message.channel.send(
                f'❌ Cannot find playlist "{pl_name}"!'
            )
        playlist = other.playlists[pl_name]
        if not playlist:
            return await message.channel.send(
                f'❌ The playlist "{pl_name}" is empty!'
            )
        await self.playlist_create(pl_alias)
        counter = 0
        for song_url in playlist:
            song = {
                "title": playlist[song_url],
                "webpage_url": song_url
            }
            counter += 1
            await self.add_to_playlist(pl_alias, song)
        await message.channel.send(f"Created a playlist **{pl_alias}** and added {counter} songs!")