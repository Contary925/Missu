import json
from src.quests import quest_available, quests_menu, quest_available, quest_accept, quest_report, quest_check_completion
with open('src/NPC/npc_info.json') as f:
    npc_info = json.load(f)
with open('src/items/item_data.json') as f:
    item_data = json.load(f)

def merchant_menu(player, merchant: str):
    greet(merchant, player) 
    while True:
        print('[1] Buy items')
        print('[2] Sell items')
        print('[3] View quests')
        print('[0] Go back')
        choice = input('Choose an action > ')
        match choice:
            case '0':
                return
            case '1':
                buy_items_menu(player, merchant)
            case '2':
                sell_items_menu(player, merchant)
            case '3':
                quests_menu(player, merchant)
            case _:
                print("Invalid input! Please choose from the menu.")
                continue

def buy_items_menu(player, merchant):
    print(f"-----------------------------------")
    print(f"Money held: {player.inventory.get("gold_coin", 0)}")
    items = npc_info[merchant]["items"]
    counter = 0
    for item in items:
        counter += 1
        print(f"[{counter}]: {item_data[item]["name"]} ({round(2*item_data[item]["merchant_price"])})")
    print('[0] Go back')
    while True:
        choice = input('Select the item you want to buy > ')
        try:
            choice = int(choice)
            if not choice in range(0, counter+1):
                print("Invalid index! Please choose from the menu.")
                continue
            if choice == 0:
                return
            player.buy_item(items[choice-1])
            print(f"Money held: {player.inventory.get("gold_coin", 0)}")
            continue
        except Exception:
            print("Invalid index! Please choose from the menu.")
            continue

def sell_items_menu(player, merchant):
    print(f"-----------------------------------")
    print(f"Money held: {player.inventory.get("gold_coin", 0)}")
    items = list(player.inventory)
    if "gold_coin" in items:
        items.remove("gold_coin")
    counter = 0
    for item in items:
        counter += 1
        print(f"[{counter}]: {item_data[item]["name"]} ({round(item_data[item]["merchant_price"])} gold, held: {player.inventory[item]})")
    print('[0] Go back')
    while True:
        choice = input('Select the item you want to sell > ')
        try:
            choice = int(choice)
            if not choice in range(0, counter+1):
                print("Invalid index! Please choose from the menu.")
                continue
            if choice == 0:
                return
            player.sell_item(items[choice-1])
            print(f"Money held: {player.inventory.get("gold_coin", 0)}")
            continue
        except Exception:
            print("Invalid index! Please choose from the menu.")
            continue


def greet(merchant, player):
    print(f"-----------------------------------")
    print(f'==={merchant}===')
    print(f"-----------------------------------")
    print(f'Greetings, {player.name}!')
    print(npc_info[merchant]["greeting"])