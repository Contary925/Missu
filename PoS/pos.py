import json
from PoS.src.town_loop import town_loop
from PoS.src.entity_classes import Player
from PoS.src.construct_options import construct_options
from PoS.src.choose_option import choose_option
from PoS.src.embed import construct_embed, send_embed_with_buttons, send_embed_with_custom_buttons, change_name
from functions.check_owner import check_owner
from PoS.src.add.creation_menu import creation_menu

async def pos(client, message, content = ""):
    match content.strip.casefold():
        case "add":
            await add_to_game(client, message)
            return
    await run_game(client, message, content)
    return

async def run_game(client, message, content = ""):
    with open('PoS/saves/saves.json') as f: #make sure the data here is fresh!
        saves = json.load(f)
    title = "Welcome to Path of Steel!"
    text = ""
    id = str(message.author.id)
    if id in saves:
        name = saves[id].get("name", "Guest")
        text += f'Character data was found. Continue to play as {name}?'
        while True:
            game_msg, choice = await send_embed_with_custom_buttons(None, message, title, text, ["Exit", "Play"])
            match choice:
                case "Exit":
                    await message.channel.send("Goodbye!", delete_after = 10.0)
                    return
                case "Play":
                    await message.channel.send(f"Welcome back, {name}!", delete_after = 10.0)
                    player_data = saves[id]
                    break
    else:
        name = message.author.display_name
        text += f'Character data was not found. Start a new game as {name}?'
        while True:
            game_msg, choice = await send_embed_with_custom_buttons(None, message, title, text, ["Exit", "Play", "Change name"])
            match choice:
                case "Exit":
                    await message.channel.send("Goodbye!", delete_after = 10.0)
                    return
                case "Play":
                    await message.channel.send(f"Welcome, {name}!", delete_after=10.0)
                    player_data = {
                        "id": id,
                        "name": name
                    }
                    break
                case "Change name":
                    name = await change_name(game_msg, message, client)
                    if name is None:
                        await message.channel.send("Unable to set a new name...", delete_after = 10.0)
                        continue
                    player_data = {
                        "id": id,
                        "name": name
                    }
                    break
    player = Player(player_data)
    player.save_data()
    await town_loop(client, message, player, game_msg)

async def add_to_game(client, message):
    if not check_owner(message):
        return await message.channel.send("Only the owner can modify game data.")
    await creation_menu(message)