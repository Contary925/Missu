from src.entity_classes import Player, Enemy
from src.town_loop import town_loop

def main_test(player_data: dict = {}):
    player = Player(player_data)
    player.add_to_inventory('plate_armor')
    town_loop(player)

if __name__ == "__main__":
    main_test()