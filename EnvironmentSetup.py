import pygame, sys, json, os

pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TILE_SCALE = 2
GRID_SIZE = 16     # <--- UNIFORM SNAP VALUE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Environment Builder")
clock = pygame.time.Clock()

# -----------------------------------------------------------
# Load master tileset
# -----------------------------------------------------------
TILESET_PATH = "Environment/RF_Catacombs_v1.0/mainlevbuild.png"
tileset = pygame.image.load(TILESET_PATH).convert_alpha()

# -----------------------------------------------------------
# Tile atlas rects (easy editable)
# -----------------------------------------------------------
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

TILE_KEYS = list(TILE_RECTS.keys())
current_tile_index = 0

# -----------------------------------------------------------
# Map storage: (key, x, y)
# -----------------------------------------------------------
placed_tiles = []

# -----------------------------------------------------------
# Floor placement
# -----------------------------------------------------------
def place_floor_tiles():
    floor_key = "basic_floor"
    rect = TILE_RECTS[floor_key]

    tile_w = rect.width * TILE_SCALE
    tile_h = rect.height * TILE_SCALE

    tiles_across = SCREEN_WIDTH // tile_w + 2
    tiles_down   = SCREEN_HEIGHT // tile_h + 2

    for row in range(tiles_down):
        for col in range(tiles_across):
            x = col * tile_w
            y = row * tile_h
            placed_tiles.append((floor_key, x, y))

    print(f"Placed {tiles_across * tiles_down} floor tiles.")


# -----------------------------------------------------------
# Tile preview
# -----------------------------------------------------------
def draw_tile_preview(mouse_pos):
    tile_key = TILE_KEYS[current_tile_index]
    rect = TILE_RECTS[tile_key]

    scaled_w = rect.width * TILE_SCALE
    scaled_h = rect.height * TILE_SCALE

    snap_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    snap_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE

    tile_img = tileset.subsurface(rect)
    tile_img = pygame.transform.scale(tile_img, (scaled_w, scaled_h))

    screen.blit(tile_img, (snap_x, snap_y), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.rect(screen, (0,255,0), (snap_x, snap_y, scaled_w, scaled_h), 2)


# -----------------------------------------------------------
# Save to JSON
# -----------------------------------------------------------
def save_map():
    data = {
        "tiles": [
            {"type": tile_key, "x": x, "y": y}
            for (tile_key, x, y) in placed_tiles
        ]
    }
    with open("environment_layout.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Saved environment_layout.json")


# -----------------------------------------------------------
# Main loop
# -----------------------------------------------------------
running = True
while running:

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Keyboard input
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_s:
                save_map()

            if event.key == pygame.K_f:
                place_floor_tiles()

            if pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if idx < len(TILE_KEYS):
                    current_tile_index = idx
                    print(f"Selected tile: {TILE_KEYS[current_tile_index]}")

        # Mouse click placement
        if event.type == pygame.MOUSEBUTTONDOWN:
            tile_key = TILE_KEYS[current_tile_index]
            rect = TILE_RECTS[tile_key]

            scaled_w = rect.width * TILE_SCALE
            scaled_h = rect.height * TILE_SCALE

            snap_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
            snap_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE

            # Left click places a tile
            if event.button == 1:
                placed_tiles.append((tile_key, snap_x, snap_y))

            # Right click removes tile
            if event.button == 3:
                for tile in placed_tiles[:]:
                    t_key, tx, ty = tile
                    t_rect = TILE_RECTS[t_key]

                    tile_rect = pygame.Rect(
                        tx, ty,
                        t_rect.width * TILE_SCALE,
                        t_rect.height * TILE_SCALE
                    )

                    if tile_rect.collidepoint(mouse_pos):
                        placed_tiles.remove(tile)

    # -------------------------------------------------------
    # Draw
    # -------------------------------------------------------
    screen.fill((50, 50, 50))

    # Draw placed tiles
    for tile_key, x, y in placed_tiles:
        rect = TILE_RECTS[tile_key]
        tile_img = tileset.subsurface(rect)

        scaled_img = pygame.transform.scale(
            tile_img,
            (rect.width * TILE_SCALE, rect.height * TILE_SCALE)
        )

        screen.blit(scaled_img, (x, y))

    # Preview
    draw_tile_preview(mouse_pos)

    # UI label
    font = pygame.font.Font(None, 36)
    label = f"Current Tile: {TILE_KEYS[current_tile_index]}"
    screen.blit(font.render(label, True, (255,255,255)), (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
