import json
with open('PoS/src/skills/skill_data.json') as f:
    skills_info = json.load(f)

def skills_menu(player, enemy):
    skills = player.skills
    print(f"-----------------------------------")
    print(f"The MP cost is specified in ()")
    counter = 0
    for skill in skills:
        counter += 1 
        print(f"[{counter}]: {skill} ({skills_info[skill]["cost"]})") 
    print(f"[0] Go back")
    while True:
        choice = input("Choose a skill you want to use > ").strip()
        if not choice.isdigit():
            print('Invalid skill! Choose from the menu.')
            continue
        choice = int(choice)
        if choice > counter:
            print('Invalid skill! Choose from the menu.')
            continue
        if choice == 0:
            return False
        break
    return player.use_skill(skills[choice-1], enemy)

