import json
from PoS.src.embed import send_embed_with_buttons
with open('PoS/src/skills/skill_data.json') as f:
    skills_info = json.load(f)

async def skills_menu(game_msg, player, enemy, message, title):
    skills = player.skills
    text = "\nThe MP cost is specified in ()"
    counter = 0
    for skill in skills:
        counter += 1 
        text += f"\n[{counter}] {skill.capitalize()} ({skills_info[skill]["cost"]})"
    text += f"\n[0] Go back"
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, len(skills)+1)
    if choice == 0:
        return "", False
    return player.use_skill(skills[choice-1], enemy)

