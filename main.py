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

# --------------- Resources & Environment -------------------
TITLE_IMAGE_PATH = "Environment/RealmBelowTItleImage.png"
raw_title_image = pygame.image.load(TITLE_IMAGE_PATH).convert()
title_image = pygame.transform.smoothscale(raw_title_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

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

# ---------- Action icon UI resources ----------
# expected icon filenames (you can change these to your filenames)
ICON_FILENAMES = ["Ativo 2.png", "Ativo 15.png", "Ativo 14.png", "Ativo 7.png"]
ICON_DIR = "Environment/64/PNG"
ICON_SIZE = 64
ICON_SPACING = 24  # horizontal space between icons

action_icons = []
for fname in ICON_FILENAMES:
    path = f"{ICON_DIR}/{fname}"
    try:
        surf = pygame.image.load(path).convert_alpha()
        # scale to 64x64 if needed
        if surf.get_width() != ICON_SIZE or surf.get_height() != ICON_SIZE:
            surf = pygame.transform.smoothscale(surf, (ICON_SIZE, ICON_SIZE))
        action_icons.append(surf)
    except Exception as e:
        # missing file -> append None as placeholder
        print(f"[UI] Failed loading icon '{path}': {e}")
        action_icons.append(None)

ui_key_font = pygame.font.Font(None, 28)
ui_hint_font = pygame.font.Font(None, 28)

# ----------------- Entities ------------------

def boss_factory():
    b = Boss((0,0), .5)
    b.last_special_start = pygame.time.get_ticks()
    return b

def make_initial_game_state(play_intro=False):
    """
    Returns (player, boss, all_sprites, enemies).
    If play_intro==True this will run play_opening() and may return a boss_from_intro.
    Note: play_opening is blocking (plays intro) — only call when desired.
    """
    # create player
    player = Player((0,0), 1)
    player.facing = "north"
    player.health = 300
    player.max_health = 300

    boss = None
    if play_intro:
        # play_intro: let the intro return the boss and possibly modify player
        boss_from_intro, player_after_intro, skipped = play_opening(
            screen=screen, clock=clock, player=player, boss_factory=boss_factory, bg_surface=background,
            pillar_spritesheet_path="Spritesheets/BossEnemy/Retro Impact Effect Pack 5 A.png",
            pillar_y=1152, pillar_frames=8, pillar_frame_w=64, pillar_frame_h=64,
            pillar_scale=4, frame_delay=8, spawn_frame_index=4, spawn_extra_frames=6, skip_key=pygame.K_SPACE
        )
        if boss_from_intro:
            boss = boss_from_intro
            player = player_after_intro
            boss.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            # fallback
            boss = Boss((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), .5)
            boss.last_special_start = pygame.time.get_ticks()
    else:
        boss = Boss((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), .5)
        boss.last_special_start = pygame.time.get_ticks()

    
    boss.health = 500
    boss.max_health = 500

    # groups
    all_sprites = pygame.sprite.Group(player, boss)
    enemies = pygame.sprite.Group()   # keep boss out of enemies if you treat boss specially

    return player, boss, all_sprites, enemies

TEMP_COLOR = (48,69,41)

# --------------- Title screen UI -------------------
BUTTON_W = 420
BUTTON_H = 90
BUTTON_Y_OFFSET = 80  # space from bottom
button_font = pygame.font.Font(None, 64)
title_font = pygame.font.Font(None, 96)
hint_font = pygame.font.Font(None, 28)

def draw_title(screen):
    # draw background image (fills entire screen)
    screen.blit(title_image, (0,0))

    # draw title text (optional, on top of image)
    title_surf = title_font.render("REALM BELOW", True, (255, 240, 200))
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 140))
    screen.blit(title_surf, title_rect)

    # button rect centered bottom
    bx = (SCREEN_WIDTH - BUTTON_W) // 2
    by = SCREEN_HEIGHT - BUTTON_Y_OFFSET - BUTTON_H
    button_rect = pygame.Rect(bx, by, BUTTON_W, BUTTON_H)

    # hover effect
    mx, my = pygame.mouse.get_pos()
    is_hover = button_rect.collidepoint((mx, my))
    color = (180, 40, 40) if is_hover else (140, 20, 20)

    pygame.draw.rect(screen, color, button_rect, border_radius=12)
    pygame.draw.rect(screen, (255,255,255), button_rect, 3, border_radius=12)

    text = button_font.render("START", True, (255,255,255))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    hint = hint_font.render("Press Enter or Space to start. ESC to quit.", True, (220,220,220))
    hint_rect = hint.get_rect(center=(SCREEN_WIDTH//2, by + BUTTON_H + 30))
    screen.blit(hint, hint_rect)

    return button_rect


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

# ------------ Helper
def draw_action_ui(screen):
    """
    Draw 4 icons centered at bottom of the screen with key labels beneath them,
    plus a left-bottom hint for dodge (L_SHIFT).
    """
    # only run if icons loaded (we still draw placeholders if None)
    total_icons = len(action_icons)
    if total_icons == 0:
        return

    icon_w = ICON_SIZE
    icon_h = ICON_SIZE
    spacing = ICON_SPACING

    total_width = total_icons * icon_w + (total_icons - 1) * spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_icon = SCREEN_HEIGHT - icon_h - 48  # 48 px margin from bottom; tweak as desired

    # Draw icon background strip (subtle)
    strip_h = icon_h + 64
    strip_rect = pygame.Rect(start_x - 24, y_icon - 18, total_width + 48, strip_h)
    overlay = pygame.Surface((strip_rect.width, strip_rect.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))  # semi transparent dark strip
    screen.blit(overlay, (strip_rect.x, strip_rect.y))

    # Draw icons and labels
    keys = ['Q', 'W', 'Z', 'G']
    for i, icon in enumerate(action_icons):
        x = start_x + i * (icon_w + spacing)
        # icon bg
        icon_bg = pygame.Rect(x - 6, y_icon - 6, icon_w + 12, icon_h + 12)
        pygame.draw.rect(screen, (30,30,30,200), icon_bg, border_radius=6)
        pygame.draw.rect(screen, (200,200,200), icon_bg, 2, border_radius=6)

        if icon:
            screen.blit(icon, (x, y_icon))
        else:
            # placeholder
            pygame.draw.rect(screen, (90,90,90), (x, y_icon, icon_w, icon_h))
            ph_text = ui_key_font.render("NoImg", True, (220,220,220))
            screen.blit(ph_text, (x + (icon_w - ph_text.get_width())//2, y_icon + (icon_h - ph_text.get_height())//2))

        # key label under icon
        key_label = ui_key_font.render(keys[i], True, (240,240,240))
        key_x = x + icon_w//2 - key_label.get_width()//2
        key_y = y_icon + icon_h + 6
        screen.blit(key_label, (key_x, key_y))

    # Bottom-left hint for dodge
    hint_text = ui_hint_font.render("L_SHIFT = Dodge", True, (220,220,220))
    hint_pos = (16, SCREEN_HEIGHT - 36)
    # draw small backdrop for readability
    hint_bg = pygame.Surface((hint_text.get_width()+10, hint_text.get_height()+6), pygame.SRCALPHA)
    hint_bg.fill((0,0,0,140))
    screen.blit(hint_bg, (hint_pos[0]-5, hint_pos[1]-3))
    screen.blit(hint_text, hint_pos)

#---------------- Restart ------------
def restart_game(play_intro=True):
    """
    Tear down current dynamic state and return fresh objects. Uses make_initial_game_state.
    play_intro: if True, replay the intro sequence (blocking).
    """
    # Clear any dynamic containers that might hold sprites (so objects get GC'd if referenced)
    # We won't destroy tile_cache/background which are reused.

    new_player, new_boss, new_all_sprites, new_enemies = make_initial_game_state(play_intro=play_intro)

    # Return the new objects so caller can rebind variables
    return new_player, new_boss, new_all_sprites, new_enemies

# ------------- Main Loop ----------------
on_title = True
running = True
game_over = False
you_win = False

# ------------ End Screen ----------------
font = pygame.font.Font(None, 160)
game_over_text = font.render("GAME OVER", True, (255, 0, 0))
game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

win_text = font.render("YOU WIN!", True, (0, 255, 0))
win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

while running:

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # TITLE SCREEN
    if on_title:
        screen.fill((0,0,0))
        start_button = draw_title(screen)
        pygame.display.flip()

        # handle title events from the single event fetch above
        for ev in events:
            if ev.type == pygame.QUIT:
                running = False
                on_title = False
                break
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if start_button.collidepoint(ev.pos):
                    # Start game and play intro by default
                    player, boss, all_sprites, enemies = make_initial_game_state(play_intro=True)
                    on_title = False
                    game_over = False
                    you_win = False
                    break
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    player, boss, all_sprites, enemies = make_initial_game_state(play_intro=True)
                    on_title = False
                    game_over = False
                    you_win = False
                    break
        clock.tick(60)
        continue

    if all_sprites is None:
        player, boss, all_sprites, enemies = make_initial_game_state(play_intro=True)
    if game_over or you_win:
        if game_over:
            screen.blit(game_over_text, game_over_rect)
            hint = "Press R to Restart (with/without intro), or ESC to Quit"
        else:
            screen.blit(win_text, win_rect)
            hint = "Press R to Play Again (with/without intro), or ESC to Quit"

        # small hint text
        hint_font = pygame.font.Font(None, 32)
        hint_surf = hint_font.render(hint + "  (press I to restart + play intro)", True, (200,200,200))
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        screen.blit(hint_surf, hint_rect)

        pygame.display.flip()

        # Blocking wait loop: this guarantees single key press handling
        waiting_for_input = True
        while waiting_for_input:
            ev = pygame.event.wait()   # blocks until an event arrives
            if ev.type == pygame.QUIT:
                running = False
                waiting_for_input = False
                break
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                    waiting_for_input = False
                    break
                if ev.key == pygame.K_r:
                    # restart WITHOUT intro
                    player, boss, all_sprites, enemies = restart_game(play_intro=False)
                    game_over = False
                    you_win = False
                    waiting_for_input = False
                    break
                if ev.key == pygame.K_i:
                    # restart AND play intro (blocking)
                    player, boss, all_sprites, enemies = restart_game(play_intro=True)
                    game_over = False
                    you_win = False
                    waiting_for_input = False
                    break
            # ignore other events while paused
        # continue main loop
        clock.tick(30)
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
                        if player.blocking or player.block_holding:
                            player.take_damage(0, enemy.facing)
                        else:
                            player.take_damage(10, enemy.facing)
                        enemy.attack_registered = True
                        print(f"{enemy.__class__.__name__} hit the player!")

            if hasattr(enemy, "projectiles"):
                for projectile in list(enemy.projectiles):
                    if projectile.rect.colliderect(player.hitbox):
                        if player.blocking or player.block_holding:
                            player.take_damage(0, enemy.facing)
                        else:
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
                        if player.blocking or player.block_holding:
                            player.take_damage(0, boss.facing)
                        else:
                            player.take_damage(40, boss.facing)
            if getattr(boss, "attack_active", False) and getattr(boss, "attack_hitbox", None):
                poly_bbox = get_polygon_bounding_box(boss.attack_hitbox)
                if polygon_rect_collision(boss.attack_hitbox, player.hitbox):
                    if player.blocking or player.block_holding:
                        player.take_damage(0, boss.facing)
                    else:
                        player.take_damage(20, boss.facing)
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
        # sprite.draw_hitbox(screen)

    for enemy in enemies:
        if hasattr(enemy, "projectiles"):
            enemy.projectiles.draw(screen)
    
    # draw action UI only when actually in the game (not title and not end screens)
    if not on_title and not game_over and not you_win:
        draw_action_ui(screen)

        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()