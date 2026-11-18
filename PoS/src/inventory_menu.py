import json
with open('src/items/item_data.json') as f:
    item_data = json.load(f)

def inventory_menu(player):
    items = player.inventory
    print(f"-----------------------------------")
    print(f"{player.kind}'s inventory:")
    for item in items:
        print(f'{item_data[item]["name"]}: {items[item]}')
    while True:
        print(f"-----------------------------------")
        print("[0] Go back")
        print("[1] Use a consumable item")
        print("[2] Equip an item")
        choice = input("What do you want to do next? > ").strip()
        if not choice.isdigit():
            print('Invalid option! Choose from the menu.')
            continue
        choice = int(choice)
        match choice:
            case 0:
                return
            case 1:
                consumable_menu(player)
            case 2:
                equipment_menu(player)
            case _:
                print('Invalid option! Choose from the menu.')
                continue
        continue

def consumable_menu(player):
    consumable_items = {}
    print(f"-----------------------------------")
    items = player.inventory
    print(f"{player.kind}'s consumable items:")
    counter = 0
    for item in items:
        if item_data[item]["type"] == "Consumable":
            counter += 1
            consumable_items[item] = player.inventory[item]
            print(f'[{counter}]: {item_data[item]["name"]} ({items[item]})')
    if consumable_items == {}:
        print("You don't have consumable items!")
        return
    print(f"[0]. Go back")
    while True:
        choice = input("Choose an item you want to use > ").strip()
        if not choice.isdigit():
            print('Invalid item! Choose from the menu.')
            continue
        choice = int(choice)
        if choice > counter:
            print('Invalid item Choose from the menu.')
            continue
        if choice == 0:
            return False
        break
    consumable_items = list(consumable_items)
    player.use_item(consumable_items[choice-1])
    

def equipment_menu(player):
    equipment = {}
    print(f"-----------------------------------")
    print(f"{player.kind}'s equipped items:")
    for slot, item_id in player.equipment.items():
        if item_id and item_id in item_data:
            item_name = item_data[item_id]["name"]
            bonuses = item_data[item_id].get("stat_bonuses", {})
            bonus_str = " (" + ", ".join(f"+{v} {k}" for k, v in bonuses.items()) + ")" if bonuses else ""
            print(f"   [{slot.capitalize():<9}] : {item_name}{bonus_str}")
        else:
            print(f"   [{slot.capitalize():<9}] : <Empty>")
    print(f"-----------------------------------")
    items = player.inventory
    print(f"{player.kind}'s equipment:")
    counter = 0
    for item in items:
        if item_data[item]["type"] == "Equipment":
            counter += 1
            equipment[item] = player.inventory[item]
            print(f'[{counter}]: {item_data[item]["name"]} ({items[item]})')
    if equipment == {}:
        print("You don't have any equipment!")
        return
    print(f"[0]. Go back")
    while True:
        choice = input("Choose a piece of equipment you want to equip > ").strip()
        if not choice.isdigit():
            print('Invalid item! Choose from the menu.')
            continue
        choice = int(choice)
        if choice > counter:
            print('Invalid item Choose from the menu.')
            continue
        if choice == 0:
            return False
        break
    equipment = list(equipment)
    player.equip(equipment[choice-1])