import pygame, sys

from player import Player

pygame.init()
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
player = Player((SCREEN_WIDTH / 2 - 32, SCREEN_HEIGHT / 2 - 32), 2)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Realm Below")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    player.handle_event(event)
    screen.fill(pygame.Color('gray'))
    screen.blit(player.image, player.rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()