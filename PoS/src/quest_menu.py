import json
with open('src/items/item_data.json') as f:
    item_data = json.load(f)

def quest_menu(player):
    while True:
        print(f"-----------------------------------")
        if player.quests == {}:
            print("You don't have any quests accepted!")
            return
        counter = 0
        for quest in player.quests:
            counter += 1
            print(f'[{counter}] {quest}')
        print('[0] Go back')
        choice = input('Choose a quest > ')
        if not choice.isdigit():
            print("Invalid input! Please choose from the menu!")
            continue
        choice = int(choice)
        if choice == 0:
            return
        view_quest(player, list(player.quests)[choice-1])

def view_quest(player, quest_name):
    print(f"-----------------------------------")
    print(f'Quest: {quest_name}')
    print('Progress:')
    quest = player.quests[quest_name]
    if 'kill' in quest["objectives"]:
        for target in quest["objectives"]["kill"]:
            print(f'- Kill {target}: {quest["progress"]["kill"][target]}/{quest["objectives"]["kill"][target]}')
    if 'collect' in quest["objectives"]:
        for target in quest["objectives"]["collect"]:
            print(f' - Collect {item_data[target]["name"]}: {player.inventory.get(target, 0)}/{quest["objectives"]["collect"][target]}')
    print('[1] Abandon quest')
    print('[0] Go back')
    while True:
        match input('Choose an action > '):
            case '0':
                return
            case '1':
                print(f'Abandoned the quest "{quest_name}"!')
                del player.quests[quest_name]