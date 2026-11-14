
from collections.abc import Callable
import inspect

from functions.ping import ping
from functions.shutdown import shutdown
from functions.interactions import *
from functions.alias import *
from functions.cutword import cutword
from functions.help import *
from functions.help_ru import *
from functions.gifs import *
from auto_git_push import sync_to_github
from functions.perms import *
from functions.react import react, react_add, react_remove, react_list, react_listall
from functions.reply import reply, reply_add, reply_remove, reply_list, reply_listall
from functions.music.music import (
    play, stop, skip, queue, shuffle, pause, resume, push, playnum,
    favlist, repeat, play_favlist, now_playing, pin, unpin
)
from functions.press_F import press_F
from functions.music.playlists import playlist, playlist_default
from functions.music.find_lyrics import find_lyrics
from functions.music.get_link import get_link
from functions.ai_mode import ai_mode, ai_mode_deep
from functions.reboot import reboot
from functions.gamba import choose


function_map: dict[str, Callable] = {
    # General
    "ping": ping,

    # Administration
    "shutdown": shutdown,
    "gitpush": sync_to_github,
    "reboot": reboot,
    "perms": perms,
    "perms_set": perms_set,

    # Interactions
    "hug": hug,
    "kiss": kiss,
    "boop": boop,
    "bite": bite,
    "pat": pat,
    "spank": spank,
    "lick": lick,
    "bonk": bonk,

    # Personal aliases
    "alias": alias,
    "alias_add": alias_add,
    "alias_remove": alias_remove,
    "alias_list": alias_list,

    # GIFs
    "gif": gif,
    "gif_add": gif_add,
    "gif_remove": gif_remove,
    "gif_list": gif_list,

    # Reactions
    "react": react,
    "react_add": react_add,
    "react_remove": react_remove,
    "react_list": react_list,
    "react_listall": react_listall,

    # Automatic replies
    "reply": reply,
    "reply_add": reply_add,
    "reply_remove": reply_remove,
    "reply_list": reply_list,
    "reply_listall": reply_listall,

    # Music
    "play": play,
    "stop": stop,
    "skip": skip,
    "queue": queue,
    "shuffle": shuffle,
    "pause": pause,
    "resume": resume,
    "push": push,
    "playnum": playnum,
    "favlist": favlist,
    "repeat": repeat,
    "play_favlist": play_favlist,
    "playlist": playlist,
    "playlistdefault": playlist_default,
    "link": get_link,
    "now_playing": now_playing,
    "pin": pin,
    "unpin": unpin,

    # AI and lyrics
    "ai": ai_mode,
    "ai_deep": ai_mode_deep,
    "lyrics": find_lyrics,

    # Miscellaneous
    "f": press_F,
    "choose": choose,

    # English help
    "help": help,
    "help_alias": help_alias,
    "help_interactions": help_interactions,
    "help_gifs": help_gifs,
    "help_react": help_react,
    "help_reactions": help_react,
    "help_reply": help_reply,
    "help_music": help_music,
    "help_favlist": help_favlist,
    "help_playlists": help_playlists,
    "help_lyrics": help_lyrics,
    "help_ai": help_ai,
    "help_misc": help_misc,
    "help_admin": help_admin,

    # Russian help
    "help_ru": help_ru,
    "help_ru_music": help_ru_music,
    "help_ru_favlist": help_ru_favlist,
    "help_ru_playlists": help_ru_playlists,
    "help_ru_lyrics": help_ru_lyrics,
    "help_ru_ai": help_ru_ai,
    "help_ru_react": help_ru_react,
    "help_ru_reply": help_ru_reply,
    "help_ru_misc": help_ru_misc,
    "help_ru_admin": help_ru_admin,
    "help_ru_alias": help_ru_alias,
    "help_ru_interactions": help_ru_interactions,
    "help_ru_gifs": help_ru_gifs,
}


function_alias: dict[str, str] = {
    # Interaction aliases
    "хаг": "hug",
    "цем": "kiss",
    "кисс": "kiss",
    "тык": "boop",
    "кусь": "bite",
    "ням": "bite",
    "pet": "pat",
    "пат": "pat",
    "бонк": "bonk",
    "боньк": "bonk",
    "спанк": "spank",
    "шпаньк": "spank",
    "лизь": "lick",

    # GIF aliases
    "гиф": "gif",
    "gif_адд": "gif_add",
    "gif_удалить": "gif_remove",
    "gif_убрать": "gif_remove",
    "gif_ремув": "gif_remove",
    "gif_лист": "gif_list",
    "gif_список": "gif_list",

    # Command aliases
    "reaction": "react",
    "next": "skip",
    "playfav": "play_favlist",
    "ф": "f",
    "pl": "playlist",
    "pld": "playlistdefault",
    "np": "now_playing",
    "нп": "now_playing",
    "чтоиграет": "now_playing",
    "пин": "pin",
    "ии": "ai",
    "текст": "lyrics",
    "дипсик": "ai_deep",
    "deepseek": "ai_deep",
    "ссылка": "link",
    "gamble": "choose",
    "gamba": "choose",

    # Russian help entry points
    "хелп": "help_ru",
    "помощь": "help_ru",
    "справка": "help_ru",

    # Russian help section aliases
    "help_ru_музыка": "help_ru_music",
    "help_ru_фавлист": "help_ru_favlist",
    "help_ru_плейлисты": "help_ru_playlists",
    "help_ru_текст": "help_ru_lyrics",
    "help_ru_ии": "help_ru_ai",
    "help_ru_реакции": "help_ru_react",
    "help_ru_ответы": "help_ru_reply",
    "help_ru_разное": "help_ru_misc",
    "help_ru_админ": "help_ru_admin",
    "help_ru_алиасы": "help_ru_alias",
    "help_ru_взаимодействия": "help_ru_interactions",
    "help_ru_гиф": "help_ru_gifs",
}


async def call_function(client, message, content):
    if not content.strip():
        return 0
    pre_alias_command = content.split()[0].lower()
    command = pre_alias_command

    if pre_alias_command in function_alias:
        command = function_alias[pre_alias_command]

    print(f"Processing command: {command}")

    if command in function_map:
        content = cutword(content, pre_alias_command)

        args = {
            "client": client,
            "message": message,
            "content": content,
        }

        func = function_map[command]
        required_args = {
            name: args[name]
            for name in inspect.signature(func).parameters
            if name in args
        }

        await function_map[command](**required_args)
        return 1

    return 0
