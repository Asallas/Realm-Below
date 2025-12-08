# intro_pillar.py
import pygame
from typing import Callable, Optional, Tuple

def play_opening(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    player,                        # Player instance (will be displayed)
    boss_factory: Callable[[], object],  # function returning a Boss instance
    bg_surface: Optional[pygame.Surface] = None,
    pillar_spritesheet_path: str = "Spritesheets/BossEnemy/Retro Impact Effect Pack 5 A.png",
    pillar_y: int = 1152,
    pillar_frames: int = 8,
    pillar_frame_w: int = 64,
    pillar_frame_h: int = 64,
    pillar_scale: float = 4.0,
    frame_delay: int = 8,          # ticks per frame at 60 fps
    spawn_frame_index: int = 4,    # spawn boss on this frame (0-based)
    spawn_extra_frames: int = 6,   # extra frames to wait after spawn_frame_index before spawning
    skip_key=pygame.K_SPACE,
    skip_text="Press SPACE to skip"
) -> Tuple[object, object, bool]:
    """
    Plays a blocking intro showing the player and a pillar that animates in the center.
    When the pillar animation reaches 'spawn_frame_index' and the extra wait passes,
    the boss_factory() is called and the boss is returned.

    Returns: (boss_or_None, player, skipped_bool)
    """
    # Load pillar spritesheet
    sheet = pygame.image.load(pillar_spritesheet_path).convert_alpha()

    # Build frame rects and surfaces
    frames = []
    for i in range(pillar_frames):
        rect = pygame.Rect(i * pillar_frame_w, pillar_y, pillar_frame_w, pillar_frame_h)
        frame = sheet.subsurface(rect).copy()
        if pillar_scale != 1:
            w, h = frame.get_size()
            frame = pygame.transform.scale(frame, (int(w * pillar_scale), int(h * pillar_scale)))
        frames.append(frame)

    # Setup positions
    screen_rect = screen.get_rect()
    pillar_center = (screen_rect.centerx, screen_rect.centery)
    # Place player at bottom-center slightly above bottom wall (tweak offset if needed)
    player_start_x = screen_rect.centerx - player.rect.width // 2
    player_start_y = screen_rect.bottom - player.rect.height - 48
    player.rect.topleft = (player_start_x, player_start_y)

    # fonts / skip text
    font = pygame.font.Font(None, 28)
    skip_surf = font.render(skip_text, True, (255, 255, 255))
    skip_rect = skip_surf.get_rect(midbottom=(screen_rect.centerx, screen_rect.bottom - 16))

    # state
    anim_timer = 0
    frame_index = 0
    spawned_boss = None
    skipped = False
    post_spawn_wait = 0
    boss_spawned_flag = False

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == skip_key:
                    skipped = True
                    running = False
                    break

        # update animation timer
        anim_timer += 1
        if anim_timer >= frame_delay:
            anim_timer = 0
            # advance frame unless we've reached last frame and want to hold
            if frame_index < len(frames) - 1:
                frame_index += 1

        # when reached the spawn frame, start counting extra wait then spawn boss once
        if frame_index >= spawn_frame_index and not boss_spawned_flag:
            post_spawn_wait += 1
            if post_spawn_wait >= spawn_extra_frames:
                # spawn boss
                try:
                    spawned_boss = boss_factory()
                except Exception as e:
                    print("boss_factory() raised:", e)
                    spawned_boss = None
                boss_spawned_flag = True
                if spawned_boss is not None:
                    # ensure boss has an image + rect (most Boss constructors set these)
                    if getattr(spawned_boss, "image", None) is None:
                        print("Warning: spawned boss has no 'image' attribute")
                    if getattr(spawned_boss, "rect", None) is None:
                        # try to set a sensible rect
                        spawned_boss.rect = spawned_boss.image.get_rect(center=pillar_center)
                    else:
                        spawned_boss.rect.center = pillar_center

                    # draw one visual frame with the boss, then pause a short moment
                    if bg_surface:
                        screen.blit(bg_surface, (0, 0))
                    else:
                        screen.fill((18, 18, 26))
                    screen.blit(player.image, player.rect)
                    
                    screen.blit(spawned_boss.image, spawned_boss.rect)
                    screen.blit(skip_surf, skip_rect)
                    pygame.display.flip()
                    # short visible delay so the player sees the boss spawn
                    pygame.time.delay(250)

                # after showing boss (or failing to spawn) exit intro
                running = False
                break


        # draw
        if bg_surface:
            screen.blit(bg_surface, (0, 0))
        else:
            screen.fill((18, 18, 26))

        # draw player
        screen.blit(player.image, player.rect)

        # draw pillar frame centered
        pillar_img = frames[frame_index]
        pr = pillar_img.get_rect(center=pillar_center)
        screen.blit(pillar_img, pr)

        # draw skip text
        screen.blit(skip_surf, skip_rect)

        pygame.display.flip()
        clock.tick(60)

        # exit conditions:
        # - user skipped -> break and return None boss
        # - boss spawned and we've shown at least one frame after spawn -> break
        # I choose to break once boss_spawned_flag is True and we've shown it for at least 1 loop
        if skipped:
            break
        if boss_spawned_flag:
            # give one extra frame to let player see the spawned boss
            pygame.time.delay(120)
            running = False

    return spawned_boss, player, skipped
