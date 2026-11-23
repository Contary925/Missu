import json
from pathlib import Path


ENEMY_SKILLS_PATH = Path("PoS/src/skills/enemy_skills.json")


def save_enemy_skills(enemy: str, skills: dict):
    with ENEMY_SKILLS_PATH.open("r", encoding="utf-8") as f:
        enemy_skills = json.load(f)

    enemy_skills[enemy] = skills

    with ENEMY_SKILLS_PATH.open("w", encoding="utf-8") as f:
        json.dump(enemy_skills, f, indent=4, ensure_ascii=False)