
import functions.call_function


async def help(client, message, content):
    new_content = "help_" + content.strip().lower()
    called = await functions.call_function.call_function(
        client, message, new_content
    )

    if not called:
        text = """# Hello! I'm **Missu**, Kissu's personal Discord bot, written with discord.py.
Use **uwu** (or **уву**) as the command prefix.

**Music:** `play`, `pause`, `resume`, `skip`, `stop`, `queue`, `push`, `playnum`, `shuffle`, `repeat`, `link`.
→ `uwu help music`

**Playlists & favlist:** save, organize and play your music.
→ `uwu help playlists` | `uwu help favlist`

**Lyrics:** search for song lyrics using Genius.
→ `uwu help lyrics`

**AI:** chat with AI models or use DeepSeek with web search.
→ `uwu help ai`

**Interactions:** `hug`, `kiss`, `pat`, `bite`, `boop`, `spank`, `lick`, `bonk`.
→ `uwu help interactions`

**Aliases:** create personal shortcuts for mentions.
→ `uwu help alias`

**GIFs:** view and manage interaction GIFs.
→ `uwu help gifs`

**Reactions & replies:** automatic reactions and responses to messages.
→ `uwu help react` | `uwu help reply`

**Misc:** `ping`, `choose`, `gamba`, `gamble`, `f`.
→ `uwu help misc`

**Administration:** `perms`, `reboot`, `gitpush`, `shutdown`.
→ `uwu help admin`

Use **uwu help [category]** to learn more about a command category."""
        await message.channel.send(text)


async def help_alias(message):
    text = """# Personal aliases
Create shortcuts for mentions and use them in interaction commands.

1. `uwu alias add [name]=[mention]` — create an alias.
   Example: `uwu alias add Missu=<@1529029241566662746>`.
2. `uwu alias remove [name]` — remove an alias.
3. `uwu alias list` — show your aliases.

After creating an alias, you can use it instead of mentioning the user:
`uwu hug Missu`.

You must mention the user when creating an alias."""
    await message.channel.send(text)


async def help_interactions(message):
    text = """# Interact with other users!
Available interactions: `hug`, `kiss`, `pat`, `bite`, `boop`, `spank`, `lick`, `bonk`.

Examples:
- `uwu hug @User`
- `uwu kiss @User`
- `uwu pat @User`
- `uwu bite @User`
- `uwu bonk @User`
- `uwu spank @User`

Most interactions require mentioning another user. You can use a personal alias instead; see `uwu help alias`.

`uwu boop` and `uwu lick` do not require a target."""
    await message.channel.send(text)


async def help_gifs(message):
    text = """# Manage interaction GIFs
You can view GIFs for supported interactions:
`uwu gif list [type]`

Examples:
- `uwu gif list hug`
- `uwu gif list pat`
- `uwu gif list kiss`
- `uwu gif list bite`

Administrators can manage GIFs:
- `uwu gif add [type] [url]` — add a GIF.
- `uwu gif remove [type] [index]` — remove a GIF by its index.

Supported GIF types include `hug`, `pat`, `kiss`, `bite`, `lick` and `bonk`."""
    await message.channel.send(text)


async def help_react(message):
    text = """# Automatic reactions
1. `uwu react add [text] = [emoji]` — add a personal reaction.
   Example: `uwu react add hello = 👋`.
2. `uwu react remove [text]` — remove one of your reactions.
3. `uwu react list` — show your personal reactions.

**Global reactions (administrators only):**
4. `uwu react add [text] = [emoji] all` — add a reaction for everyone.
5. `uwu react remove [text] all` — remove a global reaction.
6. `uwu react listall` — show all global reactions.

You can also use `uwu reaction` instead of `uwu react`."""
    await message.channel.send(text)


async def help_reply(message):
    text = """# Automatic replies
1. `uwu reply add [text] = [response]` — add a personal automatic reply.
   Example: `uwu reply add good morning = Good morning!`.
2. `uwu reply remove [text]` — remove one of your replies.
3. `uwu reply list` — show your personal replies.

**Global replies (administrators only):**
4. `uwu reply add [text] = [response] all` — add a reply for everyone.
5. `uwu reply remove [text] all` — remove a global reply.
6. `uwu reply listall` — show all global replies.

Missu sends the configured response when a message contains the specified text."""
    await message.channel.send(text)


async def help_music(message):
    text = """# Play music from YouTube!
You must be in a voice channel to use these commands. If music is already playing, new songs will be added to the queue.

1. `uwu play [source]` — play songs from a YouTube search, video link or playlist link.
   Example: `uwu play Toram Online BGM - King Piton`.
   Add `-s` to shuffle playlist results: `uwu play [source] -s`.

2. `uwu play [prompt] -select [count]` — choose a song from search results instead of automatically playing the first match.
   By default, 5 results are shown; you can request up to 10.
   Example: `uwu play Toram Online BGM -select 10`.

3. `uwu pause` / `uwu resume` — pause or resume playback.
4. `uwu skip` (or `uwu next`) — skip the current song.
5. `uwu stop` — stop playback, disconnect and clear the queue.
6. `uwu queue` — view the queue. Use `uwu queue remove [index]` or `uwu queue remove last` to remove a song.
7. `uwu push [index]` — move a queued song to the next position.
   Use `uwu push last` to move the last song, or `uwu push [source]` to add new songs to the front of the queue.
8. `uwu playnum [index]` — play a queued song immediately. Also supports `last`.
9. `uwu shuffle` — shuffle the queue.
10. `uwu repeat` — play the current song again after it finishes.
11. `uwu link` (or `uwu ссылка`) — get a link to the currently playing song.
12. `uwu play np` — add the currently playing song to the queue.

Missu supports personal music collections:
- `uwu favlist` — manage your favourite songs.
- `uwu playlist` — create, manage and share playlists.

See `uwu help favlist` and `uwu help playlists` for details."""
    await message.channel.send(text)


async def help_favlist(message):
    text = """# Save songs to your favourite music list!
1. `uwu favlist` — view your favlist.
2. `uwu favlist add [source]` — add a song using a YouTube search prompt or video link. Playlist links are not supported.
3. `uwu favlist add np` — add the currently playing song.
4. `uwu favlist remove [index]` — remove a song by its index.
5. `uwu favlist clear` — clear your favlist.
6. `uwu play favlist` (or `uwu playfav`) — add all saved songs to the queue.
   Add `-s` to shuffle them: `uwu play favlist -s`.

**Explore other users' music:**
7. `uwu favlist browse [@user]` — view another user's favlist.
   Personal aliases can be used instead of mentions.

**Visibility settings:**
8. `uwu playlist visibility on` — allow other users to view your playlists and favlist.
9. `uwu playlist visibility off` — hide your playlists and favlist from other users.

Visibility is disabled by default. You can only browse another user's music if they have enabled visibility.

If music is already playing, saved songs will be added to the queue."""
    await message.channel.send(text)


async def help_playlists(message):
    text = """# Create and manage your own playlists!
1. `uwu playlist create [name]` — create a playlist.
2. `uwu playlist delete [name]` — delete a playlist.
3. `uwu playlist add [name] [source]` — add songs from a search, video link or playlist link.
   Use `np` to add the currently playing song.
   Short form: `uwu playlist + [name] [source]`.
4. `uwu playlist remove [name] [index]` — remove a song.
   Short form: `uwu playlist - [name] [index]`.
5. `uwu playlist show [name]` — view the contents of a playlist.
6. `uwu playlist showall` — view all your playlists.
7. `uwu playlist play [name]` — add playlist songs to the queue.
8. `uwu playlist push [name]` — add playlist songs to the front of the queue.
   Add `-s` to shuffle songs.

**Explore other users' playlists:**
9. `uwu playlist browse [@user]` — view another user's playlists.
   Add `= [playlist name]` to view a specific playlist:
   `uwu playlist browse @user = Three Days Grace`.
   Personal aliases can be used instead of mentions.

10. `uwu playlist copy [@user] = [playlist name]` — copy another user's playlist into your collection.
    You can specify a different name for your copy using `AS`:
    `uwu playlist copy @user = Three Days Grace AS My Favourite Songs`.

**Visibility settings:**
11. `uwu playlist visibility on` — allow other users to view your playlists and favlist.
12. `uwu playlist visibility off` — hide your playlists and favlist from other users.

Visibility is disabled by default. Other users cannot browse or copy your playlists unless you enable it.

**Default playlist:** use `uwu playlistdefault set [name]` to set one.
After that, you can omit the playlist name in supported commands:
`uwu playlistdefault play`, `uwu playlistdefault show`, `uwu playlistdefault add [source]`, etc.
Short alias: `uwu pld set [name]`.

Playlists are personal to each user. Browsing and copying another user's playlists does not modify their original collection."""
    await message.channel.send(text)


async def help_lyrics(message):
    text = """# Find song lyrics using Genius!
1. `uwu lyrics [song name]` — search for a song on Genius.
   Example: `uwu lyrics Never Too Late Three Days Grace`.
2. `uwu lyrics np` — search for lyrics of the currently playing song.

You can also use the Russian alias `uwu текст`.
Missu attempts to retrieve the lyrics automatically. If that fails, a link to the Genius page may still be available."""
    await message.channel.send(text)


async def help_ai(message):
    text = """# Chat with AI models!
1. `uwu ai [prompt]` (or `uwu ии [prompt]`) — send a prompt to an AI model.
2. `uwu ai_deep [prompt]` (or `uwu deepseek [prompt]`) — ask DeepSeek with web search enabled.
   You can also use `uwu дипсик`.

AI responses may take some time. Always verify important information and be careful with links provided by AI."""
    await message.channel.send(text)


async def help_misc(message):
    text = """# Miscellaneous commands

**Ping**
- `uwu ping` — check Missu's response time.

**Random choice**
- `uwu choose [item 1], [item 2], ...` — choose a random item.
  Example: `uwu choose pizza, sushi, burger`.
- You can assign probabilities: `uwu choose pizza 70%, sushi 20%, burger`.
  The remaining probability is distributed equally among items without a specified percentage.
- Aliases: `uwu gamba` and `uwu gamble`.

**Saved choice lists**
- `uwu choose create [name] = [items]` — create a reusable list.
- `uwu choose add [name] [items]` — add items to a saved list.
- `uwu choose remove [name] [items]` — remove items from a saved list.
- `uwu choose show` — view your saved lists.
- `uwu choose [name]` — choose from a saved list.
  You can temporarily add or remove items: `uwu choose dinner + pasta - sushi`.

**Pay respects**
- `uwu f [name]` — start a 15-second "Press F to pay respects" event.
  Users can react with 🇫 to pay their respects."""
    await message.channel.send(text)


async def help_admin(message):
    text = """# Administration commands

**Administrator:**
- `uwu reboot` — restart Missu.

**Bot owner:**
- `uwu perms set [user] [access_level]` — change a user's access level.
  Available levels: `default`, `admin` or `administrator`.
- `uwu gitpush` — upload local changes to GitHub.
- `uwu shutdown` — shut down Missu.

Use these commands with care!"""
    await message.channel.send(text)
