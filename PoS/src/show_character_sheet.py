import json
from PoS.src.embed import send_embed_with_custom_buttons
with open('PoS/src/items/item_data.json') as f:
    item_data = json.load(f)
with open('PoS/src/skills/skill_data.json') as f:
    skill_data = json.load(f)

async def show_character_sheet(game_msg, player, message):
    text = ""
    # Calculate XP progress percentage and bar
    xp_pct = min(1.0, player.exp / player.level_exp) if player.level_exp > 0 else 1.0
    bar_length = 20
    filled_length = int(bar_length * xp_pct)
    xp_bar = "█" * filled_length + "░" * (bar_length - filled_length)

    title = f"**CHARACTER SHEET: {player.name}**"
    
    # Section 1: Overview & Progression
    text += f"\n Class / Job: {player.job.capitalize()}"
    text += f"\n Level: {player.level}"
    text += f"\n Experience: {player.exp} / {player.level_exp} [{xp_bar}] {int(xp_pct * 100)}%"
    
    # Section 2: Vitals & Core Stats
    text += f"\n HP (Health): {player.hp} / {player.stats['maxhp']}"
    text += f"\n MP (Mana): {player.mp} / {player.maxmp()}"
    text += f"\n Attack (ATK): {player.stats['atk']}"
    text += f"\n Defense (DEF): {player.stats['def']}"
    if player.stats.get("resistances"):
        res_str = ", ".join(f"{k}: {v}%" for k, v in player.stats["resistances"].items())
        text += f"\n Resistances: {res_str}"
    
    # Section 3: Equipment Loadout
    text += "\n\n EQUIPMENT:"
    for slot, item_id in player.equipment.items():
        if item_id and item_id in item_data:
            item_name = item_data[item_id]["name"]
            bonuses = item_data[item_id].get("stat_bonuses", {})
            bonus_str = " (" + ", ".join(f"+{v} {k}" for k, v in bonuses.items()) + ")" if bonuses else ""
            text += f"\n[{slot.capitalize()}]: {item_name}{bonus_str}"
        else:
            text += f"\n[{slot.capitalize()}]: <Empty>"

    # Section 4: Known Skills
    text += "\n\n LEARNED SKILLS:"
    for skill_name in player.skills:
        info = skill_data[skill_name]
        cost = info.get("cost", 0)
        desc = info.get("description", "")
        text += f"\n- {skill_name.capitalize()} (Cost: {cost} MP) -> {desc}"

    await send_embed_with_custom_buttons(game_msg, message, title, text, ["To Town"])
    return