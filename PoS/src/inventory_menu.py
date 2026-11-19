import json
from PoS.src.embed import send_embed_with_buttons, send_embed_with_custom_buttons
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)

def header(player):
    items = player.inventory
    text = ""
    for item in items:
        text += f'\n{item_data[item]["name"].capitalize()}: {items[item]}'
    text += "\n\n[0] Go back"
    text += "\n[1] Use a consumable item"
    text += "\n[2] Equip an item"
    return text

async def inventory_menu(game_msg, player, message):
    title = f"**{player.name}'s inventory:**"
    while True:
        text = header(player)
        _, choice = await send_embed_with_buttons(game_msg, message, title, text, 3)
        match choice:
            case 0:
                return
            case 1:
                await consumable_menu(game_msg, player, message)
            case 2:
                await equipment_menu(game_msg, player, message)
        continue

async def consumable_menu(game_msg, player, message):
    consumable_items = {}
    items = player.inventory
    title = f"**{player.name}'s consumable items:**"
    text = ""
    counter = 0
    for item in items:
        if item_data[item]["type"] == "consumable":
            counter += 1
            consumable_items[item] = player.inventory[item]
            text += f'\n[{counter}] {item_data[item]["name"]} ({items[item]})'
    if consumable_items == {}:
        text += "\nYou don't have consumable items!"
        await send_embed_with_custom_buttons(game_msg, message, title, text, ["To Town"])
        return
    text += f"\n[0] Go back"
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, len(consumable_items)+1)
    consumable_items = list(consumable_items)
    res_text = player.use_item(consumable_items[choice-1])
    await message.channel.send(res_text, delete_after = 10.0)
    return

async def equipment_menu(game_msg, player, message):
    equipment = {}
    title = f"**{player.name}'s equipped items:**"
    text = ""
    for slot, item_id in player.equipment.items():
        if item_id and item_id in item_data:
            item_name = item_data[item_id]["name"]
            bonuses = item_data[item_id].get("stat_bonuses", {})
            bonus_str = " (" + ", ".join(f"+{v} {k}" for k, v in bonuses.items()) + ")" if bonuses else ""
            text += f"\n[{slot.capitalize()}]: {item_name}{bonus_str}"
        else:
            text += f"\n[{slot.capitalize()}]: <Empty>"
    items = player.inventory
    text += f"\n\n**{player.name}'s equipment:**"
    counter = 0
    for item in items:
        if item_data[item]["type"] == "equipment":
            counter += 1
            equipment[item] = player.inventory[item]
            text += f'\n[{counter}] {item_data[item]["name"]} ({items[item]})'
    if equipment == {}:
        text += "You don't have any equipment!"
        await send_embed_with_custom_buttons(game_msg, message, title, text, ["To Town"])
        return
    text += f"\n[0] Go back"
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, len(equipment)+1)
    equipment = list(equipment)
    res_text = player.equip(equipment[choice-1])
    await message.channel.send(res_text, delete_after = 10.0)
    return