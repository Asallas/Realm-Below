import pygame, os
from math import sqrt

class Player(pygame.sprite.Sprite):
    def __init__(self, position, scale=2):
        # Load the image file sprite sheet
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/PlayerAnimations/Walk.png"),
            "run" : self.load_sheet("Spritesheets/PlayerAnimations/Run.png"),
            "idle": self.load_sheet("Spritesheets/PlayerAnimations/Idle.png"),
            "roll" : self.load_sheet("Spritesheets/PlayerAnimations/Rolling.png"),
            "attack1": self.load_sheet("Spritesheets/PlayerAnimations/Melee.png"),
            "attack2": self.load_sheet("Spritesheets/PlayerAnimations/MeleeRun.png"),
            "counter": self.load_sheet("Spritesheets/PlayerAnimations/Counter.png"),
            "block_start": self.load_sheet("Spritesheets/PlayerAnimations/ShieldBlockStart.png"),
            "block_holding": self.load_sheet("Spritesheets/PlayerAnimations/ShieldBlockMid.png"),
            "damaged": self.load_sheet("Spritesheets/PlayerAnimations/Take/Damage.png"),
            "dead" : self.load_sheet("Spritesheets/PlayerAnimations/Die.png")
        }
        self.health = 10
        
        self.scale = scale # Scaling factor for sprites
        self.frame_index = 0 # Initialize a frame counter
        self.distance = 15 # Set walking distance
        self.facing = 'south'# Set initial standing position
        self.prev_facing = None # Save previous facing for restoration during rolling
        
        # Animation timing delay
        self.animation_timer = 0
        self.animation_delay = 5

        # State flags
        self.locked = False 
        self.blocking = False
        self.block_holding = False
        self.rolling = False

        # Rolling data
        self.roll_distance = 300
        self.roll_speed = 12
        self.roll_direction = None
        self.roll_target_pos = None
        self.roll_cooldown = 0
        self.roll_cooldown_max = 60

        # --------------------- Hitboxes ------------------
        self.scale_base = .5 # Scale at which the original hitbox values were set
        self.scale_ratio = self.scale_base / self.scale
        # (width, height, x offset, y offset)
        self.hitbox_data = {
            "north": (58 * self.scale_ratio, 119 * self.scale_ratio, 105 * self.scale_ratio, 77 * self.scale_ratio),
            "south": (53 * self.scale_ratio, 107 * self.scale_ratio, 94 * self.scale_ratio, 92 * self.scale_ratio),
            "east" : (79 * self.scale_ratio, 95 * self.scale_ratio, 90 * self.scale_ratio, 95 * self.scale_ratio),
            "west" : (73 * self.scale_ratio, 103 * self.scale_ratio, 86 * self.scale_ratio, 87 * self.scale_ratio),
            "northeast" : (52 * self.scale_ratio, 105 * self.scale_ratio, 114 * self.scale_ratio, 88 * self.scale_ratio),
            "northwest" : (75 * self.scale_ratio, 100 * self.scale_ratio, 85 * self.scale_ratio, 85 * self.scale_ratio),
            "southeast" : (75 * self.scale_ratio, 90 * self.scale_ratio, 90 * self.scale_ratio, 100 * self.scale_ratio),
            "southwest" : (62 * self.scale_ratio, 100 * self.scale_ratio, 88 * self.scale_ratio, 95 * self.scale_ratio)
        }

        w,h,ox,oy = self.hitbox_data[self.facing]

        self.rect = pygame.Rect(*position, 128,128)
        self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
        # Attack polygon points
        self.attack_hitbox_points = [
            (0,0), # Center
            (50,-30), # Forward upper point
            (50,30) # forward lower point
        ]
        self.attack_hitbox = None
        self.attack_active = False
        self.attack_timer = 0

        # Animations
        self.animations = {}
        # Define directions for animations
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
        self.non_interruptible = {"attack1", "attack2", "roll", "counter", "block_start", "damaged", "dead"}
        self.looping = {'walk', 'run', 'idle', 'block_hold'}

        for anim_name, sheet in self.sheets.items():
            self.animations[anim_name] = {d: {} for d in directions}
            for i in range(15):
                for direct, y in directions.items():
                    self.animations[anim_name][direct][i] = (128 * i, y, 128, 128)

                
        # Set default animation
        self.current_animation = "idle"
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
        self.rect = self.image.get_rect(topleft = position)

# --------------- Loading / Frame Handling ---------------------

    def load_sheet(self, path):
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
        if animation_name != self.current_animation:
            self.current_animation = animation_name
            self.frame_index = 0
            self.animation_delay = 5
        if animation_name in self.non_interruptible:
            self.animation_delay = 2
        
# ------------------ Update & Animation --------------------------
    def update(self):
        if self.roll_cooldown > 0:
            self.roll_cooldown -= 1

        if self.rolling:
            self._update_roll()
        
        self.update_animations()
        self._update_hitboxes()

        if self.attack_active:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attack_active = False
                self.attack_hitbox = None

    
    def update_animations(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.frame_index += 1
            self.animation_timer = 0

            frames = len(self.animations[self.current_animation][self.facing])
            if self.frame_index >= frames:
                if self.current_animation in self.looping:
                    self.frame_index = 0
                else:
                    if self.current_animation == "block_start":
                        self.set_animation("block_holding")
                        self.block_holding = True
                        self.frame_index = 0
                        self.locked = True
                    elif self.current_animation in {"attack1", "attack2", "roll", "counter"}:
                        self.frame_index = frames - 1
                        if self.current_animation == "roll":
                            self._end_roll()
                        elif self.current_animation in self.non_interruptible:
                            self.locked = False
                            self.set_animation("idle")
                    else: # default
                        self.frame_index = 0
    
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
        
# ------------------------------ Movement -------------------------
    def move(self, direction):
        if self.locked or self.rolling:
            return
        if self.blocking or self.block_holding:
            return

        self.set_animation('run')
        self.facing = direction
        delta = 0
        if direction in ('northeast', 'northwest', 'southeast', 'southwest'):
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
        

    def stand(self):
        if self.locked or self.rolling:
            return
        if self.blocking or self.block_holding:
            return
        self.set_animation("idle")

# ---------------------- Combat -----------------------------    
    def attack(self):
        if not self.locked and not self.rolling:
            self.set_animation("attack1")
            self.frame_index = 0
            self.locked = True
            self._activate_attack_hitbox(15)
            
    def attack2(self):
        if not self.locked and not self.rolling:
            self.set_animation("attack2")
            self.frame_index = 0
            self.locked = True
            self._activate_attack_hitbox(15)

    def counter(self):
        if not self.locked and not self.rolling:
            self.set_animation("counter")
            self.frame_index = 0
            self.locked = True
            self._activate_attack_hitbox(12)

    def _activate_attack_hitbox(self,duration):
        self.attack_active = True
        self.attack_timer = duration
        
        facing_mod = {
            "north" : (0,-1), "south" : (0,1), "east" : (1,0), "west": (-1,0),
            "northeast" : (0.7, -0.7), "northwest" : (-0.7, -0.7),
            "southeast" : (0.7, 0.7), "southwest" : (-0.7, 0.7)
        }
        fx, fy = facing_mod[self.facing]
        cx, cy = self.rect.center

        self.attack_hitbox = [
            (cx + px * fx, cy + py * fy)
            for px,py in self.attack_hitbox_points
        ]
# ---------------------- Damage ---------------------

    def _take_damage(self):
        self.set_animation("damaged")
        self.frame_index = 0
        self.locked = True
        self.hitbox = None
        self.health -= 1
        # Player gets moved back a set number of tiles
        
        
    def knockback(self):
        pass
    
    def _player_death(self):
        self.set_animation("dead")
        self.frame_index = 0
        self.locked  = True
        # Only thing that should happen since killing sprite is in main game loop
        

# ---------------------- Block Logic -------------------
    def block(self):
        if self.locked or self.rolling or self.blocking:
            return
        
        self.blocking = True
        self.locked = True
        self.set_animation("block_start")
        self.frame_index = 0
    
    def release_block(self):
        if not self.blocking:
            return
        
        self.blocking = False
        self.locked = False
        self.block_holding = False
        self.set_animation("idle")

# --------------------- Roll Logic ----------------------
    def roll(self):
        if self.locked or self.rolling or self.roll_cooldown > 0:
            return
        
        self.rolling = True
        self.locked = True

        self.roll_direction = self._get_opposite_direction(self.facing)

        self.prev_facing = self.facing
        self.facing = self.roll_direction

        self.set_animation("roll")
        start_pos = pygame.Vector2(self.rect.center)
        direction_vector = self._get_direction_vector(self.roll_direction)
        self.roll_target_pos = start_pos + direction_vector * self.roll_distance

        self.hitbox = None
        self.attack_hitbox = None

    def _update_roll(self):
        if not self.rolling:
            return
        
        direction_vector = self._get_direction_vector(self.roll_direction)
        move_step = direction_vector * self.roll_speed
        self.rect.center += move_step

        current_pos = pygame.Vector2(self.rect.center)
        distance_remaining = current_pos.distance_to(self.roll_target_pos)
        if distance_remaining <= self.roll_speed:
            self._end_roll()

    def _end_roll(self):
        self.rolling = False
        self.locked = False
        self.roll_cooldown = self.roll_cooldown_max
        self.facing = self.prev_facing
        self.set_animation('idle')
        self._reset_hitbox()
        

    # ---------------- Helper Functions -------------------
    def _update_hitboxes(self):
        if self.hitbox:
            w,h,ox,oy = self.hitbox_data[self.facing]
            self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
        if self.attack_hitbox and self.attack_active:
            cx,cy = self.rect.center
            facing_mod = {
                "north" : (0,-1), "south" : (0,1), 'east' : (1,0), 'west': (-1,0),
                "northeast" : (0.7, -0.7), "northwest" : (-0.7, -0.7),
                "southeast" : (0.7, 0.7), "southwest" : (-0.7, 0.7)
            }
            fx, fy = facing_mod[self.facing]
            self.attack_hitbox = [
                (cx + px * fx, cy + py * fy)
                for px,py in self.attack_hitbox_points
            ]
            
        
    def _reset_hitbox(self):
        w,h,ox,oy = self.hitbox_data[self.facing]
        self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)

    def _get_direction_vector(self, direction):
        mapping = {
            'north': pygame.Vector2(0, -1),
            'south': pygame.Vector2(0, 1),
            'east': pygame.Vector2(1, 0),
            'west': pygame.Vector2(-1, 0),
            'northeast': pygame.Vector2(1, -1).normalize(),
            'northwest': pygame.Vector2(-1, -1).normalize(),
            'southeast': pygame.Vector2(1, 1).normalize(),
            'southwest': pygame.Vector2(-1, 1).normalize()
        }
        return mapping.get(direction, pygame.Vector2(0,0))
    
    def _get_opposite_direction(self, direction):
        opposites = {
            'north' : 'south', 'south' : 'north',
            'east' : 'west', 'west' : 'east',
            'northeast' : 'southwest', 'southwest' : 'northeast',
            'northwest' : 'southeast', 'southeast' : 'northwest'
        }
        return opposites.get(direction, 'south')
    
    # -------------- Debug draw ------------------------
    def draw(self, screen):
        if self.hitbox:
            pygame.draw.rect(screen, pygame.Color("yellow"), self.hitbox, 2)
        if self.attack_hitbox:
            pygame.draw.polygon(screen, pygame.Color("blue"), self.attack_hitbox, 2)