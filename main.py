import pygame, sys

from player import Player
from enemys import MeleeEnemy, RangeEnemy
from boss import Boss
from environment import load_map, build_bg_surface
from intro import play_opening
from misc_sprites import *

pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Realm Below")
clock = pygame.time.Clock()

# --------------- Environment -------------------
tileset = pygame.image.load("Environment/RF_Catacombs_v1.0/mainlevbuild.png")
TILE_SCALE = 2
TILE_RECTS = {
    "basic_floor": pygame.Rect(736, 208, 32, 48),
    "Grate": pygame.Rect(487, 202, 81, 81),
    "bottom_wall": pygame.Rect(64, 43, 192, 16),
    "facing_wall": pygame.Rect(64, 415, 192, 78),
    "facing_wall2": pygame.Rect(64, 335, 192, 78),
    "left_wall": pygame.Rect(306, 41, 16, 48),
    "right_wall": pygame.Rect(368, 41, 16, 48),
    "door_frame": pygame.Rect(496, 32, 96, 78),
    "door": pygame.Rect(640, 6, 80, 90)
}
LEFT_WALL = 16
RIGHT_WALL = 16
TOP_WALL = 78
BOTTOM_WALL = 16
playable_rect = pygame.Rect(LEFT_WALL, TOP_WALL, SCREEN_WIDTH - LEFT_WALL - RIGHT_WALL, SCREEN_HEIGHT - TOP_WALL - BOTTOM_WALL)

loaded_tiles = load_map("environment_layout.json")
background, tile_cache = build_bg_surface(loaded_tiles, tileset, TILE_RECTS, TILE_SCALE, (SCREEN_WIDTH, SCREEN_HEIGHT))

# ----------------- Entities ------------------
player = Player((0,0), 1)
player.facing = "north"
player.health = 200
player.max_health = 200

# -------------- Boss Spawning -------------
def boss_factory():
    b = Boss((0,0), .5)
    b.last_special_start = pygame.time.get_ticks()
    return b

boss_from_intro, player, skipped = play_opening(
    screen=screen, clock=clock, player=player, boss_factory=boss_factory, bg_surface=background,
    pillar_spritesheet_path="Spritesheets/BossEnemy/Retro Impact Effect Pack 5 A.png",
    pillar_y=1152, pillar_frames=8, pillar_frame_w=64, pillar_frame_h=64, 
    pillar_scale=4, frame_delay=8, spawn_frame_index=4, spawn_extra_frames=6, skip_key=pygame.K_SPACE
)
if boss_from_intro:
    boss = boss_from_intro
    boss.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
else:
    boss = Boss((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), .5)


all_sprites = pygame.sprite.Group(player, boss)
enemies = pygame.sprite.Group()


TEMP_COLOR = (48,69,41)

# ------------- Collision Detection Helper Functions ---------------
def polygon_rect_collision(polygon_points, rect):
    """
    More efficient polygon vs rect collision:
     - compute bounding box of polygon and of rect,
     - compute their intersection region,
     - create a small surface & masks only for that intersection, then test overlap.
    Returns True if they overlap.
    """
    if not polygon_points:
        return False

    # polygon bounding box
    pxs = [p[0] for p in polygon_points]
    pys = [p[1] for p in polygon_points]
    poly_bb = pygame.Rect(min(pxs), min(pys), max(pxs)-min(pxs), max(pys)-min(pys))

    # fast reject if bounding boxes don't overlap
    if not poly_bb.colliderect(rect):
        return False

    # intersection rect between polygon bb and target rect
    inter = poly_bb.clip(rect)
    if inter.width == 0 or inter.height == 0:
        return False

    # shift polygon points into the intersection-space (so mask origin is small)
    shifted_poly = [(int(x - inter.x), int(y - inter.y)) for (x, y) in polygon_points]

    # build tiny surfaces only for the intersection
    poly_surf = pygame.Surface((inter.width, inter.height), pygame.SRCALPHA)
    pygame.draw.polygon(poly_surf, (255,255,255), shifted_poly)

    rect_surf = pygame.Surface((inter.width, inter.height), pygame.SRCALPHA)
    # draw rectangle in rect_surf at the rect's position relative to inter
    rect_local = pygame.Rect(rect.x - inter.x, rect.y - inter.y, rect.width, rect.height)
    pygame.draw.rect(rect_surf, (255,255,255), rect_local)

    poly_mask = pygame.mask.from_surface(poly_surf)
    rect_mask = pygame.mask.from_surface(rect_surf)

    return poly_mask.overlap(rect_mask, (0,0)) is not None


def get_polygon_bounding_box(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

# ------------- Main Loop ----------------
running = True
game_over = False
you_win = False

font = pygame.font.Font(None, 160)
game_over_text = font.render("GAME OVER", True, (255, 0, 0))
game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

win_text = font.render("YOU WIN!", True, (0, 255, 0))
win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False
    
    if game_over or you_win:
        screen.fill((0,0,0))
        if game_over:
            screen.blit(game_over_text, game_over_rect)
        elif you_win:
            screen.blit(win_text, win_rect)
        pygame.display.flip()
        clock.tick()
        continue



    if keys[pygame.K_g]:
        player.block()
    else:
        player.release_block()
    if not player.blocking and not player.block_holding and not player.is_dying:
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
    
    if boss.attack_seq_state is None:
        boss.target = player.rect
    else:
        boss.target = None
    
    for enemy in enemies:
        enemy.target = player.rect  

    if (boss.summon_state is None and boss.attack_seq_state is None and pygame.time.get_ticks() - boss.last_special_start >= 30000):
        boss.start_attack_sequence()
        boss.last_special_start = pygame.time.get_ticks()

    # ----------- Updates -------------
    all_sprites.update()
    for sprite in all_sprites:
        sprite.update_knockback()
        sprite.update_death()
        sprite.update_invulnerability()
        sprite.update_hit_stun()
    
    # ------ Projectile Update ======
    for enemy in enemies:
        if hasattr(enemy, "projectiles"):
            enemy.projectiles.update()

    # -------------- Player Attack collision ---------------------
    if player.attack_active and player.attack_hitbox:
        poly_bbox = get_polygon_bounding_box(player.attack_hitbox)
        if boss and not boss.is_dead and not boss.is_dying and getattr(boss, "hitbox", None):
            if not getattr(boss, "invulnerable", False):
                if not player.attack_registered:
                    if poly_bbox.colliderect(boss.hitbox):
                        if polygon_rect_collision(player.attack_hitbox, boss.hitbox):
                            boss.take_damage(20, player.facing)
                            player.attack_registered = True
                            print("Boss was hit")
        for enemy in enemies:
            if enemy.is_dead or enemy.is_dying:
                continue
            if not getattr(enemy, "hitbox", None):
                continue
            if getattr(enemy, "invulnerable", False):
                continue

            if not player.attack_registered:    
                if poly_bbox.colliderect(enemy.hitbox):
                    if polygon_rect_collision(player.attack_hitbox, enemy.hitbox):
                        enemy.take_damage(20, player.facing)
                        player.attack_registered = True
                        print("That's a hit")
    
    # ---------------- Enemy Attack Collision ---------------
    for enemy in enemies:
        if enemy.is_dead or enemy.is_dying:
            continue
        if player.hitbox:
            if getattr(enemy, "attack_active", False) and getattr(enemy, "attack_hitbox", None):
                poly_bbox = get_polygon_bounding_box(enemy.attack_hitbox)
                if poly_bbox.colliderect(player.hitbox):
                    if polygon_rect_collision(enemy.attack_hitbox, player.hitbox):
                        # Deal damage to player
                        player.take_damage(10, enemy.facing)
                        enemy.attack_registered = True
                        print(f"{enemy.__class__.__name__} hit the player!")

            if hasattr(enemy, "projectiles"):
                for projectile in list(enemy.projectiles):
                    if projectile.rect.colliderect(player.hitbox):
                        player.take_damage(10, enemy.facing)
                        enemy.projectiles.remove(projectile)
                        enemy.attack_registered = True
                        print(f"Projectile from {enemy.__class__.__name__} hit player!")

                    # Optionally remove projectiles off-screen
                    if (projectile.rect.right < 0 or projectile.rect.left > SCREEN_WIDTH or
                        projectile.rect.bottom < 0 or projectile.rect.top > SCREEN_HEIGHT):
                        enemy.projectiles.remove(projectile)
    
    if boss and getattr(boss, "ward_failed", False):
        if not player.is_dead and not player.is_dying:
            player.take_damage(player.max_health, boss.facing)

    if boss and not boss.is_dead and not boss.is_dying:
        if player.hitbox:
            if getattr(boss, "wards", None):
                for ward in list(boss.wards):
                    if hasattr(ward, "hitbox"):
                        if ward.hitbox.colliderect(player.hitbox):
                            ward.resume()
            if hasattr(boss, "explosions"):
                for exp in list(boss.explosions):
                    if exp.hitbox.colliderect(player.hitbox):
                        player.take_damage(40, player.facing)
            if getattr(boss, "attack_active", False) and getattr(boss, "attack_hitbox", None):
                poly_bbox = get_polygon_bounding_box(boss.attack_hitbox)
                if polygon_rect_collision(boss.attack_hitbox, player.hitbox):
                    player.take_damage(10, boss.facing)
                    boss.attack_registered = True
                    print("Boss hit player")

    if boss and getattr(boss, "pending_spawns", None):
        if not hasattr(boss, "_spawn_refs_total") or boss._spawn_refs_total is None:
            boss._spawn_refs_total = []

        for e in boss.pending_spawns:
            all_sprites.add(e)
            enemies.add(e)
            boss._spawn_refs_total.append(e)


        # clear pending_spawns so we don't re-add
        boss.pending_spawns = []
        print("Main: added boss minions to groups")

    # If boss is waiting on spawned minions, check if they're all dead
    if boss and boss.summon_state == "spawned_waiting":
        # if any of the spawn_refs still exist in enemies group and are not dead -> wait
        alive_left = 0
        for e in boss._spawn_refs_total:
            # treat "dead" if attribute is_dead True OR not in enemies group
            if getattr(e, "is_dead", False):
                continue
            if e in enemies:
                alive_left += 1

        if alive_left == 0:
            # all minions are gone -> resume boss
            boss.summon_state = None
            boss.invulnerable = False
            boss.locked = False
            boss.enable_hitbox(manual=True)
            boss._spawn_refs_total = []
            print("Main: boss minions defeated; boss resumes")    
    for sprite in all_sprites:
        sprite.clamp_to_bounds(playable_rect)
    for enemy in list(enemies):
        if enemy.is_dead:
            enemies.remove(enemy)
            all_sprites.remove(enemy)
    
    if player.is_dead:
        all_sprites.remove(player)
        game_over = True
        continue

    if len(enemies) == 0 and boss.is_dead:
        you_win = True
        continue

    screen.fill(TEMP_COLOR)
    screen.blit(background, (0,0))
    for sprite in all_sprites:
        if(isinstance(sprite, Boss)):
            sprite.draw(screen)
        else:
            screen.blit(sprite.image, sprite.rect)
        #sprite.draw_hitbox(screen)

    for enemy in enemies:
        if hasattr(enemy, "projectiles"):
            enemy.projectiles.draw(screen)
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()