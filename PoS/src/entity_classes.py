import json
import math
import random
import copy
with open('PoS/src/skills/jobs.json') as f:
    jobs_info = json.load(f)

#data from files. This is IMMUTABLE by agreement
with open('PoS/src/stats/entity_base_stats.json', 'r') as f:
    base_stats = json.load(f)
with open('PoS/src/stats/level_scaling.json', 'r') as f:
    level_scaling = json.load(f)
with open('PoS/src/stats/loot_tables.json', 'r') as f:
    loot_tables = json.load(f)
with open('PoS/src/items/item_data.json', 'r') as f:
    item_data = json.load(f)
with open('PoS/src/recipes/recipes.json', 'r') as f:
    crafting_recipes = json.load(f)

class Entity:
    def __init__(self, kind: str, level: int):
        self.kind = kind
        self.level = level
        self.buffs = {}
        self.debuffs = {}
        self.stats = self.set_stats()
        self.hp = self.stats["maxhp"]
        self.alive = True
    def tick(self) -> str:
        text = ""
        expired = []
        for name in self.buffs:
            self.buffs[name]["duration_left"] -= 1
            if self.buffs[name]["duration_left"] == 0:
                text += f'\nThe effect "{name.capitalize()}" on {self.name} has expired!'
                expired.append(name)
        for buff in expired:
            del self.buffs[buff]
        expired = []
        for debuff in self.debuffs:
            self.debuffs[debuff]["duration_left"] -= 1
            if self.debuffs[debuff]["duration_left"] == 0:
                text += f'\n{debuff.capitalize()} on {self.name} has expired!'
                expired.append(debuff)
        for debuff in expired:
            del self.debuffs[debuff]
        self.stats = self.set_stats()
        return text
    def set_stats(self) -> dict:
        if not self.kind in base_stats:
            return dict()
        match self.kind:
            case "player":
                etype = "character"
            case "companion":
                etype = "character"
            case _:
                etype = "enemy"
        total_stats = {
            "maxhp": base_stats[self.kind]["maxhp"] + (self.level-1) * level_scaling[etype]["maxhp"],
            "atk": base_stats[self.kind]["atk"] + (self.level-1) * level_scaling[etype]["atk"],
            "def": base_stats[self.kind]["def"] + (self.level-1) * level_scaling[etype]["def"],
            "resistances": base_stats[self.kind]["resistances"].copy()
        }
        for buff_name in self.buffs:
            if "stat" in self.buffs[buff_name]:
                total_stats[self.buffs[buff_name]["stat"]] += self.buffs[buff_name]["effect"]
            if "resistance" in self.buffs[buff_name]:
                for debuff in self.buffs[buff_name]["resistance"]:
                    total_stats["resistances"][debuff] = self.buffs[buff_name]["resistance"][debuff]
        return total_stats
    def take_damage(self, damage: int) -> str:
        text = ""
        text += f"\n{self.name} takes {damage} damage..."
        self.hp = max(0, self.hp - damage)
        text += f"\n{self.name}'s hp: {self.hp}"
        if self.hp <= 0:
            self.alive = False
        return text
    def deal_damage(self, target, multiplier = 100) -> str:
        text = ""
        damage = max(1, math.ceil(self.stats["atk"] * multiplier/100) - target.stats["def"])
        text += f"\n{self.name} deals {damage} damage to {target.name}..."
        text += target.take_damage(damage)
        return text
    def use_skill(self, name: str, target=None) -> str:
        text = ""
        with open('PoS/src/skills/skill_data.json', 'r') as f:
            skills = json.load(f)
        if not name in skills:
            return text
        text += f'\n{self.name} uses a skill "{name}"!'
        skill = skills[name]
        match skill["type"]:
            case "buff":
                if "duration" in skill["effects"]:
                    duration = skill["effects"]["duration"]
                    for stat in skill["effects"]["stat_buffs"]:
                        effect = skill["effects"]["stat_buffs"][stat]
                        text += self.buff(name, duration, stat, effect)
                if "healing" in skill["effects"]:
                    old_hp = self.hp
                    self.hp = min(self.stats["maxhp"], self.hp + math.ceil(self.stats["maxhp"] * skill["effects"]["healing"]/100))
                    if self.hp > old_hp:
                        text += f'\n{self.name} has recovered {self.hp - old_hp} hp!'
            case "attack":
                multiplier = skill["effects"]["multiplier"]
                text += self.deal_damage(target, multiplier)
                if not target.alive:
                    return text
                if "debuffs" in skill["effects"]:
                    for debuff in skill["effects"]["debuffs"]:
                        duration = skill["effects"]["debuffs"][debuff]["duration"]
                        debuff_res = target.stats["resistances"].get(debuff, 0)
                        chance = math.ceil(skill["effects"]["debuffs"][debuff]["chance"] * (100 - debuff_res)/100)
                        text += target.debuff(debuff, duration, chance)
        return text
    def buff(self, name: str, duration: int, stat: str = None, effect: int = None, resistance_enhance: tuple = None) -> str:
        text = ""
        if stat is not None:
            text += f'\nApplied effect "{name.capitalize()}" on {self.name}! {stat} will increase for {duration} turns!'
        if resistance_enhance is not None:
            debuff = resistance_enhance[0]
            value = resistance_enhance[1]
            match duration:
                case 1:
                    text += f'\nApplied effect "{name.capitalize()}" on {self.name}! Resistance to {debuff.capitalize()} will increase for one turn!'
                case _:
                    text += f'\nApplied effect "{name.capitalize()}" on {self.name}! Resistance to {debuff}.capitalize() will increase for {duration} turns!'
        if name in self.buffs:
            self.buffs[name]["duration_left"] = duration
            return text
        self.buffs[name] = {
            "duration_left": duration + 1, #the buffs are applied just before self.tick(), so this +1 is necessary for the buff to effectively work for {duration} turns rather than {duration-1}
        }
        if stat:
            self.buffs[name]["stat"] = stat
            self.buffs[name]["effect"] = math.ceil(self.stats[stat]*effect/100) #flat amount that will be added
        if resistance_enhance is not None:
            self.buffs[name]["resistance"] = {}
            self.buffs[name]["resistance"][debuff] = value
        self.stats = self.set_stats()
        return text
        
    def debuff(self, debuff: str, duration: int, chance: int) -> str:
        text = ""
        if random.randint(1, 100) <= chance:
            match duration:
                case 1:
                    text += f'\nApplied effect "{debuff.capitalize()}" to {self.name} for {duration} turn!'
                case _:
                    text += f'\nApplied effect "{debuff.capitalize()}" to {self.name} for {duration} turns!'
            self.debuffs[debuff] = {
                "duration_left": duration
            }
            self.buff(f'{debuff} resistance', 1, None, None, (f'{debuff}', 100))
        return text

class Player(Entity):
    def __init__(self, player_data: dict = {}):
        self.kind = 'player'
        self.level = player_data.get("level", 1)
        self.equipment = player_data.get("equipment", {
            'weapon': None,
            'armor': None,
            'special': None
        })
        super().__init__(self.kind, self.level)
        self.id = player_data.get("id", 0)
        self.name = player_data.get("name", "guest")
        self.job = player_data.get("job", "adventurer")
        self.player_data = player_data
        self.exp = player_data.get("exp", 0)
        self.level_exp = self.new_level_exp()
        self.hp = player_data.get("hp", self.stats["maxhp"])
        self.mp = player_data.get("mp", self.maxmp())
        self.inventory = player_data.get("inventory", {})
        self.skills = player_data.get("skills", jobs_info[self.job]["skills"])
        self.quests = player_data.get("quests", {})
        self.completed_quests = player_data.get("completed_quests", [])
        
    def set_stats(self):
        stats = super().set_stats()
        for eq_type in self.equipment:
            item_id = self.equipment[eq_type]
            if item_id != None:
                for stat in item_data[item_id]["equipment_info"]:
                    match stat:
                        case 'maxhp':
                            stats["maxhp"] += item_data[item_id]["equipment_info"]['maxhp']
                        case 'atk':
                            stats["atk"] += item_data[item_id]["equipment_info"]['atk']
                        case 'def':
                            stats["def"] += item_data[item_id]["equipment_info"]['def']
                        case 'resistance':
                            for debuff in item_data[item_id]["equipment_info"]["resistance"]:
                                if not debuff in stats['resistances']:
                                    stats['resistances'][debuff] = 0
                                stats['resistances'][debuff] += item_data[item_id]["equipment_info"]["resistance"][debuff]
        return stats

    def new_level_exp(self):
        return 10 * self.level ** 2
    def maxmp(self):
        return 100 + (self.level - 1) * 10
    def take_damage(self, damage: int) -> str:
        text = ""
        text += super().take_damage(damage)
        if self.alive == False:
            text += "You died! You will return to town."
            self.respawn()
        return text
    def respawn(self):
        self.hp = self.stats["maxhp"]
        self.mp = self.maxmp()
    def deal_damage(self, target, multiplier=100) -> str:
        text = ""
        text += super().deal_damage(target, multiplier)
        if target.alive == False:
            text += f"\nCongratulations! You killed a level {target.level} {target.name}!"
            text += self.get_kill_reward(target)
            text += self.count_quest_progress(target)
        return text
    def count_quest_progress(self, target) -> str:
        text = ""
        for quest in self.quests:
            if "kill" in self.quests[quest]["objectives"]:
                if target.kind in self.quests[quest]["objectives"]["kill"]:
                    self.quests[quest]["progress"]["kill"][target.kind] = min(self.quests[quest]["progress"]["kill"][target.kind]+1, self.quests[quest]["objectives"]["kill"][target.kind])
                    text += f'\n{quest.capitalize()}: Kill {target.name} {self.quests[quest]["progress"]["kill"][target.kind]}/{self.quests[quest]["objectives"]["kill"][target.kind]}'
        return text
    def get_kill_reward(self, target) -> str:
        text = ""
        text += self.get_exp(target=target)
        drops = target.roll_drops()
        for item, quantity in drops.items():
            self.inventory[item] = self.inventory.get(item, 0) + quantity
            item_name = item_data[item]["name"]
            text += f"\nObtained {quantity}x {item_name.capitalize()}!"
        return text
    def get_exp(self, target=None, amount=0) -> str:
        text = ""
        exp = 0
        if amount != 0:
            exp += amount
        if target is not None:
            if self.level - target.level > 10:
                text += f"\nYour level is too high to obtain any experience from {target.name}."
                return text
            exp += math.floor(base_stats[target.kind]["exp"] * (1 + 0.1 * target.level))
        self.exp += exp
        if exp:
            text += f"\nYou got {exp} experience."
        old_level = self.level
        while self.exp >= self.level_exp :
            self.level_up()
        if self.level > old_level:
            text += f"\nCongratulations! You leveled up to level {self.level}!"
        return text
    def level_up(self):
        self.exp -= self.level_exp
        self.level += 1
        self.stats = self.set_stats()
        self.hp = self.stats["maxhp"]
        self.mp = self.maxmp()
        self.level_exp = self.new_level_exp()
    def use_skill(self, name: str, target = None):
        text = ""
        if "stun" in self.debuffs:
            text += '\nYou are stunned! You cannot act!'
            return text, False
        with open('PoS/src/skills/skill_data.json', 'r') as f:
            skills = json.load(f)
        if not name in skills:
            return text, False
        if self.mp < skills[name]["cost"]:
            text += "\nYou don't have enough MP to use this skill!"
            return text, False
        text += super().use_skill(name, target)
        self.mp -= int(skills[name]["cost"])
        self.stats = self.set_stats()
        return text, True
    def use_item(self, id: str):
        text = ""
        if not id in self.inventory:
            return text, False
        if item_data[id]['type'] != 'consumable':
            return text, False
        text += f'\nYou used a {item_data[id]["name"].capitalize()}!'
        self.inventory[id] -= 1
        if self.inventory[id] == 0:
            del self.inventory[id]
        for effect in item_data[id]['consumable_effects']:
            match effect:
                case 'hp':
                    old_hp = self.hp
                    self.hp = min(self.hp + item_data[id]['consumable_effects']['hp'], self.stats['maxhp'])
                    if self.hp > old_hp:
                        text += f'\nRecovered {self.hp - old_hp} HP!'
                case 'mp':
                    old_mp = self.mp
                    self.mp = min(self.mp + item_data[id]['consumable_effects']['mp'], self.maxmp())
                    if self.mp > old_mp:
                        text += f'\nRecovered {self.mp - old_mp} MP!'
        self.stats = self.set_stats()
        return text, True
    def add_to_inventory(self, item, quantity=1):
        self.inventory[item] = self.inventory.get(item, 0) + quantity   
    def craft(self, item_id):
        text = ""
        if not item_id in crafting_recipes:
            text += "\nUnknown crafting recipe!"
            return text
        recipe = crafting_recipes[item_id]
        for material in recipe["materials"]:
            req_qty = recipe["materials"][material]
            if req_qty > self.inventory.get(material, 0):
                text += f"\nYou don't have enough materials to craft {item_data[item_id]["name"].capitalize()}!"
                return text
        for material in recipe["materials"]:
            req_qty = recipe["materials"][material]
            self.inventory[material] -= req_qty
            if self.inventory[material] == 0:
                del self.inventory[material]
        self.inventory[item_id] = self.inventory.get(item_id, 0) + recipe["output_quantity"]
        text += f"\nSuccessfully crafted x{recipe["output_quantity"]} {item_data[item_id]["name"].capitalize()}!"
        return text
    def equip(self, item_id):
        text = ""
        if not item_id in item_data:
            text += "\nUnknown item!"
            return text
        if not item_id in self.inventory:
            text += f"\nYou don't have a {item_data[item_id]["name"].capitalize()}!"
            return text
        if item_data[item_id]["type"] != "equipment":
            text += f"\n{item_data[item_id]["name"].capitalize()} is not equippable!"
            return text
        item_kind = item_data[item_id]["equipment_info"]["type"]
        old_item = self.equipment[item_kind]
        self.equipment[item_kind] = item_id
        self.inventory[item_id] -= 1
        if self.inventory[item_id] == 0:
            del self.inventory[item_id]
        if old_item:
            self.add_to_inventory(old_item)
        text += f"\nEquipped {item_data[item_id]["name"].capitalize()}."
        self.stats = self.set_stats()
        self.hp = min(self.hp, self.stats["maxhp"])
        self.mp = min(self.mp, self.maxmp())
        return text
    def tick(self) -> str:
        text = ""
        text += super().tick()
        self.mp = min(self.mp+10, self.maxmp())
        return text
    def save_data(self):
        self.player_data = {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "equipment": self.equipment,
            "job": self.job,
            "exp": self.exp,
            "inventory": self.inventory,
            "skills": self.skills,
            "hp": self.hp,
            "mp": self.mp,
            "quests": self.quests,
            "completed_quests": self.completed_quests
        }
        with open('PoS/saves/saves.json') as f:
            saves_data = json.load(f)
        saves_data[self.id] = self.player_data
        with open('PoS/saves/saves.json', 'w') as f:
            json.dump(saves_data, f, indent=4)
    def remove_from_inventory(self, item, quantity=1):
        if not item in self.inventory:
            return
        if self.inventory[item] < quantity:
            return
        self.inventory[item] -= quantity
        if self.inventory[item] == 0:
            del self.inventory[item]
    def sell_item(self, item):
        text = ""
        if item not in self.inventory:
            text += "\nYou don't have this item!"
            return text, False
        price = round(item_data[item]["merchant_price"])
        self.remove_from_inventory(item)
        self.add_to_inventory('gold_coin', price)
        text += f"\nSuccessfully sold {item_data[item]["name"].capitalize()}"
        return text, True
    def buy_item(self, item):
        text = ""
        price = round(2*item_data[item]["merchant_price"])
        money_held = self.inventory.get('gold_coin', 0)
        if money_held < price:
            text += "\nYou don't have enough money!"
            return text, False
        self.inventory['gold_coin'] -= price
        self.add_to_inventory(item)
        text += f'\nSuccessfully purchased {item_data[item]["name"]}!'
        return text, True

class Enemy(Entity):
    def __init__(self, kind: str, level: int):
        super().__init__(kind, level)
        self.name = self.kind.capitalize()
    def use_random_skill(self, target) -> str:
        text = ""
        if "stun" in self.debuffs:
            text += f"\n{self.name} is stunned and cannot act!"
            return text
        with open('PoS/src/skills/enemy_skills.json', 'r') as f:
            enemy_skills = json.load(f)
        skill_list = enemy_skills[self.kind]
        skill_det = random.randint(1, 100)
        for skill in skill_list:
            if skill_det <= skill_list[skill]:
                text += self.use_skill(skill, target)
                return text
            skill_det -= skill_list[skill]
    def roll_drops(self):
        possible_loot = loot_tables.get(self.kind, {})
        drops = {}
        for item, drop_info in possible_loot.items():
            if random.randint(1, 100) <= drop_info["chance"]:
                quantity = random.randint(drop_info["min_qty"], drop_info["max_qty"])
                drops[item] = quantity
        return drops
                


    
        
