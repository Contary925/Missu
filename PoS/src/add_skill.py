import json

def add_skill(
        name: str,
        type: str,
        cost: int,
        effects: dict,
        description: str = 'No description'
    ):
    with open('src/skills/skill_data.json', 'r') as f:
        skills = json.load(f)
    #if a skill is already here, we overwrite the data
    skills[name] = {
        "TYPE": type,
        "COST": cost,
        "EFFECTS": effects,
        "DESCRIPTION": description
    }
    with open('src/skills/skill_data.json', 'w') as f:
        json.dump(skills, f, indent=4)
    return
