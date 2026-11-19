from PoS.src.spawn_random_enemy import spawn_random_enemy
from PoS.src.battle_loop import battle_loop
from PoS.src.inventory_menu import inventory_menu
from PoS.src.crafting_menu import crafting_menu
from PoS.src.show_character_sheet import show_character_sheet
from PoS.src.merchant_menu import merchant_menu
from PoS.src.quest_menu import quest_menu
from PoS.src.construct_options import construct_options
from PoS.src.choose_option import choose_option
from PoS.src.embed import construct_embed
from PoS.src.embed import send_embed_with_buttons

async def town_loop(client, message, player, game_msg):
    while True:
        text = ""
        title = "TOWN"
        text += f"Hero: {player.name} | Level: {player.level} | HP: {player.hp}/{player.stats['maxhp']} | MP: {player.mp}/{player.maxmp()}\n"
        options = construct_options(["Hunt Monsters (Enter Dungeon)", "Inventory & Equipment",
            "Blacksmith (Crafting Forge)", "Rest at the Inn (Restore HP & MP)", "Visit merchant", 
            "View quests", "Character Sheet (View Full Stats)"], zero="Quit Game")
        text += options + "\n\n"
        text += "What would you like to do?"
        game_msg, choice = await send_embed_with_buttons(game_msg, message, title, text, 8)
        match choice:
            case 1:
                enemy = spawn_random_enemy(player.level)
                await battle_loop(game_msg, message, player, enemy)
            case 2:
                await inventory_menu(game_msg, player, message)
            case 3:
                await crafting_menu(game_msg, player, message)
            case 4:
                player.hp = player.stats["maxhp"]
                player.mp = player.maxmp()
                await message.channel.send("You rest at the inn. HP and MP are fully restored!", delete_after=10.0)
            case 5:
                merchant_menu(player, 'Frank the merchant')
            case 6:
                quest_menu(player)
            case 7:
                await show_character_sheet(game_msg, player, message)
            case 0:
                await message.channel.send('Goodbye!', delete_after = 10.0)
                await game_msg.delete()
                player.save_data()
                break

