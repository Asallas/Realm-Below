import pygame, sys

from player import Player

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
player = Player((0,0))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Realm Below")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(pygame.Color('gray'))
    screen.blit(player.image, player.rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()