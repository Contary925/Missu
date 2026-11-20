import json
from PoS.src.quests import quest_available, quests_menu, quest_available, quest_accept, quest_report, quest_check_completion
from PoS.src.embed import send_embed_with_buttons
with open('PoS/src/NPC/npc_info.json') as f:
    npc_info = json.load(f)
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)

async def merchant_menu(game_msg, message, player, merchant_name: str):
    text, title  = greet(merchant_name, player) 
    text += '\n\n[1] Buy items'
    text += '\n[2] Sell items'
    text += '\n[3] View quests'
    text += '\n[0] Go back'
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, 4)
    match choice:
        case 0:
            return
        case 1:
            await buy_items_menu(game_msg, message, player, merchant_name)
        case 2:
            await sell_items_menu(game_msg, message, player, merchant_name)
        case 3:
            await quests_menu(game_msg, message, player, merchant_name)

async def buy_items_menu(game_msg, message, player, merchant_name):
    text = ""
    title = f"**{merchant_name.capitalize()}'s shop**"
    items = npc_info[merchant_name]["items"]
    counter = 0
    items_list = ""
    for item in items:
        counter += 1
        items_list += f"\n[{counter}] {item_data[item]["name"].capitalize()} ({round(2*item_data[item]["merchant_price"])})"
    while True:
        header = f"\nMoney held: {player.inventory.get("gold_coin", 0)}\n" + items_list + "\n[0] Go back"
        _, choice = await send_embed_with_buttons(game_msg, message, title, header+text, len(items)+1)
        if choice == 0:
            return
        text += player.buy_item(items[choice-1])[0]
        continue

async def sell_items_menu(game_msg, message, player, merchant_name):
    title = f"**Items available for sale**"
    text = ""
    while True:
        header = f"Money held: {player.inventory.get("gold_coin", 0)}\n"
        items_list = ""
        items = list(player.inventory)
        if "gold_coin" in items:
            items.remove("gold_coin")
        counter = 0
        for item in items:
            counter += 1
            items_list += f"\n[{counter}]: {item_data[item]["name"]} ({round(item_data[item]["merchant_price"])} gold, held: {player.inventory[item]})"
        header += items_list
        header += '\n[0] Go back'
        _, choice = await send_embed_with_buttons(game_msg, message, title, header+text, len(items)+1)
        if choice == 0:
            return
        text += player.sell_item(items[choice-1])[0]
        continue


def greet(merchant_name, player):
    text = ""
    title = f'**{merchant_name.capitalize()}**'
    text += f'\nGreetings, {player.name}!'
    text += npc_info[merchant_name]["greeting"]
    return text, title