
import json


def add_base_entity_stats(
        kind: str,
        hp: int,
        attack: int,
        defense: int,
        exp: int,
        resistances: dict[str, int],
        min_lvl: int = 1,
        max_lvl: int = 999,
        spawn_rate_weight: int = 10,
        regeneration: int = 0,
        ):
    path = 'PoS/src/stats/entity_base_stats.json'

    with open(path, 'r') as f:
        stats = json.load(f)

    stats[kind] = {
        "maxhp": hp,
        "atk": attack,
        "def": defense,
        "exp": exp,
        "regeneration": regeneration,
        "resistances": resistances,
        "min_lvl": min_lvl,
        "max_lvl": max_lvl,
        "spawn_rate_weight": spawn_rate_weight
    }

    with open(path, 'w') as f:
        json.dump(stats, f, indent=4)

    return
