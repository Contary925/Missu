# Path of Steel

A text-based RPG built in Python featuring object-oriented design and data-driven game mechanics.

## Features

- **Turn-Based Combat System:** Dynamic combat calculations accounting for base stats, attack power, defense, and status resistances.
- **Data-Driven Architecture:** All entity baselines, enemy spawn weights, items, quests, and drop tables are decoupled into JSON configurations for easy extensibility.
- **Dynamic Level Scaling & Weighted Spawns:** Enemies spawn based on player level brackets using weighted probability distributions.
- **Progression & Quest System:** Track quests, gain experience, level up, and encounter rare high-level encounters (such as the Ogre boss).
- **Inventory & Crafting:** Manage equipment, items, and crafting materials.

## Architecture & Project Structure

```text
.
├── helper.py                               # helper function for adding new enemies, quests, etc. using the add_ functions in src/
├── path_of_steel.py                        # game entry point
├── README.md
├── saves
│   └── saves.json                          # player save files
├── src
│   ├── add_base_entity_stats.py            # functions for helper.py to add new data
│   ├── add_crafting_recipe.py
│   ├── add_enemy_drops.py
│   ├── add_item_data.py
│   ├── add_quest.py
│   ├── add_skill.py
│   ├── battle_loop.py                      # main combat loop
│   ├── combat_items_menu.py                # menu for using items in battle
│   ├── crafting_menu.py                    # menu for crafting in town
│   ├── entity_classes.py                   # OOP models for players and enemies
│   ├── inventory_menu.py                   # menu for managing items in inventory 
│   ├── items
│   │   └── item_data.json                  # data for all items
│   ├── merchant_menu.py                    # menu for merchants in town
│   ├── NPC
│   │   └── npc_info.json                   # data for all NPCs
│   ├── quest_menu.py                       # menu for quests at NPCs
│   ├── quests
│   │   └── quests.json                     # all quests data
│   ├── quests.py
│   ├── recipes
│   │   └── recipes.json                    # all crafting recipes data
│   ├── show_character_sheet.py             # menu for showing character stats
│   ├── skills
│   │   ├── enemy_skills.json               # probabilities of using certain skills for every enemy
│   │   ├── jobs.json                       # jobs data such as available skills per job
│   │   └── skill_data.json                 # data for all skills
│   ├── skills_menu.py                      # menu for using skills in battle
│   ├── spawn_random_enemy.py               # logic for spawning enemies based off player level
│   ├── stats
│   │   ├── entity_base_stats.json          # base stats of players and enemies
│   │   ├── exp.json                        # base exp of every enemy
│   │   ├── level_scaling.json              # data about how stats increase based off player/enemy level
│   │   └── loot_tables.json                # loot tables of every enemies
│   └── town_loop.py                        # main game loop (town)
└── test.py                                 # test script, play as guest                
```

## Getting Started

### Prerequisites
- **Python 3.10+** (Standard library only; no external dependencies required)
- **Git**

### Installation
```bash
git clone https://github.com/Contary925/path-of-steel.git
cd path-of-steel
```

### Run the Game
```bash
python3 path_of_steel.py                # normal game
python3 test.py                         # test mode, play as guest
```

## Future Roadmap

- [ ] Expanded status effect system (Poison, Burn, Freeze).
- [ ] Interactive ASCII dungeon map navigation.
- [ ] Pygame-based graphical frontend.

## License

This project is open source and available under the [MIT License](LICENSE).