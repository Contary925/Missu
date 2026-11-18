from src.spawn_random_enemy import spawn_random_enemy
from src.battle_loop import battle_loop
from src.inventory_menu import inventory_menu
from src.crafting_menu import crafting_menu
from src.show_character_sheet import show_character_sheet
from src.merchant_menu import merchant_menu
from src.quest_menu import quest_menu

def town_loop(player):
    while True:
        print("\n===TOWN===")
        print(f"Hero: {player.name} | Level: {player.level} | HP: {player.hp}/{player.stats['MAXHP']} | MP: {player.mp}/{player.maxmp()}")
        print("[1] Hunt Monsters (Enter Dungeon)")
        print("[2] Inventory & Equipment")
        print("[3] Blacksmith (Crafting Forge)")
        print("[4] Rest at the Inn (Restore HP & MP)")
        print("[5] Visit merchant")
        print("[6] View quests")
        print("[7] Character Sheet (View Full Stats)")
        print("[0] Quit Game")
        choice = input("\nWhat would you like to do? > ").strip()
        match choice:
            case '1':
                enemy = spawn_random_enemy(player.level)
                battle_loop(player, enemy)
            case '2':
                inventory_menu(player)
            case '3':
                crafting_menu(player)
            case '4':
                player.hp = player.stats["MAXHP"]
                player.mp = player.maxmp()
                print("\nYou rest at the inn. HP and MP are fully restored!")
            case '5':
                merchant_menu(player, 'Frank the merchant')
            case '6':
                quest_menu(player)
            case '7':
                show_character_sheet(player)
            case '0':
                print('Goodbye!')
                player.save_data()
                break
            case _:
                print('Invalid choice! Please enter a number from the menu.')

