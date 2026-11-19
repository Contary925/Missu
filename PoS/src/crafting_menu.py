import json
from PoS.src.embed import send_embed_with_buttons
with open('PoS/src/recipes/recipes.json') as f:
    recipes = json.load(f)
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)

async def crafting_menu(game_msg, player, message):
    title = f"Available items for crafting:"
    text = ""
    counter = 0
    for recipe in recipes:
        counter += 1
        text += f'\n[{counter}] {recipes[recipe]["output_quantity"]}x {item_data[recipe]["name"]}:'
        for material in recipes[recipe]["materials"]:
            text += f'\n- {recipes[recipe]["materials"][material]}x {item_data[material]["name"]}'
    text += f"\n[0] Go back"
    _, choice = await send_embed_with_buttons(game_msg, message, title, text, len(recipes)+1)
    res_text = player.craft(list(recipes)[choice-1])
    await message.channel.send(res_text, delete_after=10.0)
    return