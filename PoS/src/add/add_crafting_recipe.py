import json

def add_crafting_recipe(
        item_id: str, 
        materials: dict, 
        output_quantity = 1
        ):
    with open('PoS/src/recipes/recipes.json', 'r') as f:
        recipes = json.load(f)
    recipes[item_id] = {
        'materials': materials,
        'output_quantity': output_quantity
    }
    with open('PoS/src/recipes/recipes.json', 'w') as f:
        json.dump(recipes, f, indent=4)