# Missu

**Missu** is a personal Discord bot built with [discord.py](https://discordpy.readthedocs.io/). It combines music playback, playlists, automatic reactions and replies, AI chat, user interactions, and various utilities.

The bot is designed primarily for personal use.

## Features

- **Music playback** — search and play songs from YouTube, manage the queue, shuffle tracks, and repeat songs.
- **Playlists and favourites** — save tracks, organize them into personal playlists, and quickly add them to the queue.
- **Lyrics** — search for song lyrics using the Genius API.
- **AI chat** — interact with several AI models through OpenRouter, including DeepSeek with web search.
- **Automatic reactions and replies** — configure personal or global triggers for messages.
- **User interactions** — send interaction commands such as hugs, kisses, pats, and other actions to other users.
- **Personal aliases** — create shortcuts for frequently mentioned users and use them in interaction commands.
- **GIF management** — view and manage GIFs used by interaction commands.
- **Press F** — start a short community event where users can pay their respects.
- **Utilities** — random choice with custom probabilities, saved choice lists, and more.
- **GitHub synchronization** — automatically pull updates on startup and push local changes when requested.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- [Git](https://git-scm.com/)
- [FFmpeg](https://ffmpeg.org/) (required for music playback)
- A Discord bot application and token

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Contary925/Missu.git
   cd Missu
   ```

2. Install the project dependencies:

   ```bash
   uv sync
   ```

3. Install FFmpeg and make sure it is available in your system PATH.

4. Create a `.env` file in the project root:

   ```env
   DISCORD_TOKEN=your_discord_bot_token
   OPENROUTER_API_KEY=your_openrouter_api_key
   GENIUS_ACCESS_TOKEN=your_genius_access_token
   ```

   `DISCORD_TOKEN` is required. The other API keys are optional and enable their respective features.

5. Create `shared/ID.py` locally:

   ```python
   OWNER_ID = 123456789012345678
   ```

   Replace the example value with your Discord user ID. This file is intentionally excluded from the repository.

6. Enable the **Message Content Intent** in the Discord Developer Portal under your bot's settings.

## Running

Start the bot with:

```bash
uv run main.py
```

Missu will automatically attempt to pull the latest changes from the `main` branch on startup. Ignore this if you aren't using a Git remote.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `DISCORD_TOKEN` | Yes | Discord bot token |
| `OPENROUTER_API_KEY` | No | Enables AI commands |
| `GENIUS_ACCESS_TOKEN` | No | Enables lyrics search |

The bot owner is configured separately in `shared/ID.py` using `OWNER_ID`.

## Commands

All commands use the `uwu` prefix. The alternative prefix `уву` is also supported.

### Music

| Command | Description |
|---|---|
| `play [source]` | Play a YouTube search result, video, or playlist |
| `play [source] -select [count]` | Choose from multiple search results |
| `play np` | Add the currently playing song to the queue |
| `pause` / `resume` | Pause or resume playback |
| `skip` / `next` | Skip the current song |
| `stop` | Stop playback, clear the queue, and leave the voice channel |
| `queue` | Display the current queue |
| `queue remove [index]` | Remove a song from the queue |
| `push [index]` | Move a queued song to the front |
| `playnum [index]` | Immediately play a song from the queue |
| `shuffle` | Shuffle the queue |
| `repeat` | Repeat the current song |
| `link` / `ссылка` | Get the current song's link |

### Playlists and favourites

| Command | Description |
|---|---|
| `playlist create [name]` | Create a playlist |
| `playlist delete [name]` | Delete a playlist |
| `playlist add [name] [source]` | Add songs to a playlist |
| `playlist remove [name] [index]` | Remove a song from a playlist |
| `playlist show [name]` | Display a playlist |
| `playlist showall` | Display all your playlists |
| `playlist play [name]` | Add playlist songs to the queue |
| `playlist push [name]` | Add playlist songs to the front of the queue |
| `playlistdefault set [name]` | Set your default playlist |
| `favlist` | Display your favourites |
| `favlist add [source]` | Add a song to your favourites |
| `favlist remove [index]` | Remove a song from your favourites |
| `favlist clear` | Clear your favourites |
| `play favlist` / `playfav` | Add your favourites to the queue |

Playlist commands also support shorter forms such as `pl`, `pld`, `+`, and `-`.

### Lyrics

| Command | Description |
|---|---|
| `lyrics [song name]` | Search for lyrics using Genius |
| `lyrics np` / `текст` | Search for lyrics of the currently playing song |

### AI

| Command | Description |
|---|---|
| `ai [prompt]` / `ии [prompt]` | Send a prompt to an AI model |
| `ai_deep [prompt]` / `deepseek [prompt]` | Ask DeepSeek with web search enabled |

### User interactions

The following commands allow users to interact with one another:

- `hug`
- `kiss`
- `pat`
- `bite`
- `boop`
- `spank`
- `lick`
- `bonk`

Examples:

```text
uwu hug @User
uwu kiss @User
uwu pat @User
uwu bonk @User
```

Most interaction commands require a user mention. `boop` and `lick` do not require a target.

### Personal aliases

Aliases let you assign short names to users and use them instead of mentions in interaction commands.

| Command | Description |
|---|---|
| `alias add [name]=[mention]` | Create an alias |
| `alias remove [name]` | Remove an alias |
| `alias list` | Display your aliases |

Example:

```text
uwu alias add Missu=<@123456789012345678>
uwu hug Missu
```

Aliases are personal to each user.

### GIF management

GIFs are used by interaction commands.

| Command | Description |
|---|---|
| `gif list [type]` | Display GIFs of a specific type |
| `gif add [type] [url]` | Add a GIF (administrators only) |
| `gif remove [type] [index]` | Remove a GIF (administrators only) |

Supported types: `hug`, `pat`, `kiss`, `bite`, `lick`, `bonk`.

### Automatic reactions

| Command | Description |
|---|---|
| `react add [text] = [emoji]` | Add a personal automatic reaction |
| `react remove [text]` | Remove a personal reaction |
| `react list` | Display your reactions |
| `react add [text] = [emoji] all` | Add a global reaction (administrators only) |
| `react remove [text] all` | Remove a global reaction (administrators only) |
| `react listall` | Display global reactions |

The alias `reaction` can also be used instead of `react`.

### Automatic replies

| Command | Description |
|---|---|
| `reply add [text] = [response]` | Add a personal automatic reply |
| `reply remove [text]` | Remove a personal reply |
| `reply list` | Display your replies |
| `reply add [text] = [response] all` | Add a global reply (administrators only) |
| `reply remove [text] all` | Remove a global reply (administrators only) |
| `reply listall` | Display global replies |

### Miscellaneous

| Command | Description |
|---|---|
| `ping` | Check Missu's response time |
| `choose [items]` | Choose a random item |
| `choose [items with probabilities]` | Choose an item using custom probabilities |
| `choose create [name] = [items]` | Create a saved choice list |
| `choose add [name] [items]` | Add items to a saved list |
| `choose remove [name] [items]` | Remove items from a saved list |
| `choose show` | Display your saved lists |
| `f [name]` | Start a 15-second Press F event |

The `choose` command also has the aliases `gamba` and `gamble`.

### Administration

| Command | Description |
|---|---|
| `reboot` | Restart Missu |
| `perms set [user] [access_level]` | Change a user's access level |
| `gitpush` | Push local changes to GitHub |
| `shutdown` | Synchronize changes and shut down Missu |

Some administration commands are restricted to the bot owner. Others require administrator permissions.

## Help

For detailed command usage, run:

```text
uwu help
uwu help [category]
```

A Russian-language help system is also available:

```text
уву помощь
уву помощь [категория]
```

You can also use `уву хелп` or `уву справка` to open the Russian help.

## GitHub Synchronization

Missu includes a small Git-based synchronization workflow:

- `auto_git_pull.py` attempts to pull the latest changes from `origin/main` when the bot starts.
- `gitpush` uploads local changes to GitHub.
- `shutdown` attempts to synchronize local changes before shutting down.

The synchronization commands require a properly configured Git repository and working Git credentials. Ignore these if you aren't using a Git remote.

**Note:** the automatic push uses `git add .`, so make sure that sensitive files and local-only configuration are properly excluded through `.gitignore`.

## Notes

- This is a personal project, so some configuration files and credentials are intentionally not included in the repository.
- Music playback depends on external services and may be affected by changes to YouTube or yt-dlp.
- AI responses should be checked before relying on them, especially for important information.
- Personal aliases, reactions, replies, playlists, and favourites are stored separately for each user.