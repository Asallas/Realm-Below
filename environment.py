import json, os, pygame
def load_map(json_path):
    if not os.path.exists(json_path):
        return []
    with open(json_path, "r") as f:
        data = json.load(f)
    return data.get("tiles", [])

def _make_tile_cache(tileset, tile_rects, tile_scale = 1):
    cache = {}
    for key, rect in tile_rects.items():
        try:
            tile = tileset.subsurface(rect).copy()
        except Exception as e:
            print(f"[_make_tile_cache] Warning: cannot extrace {key} -> {e} - skipping")
            continue

        if tile_scale != 1:
            sw = int(rect.width * tile_scale)
            sh = int(rect.height * tile_scale)
            if sw <= 0 or sh <= 0:
                print(f"[_make_tile_cache] Invalid scale for {key}: ({sw},{sh})")
                continue
            tile = pygame.transform.scale(tile, (sw, sh))
        cache[key] = tile
    return cache

# dynamic surfaces(i.e. parallax)
def draw_loaded_map(surface, loaded_tiles, tileset, tile_rects, 
                    tile_scale = 1, cache = None, camera_offset = (0,0)):
    if cache is None:
        cache = _make_tile_cache(tileset, tile_rects, tile_scale)
    
    dx,dy = camera_offset
    blit = surface.blit
    for entry in loaded_tiles:
        t = entry.get("type")
        x = entry.get("x", 0) + dx
        y = entry.get("y", 0) + dy
        img = cache.get(t)
        if img:
            blit(img, (x,y))
        else:
            rect = tile_rects.get(t)
            if rect:
                try:
                    tile = tileset.subsurface(rect).copy()
                    if tile_scale != 1:
                        tile = pygame.transform.scale(tile, (int(rect.width*tile_scale), int(rect.height*tile_scale)))
                    blit(tile, (x, y))
                except Exception:
                    pass

# static surfaces
def build_bg_surface(loaded_tiles, tileset, tile_rects, tile_scale, screen_size, camera_offset=(0,0)):
    bg = pygame.Surface(screen_size).convert_alpha()
    bg.fill((0,0,0,0))
    cache = _make_tile_cache(tileset, tile_rects, tile_scale)
    dx,dy = camera_offset

    for entry in loaded_tiles:
        t = entry.get("type")
        x = entry.get("x", 0) + dx
        y = entry.get("y", 0) + dy
        img = cache.get(t)
        if img:
            bg.blit(img, (x,y))
    
    return bg, cache