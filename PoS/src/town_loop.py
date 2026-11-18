from PoS.src.spawn_random_enemy import spawn_random_enemy
from PoS.src.battle_loop import battle_loop
from PoS.src.inventory_menu import inventory_menu
from PoS.src.crafting_menu import crafting_menu
from PoS.src.show_character_sheet import show_character_sheet
from PoS.src.merchant_menu import merchant_menu
from PoS.src.quest_menu import quest_menu
from PoS.src.construct_options import construct_options
from PoS.src.choose_option import choose_option

async def town_loop(client, message, player):
    while True:
        text = ""
        text += "# TOWN\n\n"
        text += f"Hero: {player.name} | Level: {player.level} | HP: {player.hp}/{player.stats['maxhp']} | MP: {player.mp}/{player.maxmp()}\n"
        options = construct_options(["Hunt Monsters (Enter Dungeon)", "Inventory & Equipment",
            "Blacksmith (Crafting Forge)", "Rest at the Inn (Restore HP & MP)", "Visit merchant", 
            "View quests", "Character Sheet (View Full Stats)"], zero="Quit Game")
        text += options + "\n\n"
        text += "What would you like to do?"
        game_msg = await message.channel.send(text)
        choice = await choose_option(message.author, client, game_msg, 8)
        match choice:
            case 1:
                enemy = spawn_random_enemy(player.level)
                battle_loop(player, enemy)
            case 2:
                inventory_menu(player)
            case 3:
                crafting_menu(player)
            case 4:
                player.hp = player.stats["maxhp"]
                player.mp = player.maxmp()
                print("\nYou rest at the inn. HP and MP are fully restored!")
            case 5:
                merchant_menu(player, 'Frank the merchant')
            case 6:
                quest_menu(player)
            case 7:
                show_character_sheet(player)
            case 0:
                print('Goodbye!')
                player.save_data()
                break

