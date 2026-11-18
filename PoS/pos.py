import json
from PoS.src.town_loop import town_loop
from PoS.src.entity_classes import Player
from PoS.src.construct_options import construct_options
from PoS.src.choose_option import choose_option

async def pos(client, message, content = ""):
    await message.channel.send("Reached Path Of Steel endpoint!")
    await run_game(client, message, content)
    return

async def run_game(client, message, content = ""):
    with open('PoS/saves/saves.json') as f: #make sure the data here is fresh!
        saves = json.load(f)
    text = 'Welcome to Path of Steel!\n\n'
    id = str(message.author.id)
    if id in saves:
        name = saves[id].get("name", "Guest")
        options = construct_options(["Play"], zero="Exit")
        text += f'Character data was found. Continue to play as {name}?\n\n{options}'
        game_msg = await message.channel.send(text)
        while True:
            choice = await choose_option(message.author, client, game_msg, num=2)
            match choice:
                case -1:
                    return #-1 = failed with error (likely a timeout)
                case 0:
                    await message.channel.send("Goodbye!")
                    return
                case 1:
                    await message.channel.send(f"Welcome back, {name}!")
                    player_data = saves[id]
                    break
    else:
        name = message.author.display_name
        options = construct_options(["Play", "Change name"], zero="Exit")
        text += f'Character data was not found. Start a new game as {name}?\n\n{options}'
        game_msg = await message.channel.send(text)
        while True:
            choice = await choose_option(message.author, client, game_msg, num=3)
            match choice:
                case -1:
                    return
                case 0:
                    await message.channel.send("Goodbye!")
                    return
                case 1:
                    await message.channel.send(f"Welcome, {name}!")
                    player_data = {
                        "id": id,
                        "name": name
                    }
                    break
                case 2:
                    # TODO
                    continue
    await game_msg.delete()
    player = Player(player_data)
    player.save_data()
    await message.channel.send("Ready to enter town loop!")
    await town_loop(client, message, player)