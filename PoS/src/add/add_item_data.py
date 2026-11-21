import json

def add_item_data(
        item_id: str, 
        name: str, type: str, 
        description: str,
        consumable_effects = {},
        equipment_info = {},
        price = 1
        ):
    with open('PoS/src/items/item_data.json', 'r') as f:
        items = json.load(f)
    items[item_id] = {
        "name": name,
        "type": type,
        "description": description,
        "consumable_effects": consumable_effects,
        "equipment_info": equipment_info, 
        "merchant_price": price
    }
    with open('PoS/src/items/item_data.json', 'w') as f:
        json.dump(items, f, indent=4)
    