import json
from PoS.src.embed import send_embed_with_buttons
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)

async def combat_items_menu(game_msg, player, message, title):
    text = ""
    items = player.inventory
    consumable_items = {}
    for item in items:
        if item_data[item]["type"] == "consumable":
            consumable_items[item] = player.inventory[item]
    if consumable_items == {}:
        text += "\nYou don't have any consumable items!"
        return text, False
    text += f"\nThe amount of items you've got is specified in ()."
    counter = 0
    for item in consumable_items:
        counter += 1 
        text += f"\n[{counter}] {item_data[item]["name"].capitalize()} ({consumable_items[item]})" 
    text += f"\n[0] Go back"
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, len(consumable_items)+1)
    if choice == 0:
        return "", False
    consumable_items = list(consumable_items)
    return player.use_item(consumable_items[choice-1])
