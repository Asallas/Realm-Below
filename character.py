import pygame,os
from math import sqrt

class Character(pygame.sprite.Sprite):
    def __init__(self, position, scale = 2):
        super().__init__()
        self.scale = scale
        self.frame_index = 0
        self.facing = "south"
        self.locked = False

        self.sheets = {}
        self.animations = {}
        self.image = None
        self.rect = pygame.Rect(*position, 128, 128)

        self.distance = 7

        self.hitbox = None
        self.attack_hitbox = None

    # -------------- Sprite & Animation -----------------
    def load_sheets(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Spritesheet not found {path}")
        return pygame.image.load(path).convert_alpha()
    
    def get_frame(self, animation_name, direction, frame_set):
        rect = self.animations[animation_name][direction][frame_set]
        frame = self.sheets[animation_name].subsurface(rect)
        if self.scale != 1:
            w,h = frame.get_size()
            frame = pygame.transform.scale(frame, (int(w // self.scale), int(h // self.scale)))
        return frame
    
    def set_animation(self, animation_name):
        if animation_name != getattr(self, "current_animation", None):
            self.current_animation = animation_name
            self.frame_index = 0
            self.animation_timer = 0
    

    # ------------- Movement ---------------
    def move(self, direction):
        if self.locked:
            return
        self.facing = direction
        if direction in ("northeast", "northwest", "southwest", "southeast"):
            delta = self.distance / sqrt(2)
        else: 
            delta = self.distance

        if 'north' in direction:
            self.rect.y -= delta
        if 'south' in direction:
            self.rect.y += delta
        if 'east' in direction:
            self.rect.x += delta
        if 'west' in direction:
            self.rect.x -= delta