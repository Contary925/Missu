import json
with open('src/items/item_data.json') as f:
    item_data = json.load(f)

def combat_items_menu(player) -> bool:
    items = player.inventory
    consumable_items = {}
    for item in items:
        if item_data[item]["type"] == "Consumable":
            consumable_items[item] = player.inventory[item]
    if consumable_items == {}:
        print("You don't have any consumable items!")
        return False
    print(f"-----------------------------------")
    print(f"The amount of items you've got is specified in ().")
    counter = 0
    for item in consumable_items:
        counter += 1 
        print(f"[{counter}]: {item_data[item]["name"]} ({consumable_items[item]})") 
    print(f"[0]: Go back")
    while True:
        choice = input("Choose an item you want to use > ").strip()
        if not choice.isdigit():
            print('Invalid item! Choose from the menu.')
            continue
        choice = int(choice)
        if choice > counter:
            print('Invalid item! Choose from the menu.')
            continue
        if choice == 0:
            return False
        break
    consumable_items = list(consumable_items)
    return player.use_item(consumable_items[choice-1])
