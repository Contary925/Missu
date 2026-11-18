from src.skills_menu import skills_menu
from src.combat_items_menu import combat_items_menu

def battle_loop(player, enemy):
    print(f"\n--- Starting a fight between **{player.kind}** and **{enemy.kind}**! ---")
    round_count = 1
    while player.alive and enemy.alive:
        print(f"\n[Round {round_count}]")
        print(f"Player: {player.hp} HP | {player.mp} MP")
        print(f"{enemy.kind}: {enemy.hp} HP")
        match player_turn(enemy, player):
            case 'fled':
                return
        enemy_turn(enemy, player)
        round_count += 1
    if not player.alive:
        player.alive = True
    return

def player_turn(enemy, player):
    while True:
        print("-----------------------------------")
        print("[1] Basic Attack")
        print("[2] Cast Skill")
        print("[3] Use Potion / Item")
        print("[4] Flee")
        if "STUN" in player.debuffs:
            print('You are stunned! You cannot act!')
            player.tick()
            break
        choice = input("Choose an action > ").strip()
        match choice:
            case '1':
                player.use_skill("Attack", enemy)
            case '2':
                match skills_menu(player, enemy):
                    case False:
                        continue
            case '3':
                match combat_items_menu(player):
                    case False:
                        continue
            case '4':
                print("You fled from the battle.")
                return 'fled'
            case _:
                print("Invalid action! Choose action from the menu.")
                continue
        player.tick()
        break

def enemy_turn(enemy, player):
    if not enemy.alive:
        return
    print(f"\n--- {enemy.kind}'s Turn ---")
    enemy.use_random_skill(player)
    enemy.tick()