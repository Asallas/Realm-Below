import pygame, sys

from player import Player

pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Realm Below")
clock = pygame.time.Clock()

player = Player((0,0), .5)

target_size = (500,500)
target_rect = pygame.Rect(
    (SCREEN_WIDTH // 2 - target_size[0] // 2,
     SCREEN_HEIGHT // 2 - target_size[1] // 2),
     target_size
)
TEMP_COLOR = (48,69,41)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.draw.rect(screen, (0,255,0), (100,500,100,100))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_g]:
        player.block()
    else:
        player.release_block()
    if not player.blocking and not player.block_holding:
        if keys[pygame.K_w]:
            player.attack()
        elif keys[pygame.K_q]:
            player.attack2()
        elif keys[pygame.K_z]:
            player.counter()
        elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            player.move('northeast')
        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            player.move('northwest')
        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            player.move('southeast')
        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            player.move('southwest')
        elif keys[pygame.K_UP]:
            player.move('north')
        elif keys[pygame.K_DOWN]:
            player.move('south')
        elif keys[pygame.K_RIGHT]:
            player.move('east')
        elif keys[pygame.K_LEFT]:
            player.move('west')
        elif keys[pygame.K_LSHIFT]:
            player.roll()
        else:
            player.stand()
    
    player.update()

    if player.hitbox and player.hitbox.colliderect(target_rect):
        target_color = pygame.Color("red")
    else:
        target_color = pygame.Color("green")
    

    screen.fill(TEMP_COLOR)
    
    pygame.draw.rect(screen, target_color, target_rect)

    screen.blit(player.image, player.rect)

    player.draw(screen)

    pygame.draw.rect(screen, pygame.Color("blue"), player.rect,2)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()