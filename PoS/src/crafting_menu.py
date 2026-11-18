import json
with open('PoS/src/recipes/recipes.json') as f:
    recipes = json.load(f)
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)

def crafting_menu(player):
    print(f"-----------------------------------")
    print(f"Available items for crafting:")
    counter = 0
    for recipe in recipes:
        counter += 1
        print(f"-----------------------------------")
        print(f'[{counter}] {recipes[recipe]["output_quantity"]}x {item_data[recipe]["name"]}:')
        for material in recipes[recipe]["materials"]:
            print(f'- {recipes[recipe]["materials"][material]}x {item_data[material]["name"]}')
    print(f"-----------------------------------")
    print(f"[0] Go back")
    while True:
        choice = input("Choose an item you want to craft > ").strip()
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
    return player.craft(list(recipes)[choice-1])