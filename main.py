import pygame, sys

from player import Player
from enemys import MeleeEnemy, RangeEnemy
from boss import Boss

pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Realm Below")
clock = pygame.time.Clock()

# ----------- Entities ------------------
player = Player((0,0), 1)
enemy1 = Boss((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), .5)
enemy2 = MeleeEnemy((SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2 - 200), .75)

all_sprites = pygame.sprite.Group(player, enemy1, enemy2)
enemies = pygame.sprite.Group(enemy1, enemy2)


TEMP_COLOR = (48,69,41)

# ------------- Collision Detection Helper Functions ---------------
def polygon_rect_collision(polygon_points, rect):
    poly_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(poly_surface, (255,255,255), polygon_points)
    poly_mask = pygame.mask.from_surface(poly_surface)

    rect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(rect_surface, (255,255,255), rect)
    rect_mask = pygame.mask.from_surface(rect_surface)

    return poly_mask.overlap(rect_mask, (0,0)) is not None

def get_polygon_bounding_box(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

enemies.remove(enemy1)
all_sprites.remove(enemy1)
# ------------- Main Loop ----------------
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
    for enemy in enemies:
        enemy.target = player.rect  

    # ----------- Updates -------------
    all_sprites.update()
    for sprite in all_sprites:
        sprite.update_knockback()
        sprite.update_death()
        sprite.update_invulnerability()
        sprite.update_hit_stun()

    # -------------- Player Attack collision ---------------------
    if player.attack_active and player.attack_hitbox:
        for enemy in enemies:
            if enemy.is_dead or enemy.is_dying:
                continue

            poly_bbox = get_polygon_bounding_box(player.attack_hitbox)
            if not player.attack_registered:    
                if poly_bbox.colliderect(enemy.hitbox):
                    if polygon_rect_collision(player.attack_hitbox, enemy.hitbox):
                        enemy.take_damage(20, player.facing)
                        player.attack_registered = True
                        print("That's a hit")
    
    
    for enemy in list(enemies):
        if enemy.is_dead:
            enemies.remove(enemy)
            all_sprites.remove(enemy)
    

    screen.fill(TEMP_COLOR)

    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)
        sprite.draw_healthbar(screen)

    if enemy.attack_active and enemy.attack_hitbox:
        enemy.draw_translucent_polygon(screen, enemy.attack_hitbox, (255, 0, 0, 100))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()