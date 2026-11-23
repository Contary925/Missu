import json
from PoS.src.embed import send_embed_with_buttons, send_embed_with_custom_buttons
with open('PoS/src/quests/quests.json') as f:
    quests_data = json.load(f)
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)
with open('PoS/src/skills/jobs.json') as f:
    jobs_data = json.load(f)
jobs = list(jobs_data)

async def quests_menu(game_msg, message, player, NPC):
    title = f"**{NPC.capitalize()}'s quests:**"
    text = ""
    quests = quests_data[NPC]
    counter = 0
    available_quests = []
    for quest in quests:
        if not quest_available(player, NPC, quest):
            continue
        available_quests.append({quest: quests[quest]})
        counter += 1
        text += f'\n[{counter}] {quest.capitalize()}'
    if available_quests == []:
        text += f"{NPC} doesn't have any available quests for you."
        msg, choice = await send_embed_with_custom_buttons(game_msg, message, title, text, ["Go back"])
        await msg.delete()
        return
    text += '\n[0] Go back'
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, len(available_quests)+1)
    if choice == 0:
        return
    quest = available_quests[choice-1]
    quest_name = list(quest)[0]
    if not quest_name in player.quests:
        await quest_accept(game_msg, message, player, quest)
        return
    match quest_check_completion(player, quest):
        case True:
            await quest_report(game_msg, message, player, quest)
        case False:
            await message.channel.send("You don't meet the conditions to report this quest!", delete_after = 10.0)
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

async def quest_accept(game_msg, message, player, quest):
    quest_name = list(quest)[0]
    title = f"**{quest_name.capitalize()}**"
    text = quest[quest_name]["accept_text"]
    _, choice = await send_embed_with_custom_buttons(game_msg, message, title, text, ["Accept", "Decline"])
    match choice:
        case "Decline":
            return
        case "Accept":
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
            await message.channel.send(f'Accepted the quest "{quest_name.capitalize()}"!', delete_after = 10.0)
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

async def quest_report(game_msg, message, player, quest):
    quest_name = list(quest)[0]
    title = f"**{quest_name.capitalize()}**"
    text = quest[quest_name]["report_text"]
    exp = quest[quest_name]["rewards"].get("EXP", 0)
    text += player.get_exp(None, exp)
    for target in quest[quest_name]["objectives"].get("collect", {}):
        player.remove_from_inventory(target, quest[quest_name]["objectives"]["collect"][target])
    if "items" in quest[quest_name]["rewards"]:
        for item_reward in quest[quest_name]["rewards"]["items"]:
            player.add_to_inventory(item_reward, quest[quest_name]["rewards"]["items"][item_reward])
            text += f'\nYou got {quest[quest_name]["rewards"]["items"][item_reward]}x {item_data[item_reward]["name"]}.'
    if "skills" in quest[quest_name]["rewards"]:
        for skill in quest[quest_name]["rewards"]["skills"]:
            text += f'\nLearned a new skill: {skill.capitalize()}!'
            player.skills.append(skill)
    del player.quests[quest_name]
    if not quest_name in player.completed_quests:
        player.completed_quests.append(quest_name)
    text += f'\nReported the quest {quest_name.capitalize()}!'
    await send_embed_with_custom_buttons(game_msg, message, title, text, ["Go back"])
    return