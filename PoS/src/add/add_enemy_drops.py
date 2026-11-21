import json

def add_enemy_drops(
        enemy: str, 
        item_id: str, 
        chance: int, 
        min_qty: int,
        max_qty: int
        ):
    with open('PoS/src/stats/loot_tables.json', 'r') as f:
        loot_tables = json.load(f)
    if not enemy in loot_tables:
        loot_tables[enemy] = {}
    loot_tables[enemy][item_id] = {
        'chance': chance,
        'min_qty': min_qty,
        'max_qty': max_qty
    }
    with open('PoS/src/stats/loot_tables.json', 'w') as f:
        json.dump(loot_tables, f, indent=4)
    