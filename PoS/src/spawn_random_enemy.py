import json
import random
from PoS.src.entity_classes import Enemy
with open('PoS/src/stats/entity_base_stats.json') as f:
    enemies = json.load(f)
enemies.pop("player", None)

def spawn_random_enemy(level: int):
    valid_enemies_list = []
    weights = []
    for enemy, enemy_data in enemies.items():
        if enemy_data.get("min_lvl", 1) > level or enemy_data.get("max_lvl", 999) < level:
            continue
        valid_enemies_list.append(enemy)
        weights.append(enemy_data.get("spawn_rate_weight", 1))
    if not valid_enemies_list:
        return Enemy("goblin", level)
    chosen_enemy_kind = random.choices(valid_enemies_list, weights=weights, k=1)[0]
    return Enemy(chosen_enemy_kind, level)
