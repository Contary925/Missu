from test import main_test
import json
from src.town_loop import town_loop
from src.entity_classes import Player
with open('saves/saves.json') as f:
    saves = json.load(f)

print('Welcome to Path of Steel!')
while True:
    name = input('Please, enter your name > ')
    if name in saves:
        print('[0] Go back')
        print(f'[1] Play as {name}')
        choice = input(f'Character data was found. Continue to play as {name}? > ')
        match choice:
            case '0':
                continue
            case '1':
                print(f"Welcome back, {name}!")
                player_data = saves[name]
                break
    else:
        print('[0] Go back')
        print(f'[1] Play as {name}')
        choice = input(f'Character data was not found. Start a new game as {name}? > ')
        match choice:
            case '0':
                continue
            case '1':
                print(f"Welcome, {name}!")
                player_data = {
                    "Name": name
                }
                break

player = Player(player_data)
town_loop(player)