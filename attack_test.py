import pygame
from player import Player  # assuming your class is saved in player.py
from enemys import MeleeEnemy

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Player Attack Polygon Test")

clock = pygame.time.Clock()
running = True

# --- Spawn Player ---
player = Player((WIDTH // 2 - 128, HEIGHT // 2 - 128), .5)
enemy = MeleeEnemy((WIDTH//2 - 1000,HEIGHT // 2 - 128), .5)

# --- Direction mapping for arrow keys ---
facing_order = [
    "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest"
]
facing_index = 2  # start facing east
player.facing = facing_order[facing_index]

# --- Debug Controls ---
paused = False
step = False

def draw_translucent_polygon(surface, points, color=(255, 0, 0, 80)):
    if not points: return
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(overlay, color, points)
    surface.blit(overlay, (0, 0))

enemy.target = player.hitbox
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # --- Debug pause/step controls ---
            elif event.key == pygame.K_p:
                paused = not paused
                print(f"{'Paused' if paused else 'Unpaused'}")
            elif event.key == pygame.K_n and paused:
                step = True  # advance one frame

            # --- Attack test ---
            elif event.key == pygame.K_w:
                player.attack()
            

            # --- Rotate facing direction with arrows ---
            elif event.key == pygame.K_RIGHT:
                facing_index = (facing_index + 1) % len(facing_order)
                player.facing = facing_order[facing_index]
            elif event.key == pygame.K_LEFT:
                facing_index = (facing_index - 1) % len(facing_order)
                player.facing = facing_order[facing_index]

    # --- Update only if not paused or stepping one frame ---
    if not paused or step:
        player.update()
        enemy.update()

        step = False  # reset after a single frame step

    # --- Draw ---
    screen.fill((30, 30, 40))
    screen.blit(player.image, player.rect)
    screen.blit(enemy.image, enemy.rect)

    # Draw hitbox rectangle (body)
    if player.hitbox:
        pygame.draw.rect(screen, (0, 255, 0), player.hitbox, 2)

    # Draw attack polygon when active
    if player.attack_active and player.attack_hitbox:
        draw_translucent_polygon(screen, player.attack_hitbox, (255, 0, 0, 100))

    # Draw facing direction + debug text
    font = pygame.font.SysFont(None, 28)
    debug_text = f"Facing: {player.facing} | Paused: {paused}"
    text = font.render(debug_text, True, (255, 255, 255))
    screen.blit(text, (10, 10))
    if enemy.attack_active and enemy.attack_hitbox:
        #print(f"Current frame index: {enemy.frame_index}")
        enemy.draw_translucent_polygon(screen, enemy.attack_hitbox, (255, 0, 0, 100))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
