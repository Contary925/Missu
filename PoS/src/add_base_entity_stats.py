import json

def add_base_entity_stats(
        kind: str, 
        hp: int, 
        attack: int, 
        defense: int, 
        resistances: dict[(str, int)],
        min_level: int = 1,
        max_level: int = 999,
        spawn_rate_weight: int = 10,
        ):
    with open('PoS/src/stats/entity_base_stats.json', 'r') as f:
        stats = json.load(f)
    #if entity stats are already here, we'll simply overwrite them
    stats[kind] = {
        "maxhp": hp,
        "atk": attack,
        "def": defense,
        "resistances": resistances,
        "min_level": min_level,
        "max_level": max_level,
        "spawn_rate_weight": spawn_rate_weight
    }
    with open('PoS/src/stats/entity_base_stats.json', 'w') as f:
        json.dump(stats, f, indent=4)
    return