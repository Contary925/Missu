import json
from PoS.src.town_loop import town_loop
from PoS.src.entity_classes import Player
from PoS.src.construct_options import construct_options
from PoS.src.choose_option import choose_option
from PoS.src.embed import construct_embed, send_embed_with_buttons

async def pos(client, message, content = ""):
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
        options = construct_options(["Play"], zero="Exit")
        text += f'Character data was found. Continue to play as {name}?\n\n{options}'
        while True:
            game_msg, choice = await send_embed_with_buttons(None, message, title, text, 2)
            match choice:
                case -1:
                    return #-1 = failed with error (likely a timeout)
                case 0:
                    await message.channel.send("Goodbye!", delete_after = 10.0)
                    return
                case 1:
                    await message.channel.send(f"Welcome back, {name}!", delete_after = 10.0)
                    player_data = saves[id]
                    break
    else:
        name = message.author.display_name
        options = construct_options(["Play", "Change name"], zero="Exit")
        text += f'Character data was not found. Start a new game as {name}?\n\n{options}'
        while True:
            game_msg, choice = await send_embed_with_buttons(None, message, title, text, 2)
            match choice:
                case -1:
                    return
                case 0:
                    await message.channel.send("Goodbye!", delete_after = 10.0)
                    return
                case 1:
                    await message.channel.send(f"Welcome, {name}!", delete_after=10.0)
                    player_data = {
                        "id": id,
                        "name": name
                    }
                    break
                case 2:
                    # TODO
                    continue
    player = Player(player_data)
    player.save_data()
    await town_loop(client, message, player, game_msg)