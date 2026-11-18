import sys
import pygame

def main():
    pygame.init()

    #window init
    window_width, window_height = 800, 600
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Path of Steel - Engine Test")

    #clock init
    clock = pygame.time.Clock()

    #main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((25, 25, 35))
        pygame.display.flip()
        clock.tick(60)

    #exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__" :
    main();