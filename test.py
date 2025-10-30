import pygame, sys, random
from enemys import RangeEnemy

pygame.init()

# --- Basic window setup ---
WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enemy Facing + Hitbox Test")

clock = pygame.time.Clock()

# --- Create an enemy instance ---
enemy = RangeEnemy((WIDTH//2 - 128, HEIGHT//2 - 128), .5)

# Optional — set target to None so it doesn’t chase anything
enemy.target = None

# --- Rotation setup ---
DIRECTIONS = [
    "north", "south", "east", "west", "northeast", "northwest", "southeast",
    "southwest"
]
direction_index = 0
rotate_timer = 0
rotate_interval = 2000  # milliseconds

# --- Debug: visualize hitbox ---
def draw_hitbox(surface, rect, color=(0, 255, 0)):
    if rect:
        pygame.draw.rect(surface, color, rect, 2)

# --- Game loop ---
running = True
while running:
    dt = clock.tick(60)
    WIN.fill((48,69,41))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Rotate enemy every few seconds ---
    rotate_timer += dt
    if rotate_timer >= rotate_interval:
        rotate_timer = 0
        #direction_index = (direction_index + 1) % len(DIRECTIONS)
        enemy.facing = DIRECTIONS[direction_index]
        enemy.set_animation("idle")

    # --- Update + Draw enemy ---
    enemy.update()
    WIN.blit(enemy.image, enemy.rect.topleft)
    draw_hitbox(WIN, enemy.hitbox)

    pygame.display.flip()

pygame.quit()
sys.exit()
