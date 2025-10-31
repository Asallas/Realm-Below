import pygame
from player import Player  # or from enemy import Enemy, etc.
from enemys import MeleeEnemy, RangeEnemy
from boss import Boss

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animation Viewer + Facing Rotation + Pause")

clock = pygame.time.Clock()
running = True

# --- Spawn Entity ---
entity = MeleeEnemy((WIDTH // 2 - 500, HEIGHT // 2 - 500), 0.25)

# --- Facing Direction Setup ---
facing_order = [
    "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest"
]
facing_index = 4  # start facing south
entity.facing = facing_order[facing_index]

# --- Animation Setup ---
animations = list(entity.sheets.keys())
current_index = 0
entity.set_animation(animations[current_index])
print(f"Now playing: {animations[current_index]} ({entity.facing})")

# --- Timing Controls ---
animation_start_time = pygame.time.get_ticks()
animation_duration = 1500  # ms
auto_cycle = True  # 🔹 Auto-cycle enabled by default
font = pygame.font.SysFont(None, 32)

def draw_text(surface, text, pos, color=(255, 255, 255)):
    surface.blit(font.render(text, True, color), pos)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # --- Manual animation cycle ---
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                current_index = (current_index + 1) % len(animations)
                entity.set_animation(animations[current_index])
                entity.frame_index = 0
                animation_start_time = pygame.time.get_ticks()
                print(f"Now playing: {animations[current_index]} ({entity.facing})")

            # --- Toggle pause/resume auto cycling ---
            elif event.key == pygame.K_p:
                auto_cycle = not auto_cycle
                print(f"Auto-cycle {'resumed' if auto_cycle else 'paused'}")

            # --- Facing rotation ---
            elif event.key == pygame.K_RIGHT:
                facing_index = (facing_index + 1) % len(facing_order)
                entity.facing = facing_order[facing_index]
                print(f"Facing: {entity.facing}")

            elif event.key == pygame.K_LEFT:
                facing_index = (facing_index - 1) % len(facing_order)
                entity.facing = facing_order[facing_index]
                print(f"Facing: {entity.facing}")

    # --- Auto-cycle animations (if enabled) ---
    if auto_cycle:
        now = pygame.time.get_ticks()
        if now - animation_start_time >= animation_duration:
            current_index = (current_index + 1) % len(animations)
            entity.set_animation(animations[current_index])
            entity.frame_index = 0
            animation_start_time = now
            print(f"Now playing: {animations[current_index]} ({entity.facing})")

    # --- Update animation ---
    entity.update_animations()

    # --- Draw ---
    screen.fill((25, 25, 35))
    screen.blit(entity.image, entity.rect)

    draw_text(screen, f"Animation: {animations[current_index]}", (20, 20))
    draw_text(screen, f"Facing: {entity.facing}", (20, 50))
    draw_text(screen, f"Auto-cycle: {'ON' if auto_cycle else 'OFF'}", (20, 80))
    draw_text(screen, "← / → Rotate  |  Enter/Space Next Anim  |  P Pause/Resume  |  ESC Quit", (20, 120))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
