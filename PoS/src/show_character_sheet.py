import json
with open('src/items/item_data.json') as f:
    item_data = json.load(f)
with open('src/skills/skill_data.json') as f:
    skill_data = json.load(f)

def show_character_sheet(player):
    # Calculate XP progress percentage and bar
    xp_pct = min(1.0, player.exp / player.level_exp) if player.level_exp > 0 else 1.0
    bar_length = 20
    filled_length = int(bar_length * xp_pct)
    xp_bar = "█" * filled_length + "░" * (bar_length - filled_length)

    print("\n" + "=" * 45)
    print(f"         CHARACTER SHEET: {player.name}")
    print("=" * 45)
    
    # Section 1: Overview & Progression
    print(f" Class / Job   : {player.job}")
    print(f" Level         : {player.level}")
    print(f" Experience    : {player.exp} / {player.level_exp} [{xp_bar}] {int(xp_pct * 100)}%")
    print("-" * 45)
    
    # Section 2: Vitals & Core Stats
    print(f" HP (Health)   : {player.hp} / {player.stats['MAXHP']}")
    print(f" MP (Mana)     : {player.mp} / {player.maxmp()}")
    print(f" Attack (ATK)  : {player.stats['ATK']}")
    print(f" Defense (DEF) : {player.stats['DEF']}")
    if player.stats.get("RESISTANCES"):
        res_str = ", ".join(f"{k}: {v}%" for k, v in player.stats["RESISTANCES"].items())
        print(f" Resistances   : {res_str}")
    print("-" * 45)
    
    # Section 3: Equipment Loadout
    print(" EQUIPMENT:")
    for slot, item_id in player.equipment.items():
        if item_id and item_id in item_data:
            item_name = item_data[item_id]["name"]
            bonuses = item_data[item_id].get("stat_bonuses", {})
            bonus_str = " (" + ", ".join(f"+{v} {k}" for k, v in bonuses.items()) + ")" if bonuses else ""
            print(f"   [{slot.capitalize():<9}] : {item_name}{bonus_str}")
        else:
            print(f"   [{slot.capitalize():<9}] : <Empty>")
    print("-" * 45)

    # Section 4: Known Skills
    print(" LEARNED SKILLS:")
    for skill_name in player.skills:
        info = skill_data[skill_name]
        cost = info.get("COST", 0)
        desc = info.get("DESCRIPTION", "")
        print(f"   - {skill_name:<14} (Cost: {cost:>2} MP) -> {desc}")

    print("=" * 45)
    input("\nPress [Enter] to return to town...")