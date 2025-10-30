import pygame,os
from math import sqrt

class Character(pygame.sprite.Sprite):
    def __init__(self, position, scale = 2):
        super().__init__()
        self.scale = scale
        self.frame_index = 0
        self.facing = "south"
        self.locked = False

        self.animation_timer = 0
        self.animation_delay = 2

        self.sheets = {}
        self.animations = {}
        self.current_animation = "idle"

        self.image = None
        self.rect = pygame.Rect(*position, 128, 128)

        self.distance = 7

        self.hitbox_data = {}
        self.hitbox = None
        self.attack_hitbox = None
        
        self.non_interruptible = {}
        self.looping = {}
        

    # -------------- Sprite & Animation -----------------
    def load_sheet(self, path, name):
        directions = {
            "south":256,
            "southeast": 128,
            "east": 0,
            "northeast": 896,
            "north": 768,
            "northwest": 640,
            "west": 512,
            "southwest": 384
        }
        if not os.path.exists(path):
            raise FileNotFoundError(f"Spritesheet not found {path}")
        
        self.animations[name] = {d: {} for d in directions}
        for i in range(15):
            for direct, y in directions.items():
                self.animations[name][direct][i] = (128 * i, y, 128, 128)
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
    
    def update_animations(self):
        self.animation_timer += 1

        if self.facing is None or self.current_animation is None:
            print(f"[WARN] Invalid animation state: anim={self.current_animation}, facing={self.facing}")


        if self.current_animation not in self.animations:
            self.set_animation("idle")
            print("Current animation broke")
            return
        if self.facing not in self.animations[self.current_animation]:
            self.set_animation("idle")
            print("facing broke")
            return

        if self.animation_timer >= self.animation_delay:
            self.frame_index += 1
            self.animation_timer = 0
            frames = len(self.animations[self.current_animation][self.facing])
            if self.frame_index >= frames:
                if self.current_animation in self.looping:
                    self.frame_index = 0
                elif self.current_animation in self.non_interruptible:
                    self.frame_index = 0
                    self.locked = False
                    self.set_animation("idle")
                else:
                    self.frame_index = 0
        
        

        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)


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

    def _update_hitboxes(self):
        if self.facing not in self.hitbox_data:
            print(f"[WARN] Invalid facing '{self.facing}' in _update_hitboxes(), defaulting to 'south'")
            self.facing = "south"

        if self.hitbox:
            w,h,ox,oy = self.hitbox_data[self.facing]
            self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)

    # -------------- Debug draw ------------------------
    def draw(self, screen):
        if self.rect:
            pygame.draw.rect(screen, pygame.Color("white"), self.rect,2)
        if self.hitbox:
            pygame.draw.rect(screen, pygame.Color("yellow"), self.hitbox, 2)
        if self.attack_hitbox:
            pygame.draw.polygon(screen, pygame.Color("blue"), self.attack_hitbox, 2)