import json

from PoS.src.merchant_menu import greet
from PoS.src.embed import send_embed_with_custom_buttons
from PoS.src.quests import quests_menu

with open('PoS/src/NPC/npc_info.json') as f:
    npc_info = json.load(f)

async def church_menu(game_msg, message, player, npc_name: str):
    text, title  = greet(npc_name, player) 
    while True:
        _, choice = await send_embed_with_custom_buttons(game_msg, message, title, text, ["Restore HP", "Rest for 10 gold", "Quests", "Go back"])
        match choice:
            case "Go back":
                return
            case "Restore HP":
                player.hp = player.stats["maxhp"]
                await message.channel.send("Your HP was fully restored!", delete_after = 10.0)
            case "Rest for 10 gold":
                if player.inventory.get("gold_coin", 0) < 10:
                    await message.channel.send("You don't have enough gold!", delete_after = 10.0)
                    continue
                player.inventory["gold_coin"] -= 10
                player.hp = player.stats["maxhp"]
                player.mp = player.maxmp()
                await message.channel.send("Your HP and MP were fully restored!", delete_after = 10.0)
            case "Quests":
                await quests_menu(game_msg, message, player, npc_name)