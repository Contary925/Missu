import json
with open('PoS/src/quests/quests.json') as f:
    quests_data = json.load(f)
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)
with open('PoS/src/skills/jobs.json') as f:
    jobs_data = json.load(f)
jobs = list(jobs_data)

def quests_menu(player, NPC):
    print(f"-----------------------------------")
    quests = quests_data[NPC]
    counter = 0
    available_quests = []
    for quest in quests:
        if not quest_available(player, NPC, quest):
            continue
        available_quests.append({quest: quests[quest]})
        counter += 1
        print(f'[{counter}] {quest}')
    if available_quests == []:
        print(f"{NPC} doesn't have any available quests for you.")
        return
    print('[0] Go back')
    while True:
        choice = input('Choose a quest > ')
        try:
            choice = int(choice)
        except Exception:
            print("Invalid index! Please choose from the menu.")
            continue
        if choice == 0:
            return
        quest = available_quests[choice-1]
        break
    quest_name = list(quest)[0]
    if not quest_name in player.quests:
        quest_accept(player, quest)
        return
    match quest_check_completion(player, quest):
        case True:
            quest_report(player, quest)
        case False:
            print("You don't meet the conditions to report this quest!")
            return
    return

def quest_available(player, NPC, quest):
    job_req = quests_data[NPC][quest]["conditions"].get("job", jobs)
    min_level_req = quests_data[NPC][quest]["conditions"].get("min_level", 1)
    max_level_req = quests_data[NPC][quest]["conditions"].get("max_level", 999)
    if player.job not in job_req or player.level < min_level_req or player.level > max_level_req:
        return False
    if quests_data[NPC][quest]["repeatable"] == 0 and quest in player.completed_quests:
        return False
    return True

def quest_accept(player, quest):
    quest_name = list(quest)[0]
    print(quest[quest_name]["accept_text"])
    print('[1] Accept')
    print('[0] Go back')
    choice = input('Accept this quest? > ')
    match choice:
        case '0':
            return
        case '1':
            objectives = quest[quest_name]["objectives"]
            new_quest =  {
                "objectives": objectives,
                "progress": {}
            }
            if "kill" in objectives:
                new_quest["progress"]["kill"] = {}
                for target in objectives["kill"]:
                    new_quest["progress"]["kill"][target] = 0
            player.quests[quest_name] = new_quest
            print(f'Accepted the quest "{quest_name}"!')
    return

def quest_check_completion(player, quest):
    quest_name = list(quest)[0]
    for target in player.quests[quest_name]["objectives"].get("kill", {}):
        if player.quests[quest_name]["progress"]["kill"][target] < player.quests[quest_name]["objectives"]["kill"][target]:
            return False
    for target in player.quests[quest_name]["objectives"].get("collect", {}):
        if player.inventory.get(target, 0) < player.quests[quest_name]["objectives"]["collect"][target]:
            return False
    return True

def quest_report(player, quest):
    quest_name = list(quest)[0]
    print(f"-----------------------------------")
    print(quest[quest_name]["report_text"])
    exp = quest[quest_name]["rewards"].get("EXP", 0)
    player.get_exp(None, exp)
    for target in quest[quest_name]["objectives"].get("collect", {}):
        player.remove_from_inventory(target, quest[quest_name]["objectives"]["collect"][target])
    if "items" in quest[quest_name]["rewards"]:
        for item_reward in quest[quest_name]["rewards"]["items"]:
            player.add_to_inventory(item_reward, quest[quest_name]["rewards"]["items"][item_reward])
            print(f'You got {quest[quest_name]["rewards"]["items"][item_reward]}x {item_data[item_reward]["name"]}.')
    if "skills" in quest[quest_name]["rewards"]:
        for skill in quest[quest_name]["rewards"]["skills"]:
            player.skills.append(skill)
    del player.quests[quest_name]
    player.completed_quests.append(quest_name)
    print(f'Reported the quest {quest_name}!')
    return