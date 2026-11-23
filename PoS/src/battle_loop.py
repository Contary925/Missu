from PoS.src.skills_menu import skills_menu
from PoS.src.combat_items_menu import combat_items_menu
from PoS.src.embed import construct_embed, send_embed_with_buttons, send_embed_with_custom_buttons

def header(player, enemy, round_count):
    text = ""
    text += f"\n[Round {round_count}]"
    text += f"\n{player.name}: {player.hp} HP | {player.mp} MP"
    text += f"\n{enemy.name}: {enemy.hp} HP"
    return text

async def battle_loop(game_msg, message, player, enemy):
    title = f"A fight between **{player.name}** and **{enemy.name}** has started!"
    round_count = 1
    text = ""
    while player.alive and enemy.alive:
        text += header(player, enemy, round_count)
        res_text = await player_turn(game_msg, enemy, player, message, round_count, title, text)
        text = ""
        match res_text:
            case 'fled':
                return
            case _:
                text += res_text
        text += enemy_turn(enemy, player)
        round_count += 1
        text += "\n"
    if not player.alive:
        player.alive = True
    if not enemy.alive:
        await send_embed_with_custom_buttons(game_msg, message, title, text, ["To Town"])
    return

async def player_turn(game_msg, enemy, player, message, round_count, title="", text=""):
    res_text = ""
    while True:
        if "stun" in player.debuffs:
            text += "\nYou are stunned! You cannot act!"
            text += player.tick()
            res_text = text
            break
        text += f"\n{player.name}'s turn!\n"
        text += "\n[1] Basic Attack"
        text += "\n[2] Cast Skill"
        text += "\n[3] Use Potion / Item"
        text += "\n[4] Flee"
        game_msg, choice = await send_embed_with_buttons(game_msg, message, title, text, 4, False)
        match choice:
            case 1:
                res_text, _ = player.use_skill("attack", enemy)
                text += res_text
            case 2:
                res_text, used = await skills_menu(game_msg, player, enemy, message, title)
                match used:
                    case False:
                        text = header(player, enemy, round_count) + res_text
                        continue
            case 3:
                res_text, used = await combat_items_menu(game_msg, message, player, title)
                match used:
                    case False:
                        text = header(player, enemy, round_count) + res_text
                        continue
            case 4:
                text += "\nYou fled from the battle."
                await send_embed_with_custom_buttons(game_msg, message, title, text, ["To Town"])
                return 'fled'
        player.tick()
        break
    return res_text

def enemy_turn(enemy, player):
    text = ""
    if not enemy.alive:
        return text
    text += f"\n{enemy.name}'s turn!"
    text += enemy.use_random_skill(player)
    text += enemy.tick()
    return text