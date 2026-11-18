from src.add_base_entity_stats import add_base_entity_stats
from src.add_skill import add_skill
from src.add_enemy_drops import add_enemy_drops
from src.add_item_data import add_item_data
from src.add_crafting_recipe import add_crafting_recipe
from src.add_quest import add_quest

add_base_entity_stats('Ogre', 200, 50, 20, {"STUN": 50}, 10, 999, 1)
add_enemy_drops('Ogre', 'gold_coin', 100, 5, 10)
add_item_data("steel_sword", "Steel sword", "Equipment", "A heavy sword made of steel.", {}, {
    "type": "weapon", 
    "atk": 20,
})
add_enemy_drops('Ogre', 'steel_sword', 5, 1, 1)
add_item_data("plate_armor", "Plate armor", "Equipment", "A heavy plate armor, provides high DEF and increases resistance to STUN.", {}, {
    "type": "armor",
    "def": 10,
    'resistance': {
        "STUN": 25
    }
})
add_enemy_drops('Ogre', 'plate_armor', 2, 1, 1)
add_item_data("ogre_meat", "Ogre meat", "Raw meat you got from an Ogre. Very valuable, given how rare it is.", {}, {}, 100)
add_enemy_drops('Ogre', 'ogre_meat', 20, 1, 2)
add_enemy_drops('Ogre', 'medium_healing_potion', 20, 1, 2)
add_quest('Frank the merchant', 'Ogre hunter', {
    "conditions": {
        "min_level": 10,
        "max_level": 50,
    },
    "objectives": {
        "collect": {
            "ogre_meat": 1
        }
    },
    "rewards": {
        "EXP": 1000,
        "skills": ["Stun attack"]
    },
    "repeatable" : 0,
    "accept_text": "Hey, I heard you've truly been a nightmare for these Orks. However, there's something stronger than them... Yeah, Ogres! There's a rumor that there is one in our lands. If you manage to defeat it... Well, I'll reward you with a new skill! What would you say?",
    "report_text": "Wow, you really managed to defeat him! That's great! Here's your new skill - it deals increased damage and may stun the target if you land a good hit... Put it to a good use!"
})

# add_item_data('gold_coin', 'Gold coin', 'Material', 'Gold coins - currency.', {}, {})
# add_enemy_drops('Goblin', 'gold_coin', 50, 1, 5)


# add_item_data('cloth_piece', 'Cloth piece', 'Material', 'A piece of cloth.')
# add_item_data('goblin_ear', 'Goblin ear', 'Material', 'Goblin ear')
# add_item_data('dull_dagger', 'Dull dagger', 'Equipment', 'A dull dagger. Can be used as a weapon.', {}, 
#               {
#                 'type': 'weapon',
#                 'atk': 5
#               })
# add_item_data('small_healing_potion', 'Small healing potion', 'Consumable', 'A healing potion. Recovers 50 HP.', 
#               {
#                   'hp': 50,
#               }, {})


# add_skill("Defend", "Buff", "10", 
#           {
#               "Duration": 2,
#               "Stat_buffs": {
#                   "DEF": 3
#               }
#           }, "Increases DEF for 2 turns")
# add_skill("Stun attack", "Attack", "50", 
#           {
#               "Multiplier": 150,
#               "Debuffs": {
#                   "STUN": {
#                       "Chance": 50,
#                       "Duration": 1
#                   }
#               }
#           }, "Deals more damage to the target. Can apply STUN at a chance.")
# add_skill("Attack", "Attack", "0", 
#           {
#               "Multiplier": 100,
#           }, "Basic attack. Deals damage to the target.")
# add_skill("Heal", "Buff", "25",
#           {
#                 "Healing": 20,
#           }, "A healing spell. Recovers 20% HP to the entity")
