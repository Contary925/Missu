import json
from PoS.src.embed import send_embed_with_buttons
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)

async def quest_menu(game_msg, message, player):
    title = f"**{player.name}'s quests:**"
    text = ""
    if player.quests == {}:
        text += "You don't have any quests accepted!"
        await message.channel.send(text, delete_after=10.0)
        return
    counter = 0
    for quest in player.quests:
        counter += 1
        text += f'\n[{counter}] {quest.capitalize()}'
    text += '\n[0] Go back'
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, len(player.quests)+1)
    if choice == 0:
        return
    await view_quest(game_msg, message, player, list(player.quests)[choice-1])

async def view_quest(game_msg, message, player, quest_name):
    title = f'Quest: {quest_name.capitalize()}'
    text = 'Progress:'
    quest = player.quests[quest_name]
    if 'kill' in quest["objectives"]:
        for target in quest["objectives"]["kill"]:
            text += f'\n- Kill {target}: {quest["progress"]["kill"][target]}/{quest["objectives"]["kill"][target]}'
    if 'collect' in quest["objectives"]:
        for target in quest["objectives"]["collect"]:
            text += f'\n- Collect {item_data[target]["name"]}: {player.inventory.get(target, 0)}/{quest["objectives"]["collect"][target]}'
    text += '\n[1] Abandon quest'
    text += '\n[0] Go back'
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, 2)
    match choice:
        case 0:
            return
        case 1:
            message.channel.send(f'Abandoned the quest "{quest_name.capitalize()}"!', delete_after = 10.0)
            del player.quests[quest_name]
            return