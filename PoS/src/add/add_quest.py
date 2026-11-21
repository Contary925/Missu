import json

quest_template = {
    "conditions": {
        "min_level": 1,
        "max_level": 999
    },
    "objectives": {
        "kill": {

        },
        "collect": {

        }
    },
    "rewards": {
        "EXP": 0,
        "items": {

        },
        "skills": [

        ]
    },
    "repeatable": 1,
    "accept_text": "",
    "report_text": ""
}

def add_quest(
        character: str, 
        quest_name: str, 
        quest: dict
        ):
    with open('PoS/src/quests/quests.json') as f:
        quests = json.load(f)
    if not character in quests:
        quests[character] = {}
    quests[character][quest_name] = quest
    with open('PoS/src/quests/quests.json', 'w') as f:
        json.dump(quests, f, indent=4)