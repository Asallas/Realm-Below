import pygame, math
from character import Character
class Player(Character):
    def __init__(self, position, scale=2):
        super().__init__(position, scale)

        # Load the image file sprite sheet
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/PlayerAnimations/Walk.png", "walk"),
            "run" : self.load_sheet("Spritesheets/PlayerAnimations/Run.png", "run"),
            "idle": self.load_sheet("Spritesheets/PlayerAnimations/Idle.png", "idle"),
            "roll" : self.load_sheet("Spritesheets/PlayerAnimations/Rolling.png", "roll"),
            "attack1": self.load_sheet("Spritesheets/PlayerAnimations/Melee.png", "attack1"),
            "attack2": self.load_sheet("Spritesheets/PlayerAnimations/MeleeRun.png", "attack2"),
            "counter": self.load_sheet("Spritesheets/PlayerAnimations/Counter.png", "counter"),
            "block_start": self.load_sheet("Spritesheets/PlayerAnimations/ShieldBlockStart.png", "block_start"),
            "block_holding": self.load_sheet("Spritesheets/PlayerAnimations/ShieldBlockMid.png", "block_holding"),
            "hit": self.load_sheet("Spritesheets/PlayerAnimations/TakeDamage.png", "hit"),
            "death" : self.load_sheet("Spritesheets/PlayerAnimations/Die.png", "death")
        }
        self.distance = 15 # Set walking distance
        self.prev_facing = None # Save previous facing for restoration during rolling
        
        # Animation timing delay
        self.animation_timer = 0
        self.animation_delay = 5

        # State flags
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
        self.invulnerable = 180

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

        self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
        # Attack polygon points

        base_points = [
            (0, 0), (40, -60), (90, -40), (120, 0),
            (110, 40), (80, 70), (30,90)
        ]

        self.attack_hitbox_points = [
            (x * self.scale_ratio, y * self.scale_ratio) for (x,y) in base_points
        ]

        # ----------- Attack Flags ------------
        self.attack_registered = False
        self.attack_active = False
        self.attack_timer = 0

        # ----------- Stun flag ---------
        self.stunned = False
        self.hit_stun_duration = 30
        self.hit_stun_timer = 0

        # Animations
        
        self.non_interruptible = {"attack1", "attack2", "roll", "counter", "block_start", "hit", "death"}
        self.looping = {'walk', 'run', 'idle', 'block_hold'}
                
        # Set default animation
        self.current_animation = "idle"
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
        self.rect = self.image.get_rect(topleft = position)
        
# ------------------ Update & Animation --------------------------
    def set_animation(self, animation_name):
        if animation_name in self.non_interruptible:
            self.animation_delay = 2
        else:
            self.animation_delay = 5
        super().set_animation(animation_name)
    def update(self):
        if self.roll_cooldown > 0:
            self.roll_cooldown -= 1

        if self.rolling:
            self._update_roll()
        
        if not self.is_dead:
            self.update_animations()
            self.update_knockback()
            self._update_hitboxes()
            

        self.update_attack()

    
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
        if self.locked or self.rolling or self.blocking or self.block_holding or self.stunned:
            return
        self.set_animation('run')
        super().move(direction)
        

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
            self._activate_attack_hitbox(30)
            
    def attack2(self):
        if not self.locked and not self.rolling:
            self.set_animation("attack2")
            self.frame_index = 0
            self.locked = True
            self._activate_attack_hitbox(30)

    def counter(self):
        if not self.locked and not self.rolling:
            self.set_animation("counter")
            self.frame_index = 0
            self.locked = True
            self._activate_attack_hitbox(20)

    
        

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
        
    #-------- Stun & Damage ------------

    def take_damage(self, amount, attacker_facing):
        # ignore damage if dying/dead or invulnerable
        if self.is_dead or self.is_dying or self.invulnerable:
            return
        
        self.health -= amount
        print(f"{self.__class__.__name__} took {amount} damage - HP: {self.health}")

        # apply immediate knockback
        knockback_strength = 15
        dir_vec = self._get_direction_vector(attacker_facing)
        self.knockback_velocity = -dir_vec * knockback_strength

        # Start invulnerability window
        self.invulnerable = True
        self.invuln_timer = 0

        # Set hitstun state to stop enemy from moving
        self.stunned = True
        self.hit_stun_timer = 0

        if getattr(self, "current_animation", "") in getattr(self, "non_interruptible", set()):
            self.pending_hit = True
        else:
            self.pending_hit = False
            self.set_animation("hit")
        if self.health <= 0:
            self.health = 0
            self.die()

    def update_hit_stun(self):
        if self.stunned:
            self.hit_stun_timer += 1
            if self.hit_stun_timer >= self.hit_stun_duration:
                self.stunned = False
                self.hit_stun_timer = 0
                if self.current_animation == "hit":
                    self.set_animation("idle")
 
    # ---------------- Helper Functions -------------------            
        
    def _reset_hitbox(self):
        w,h,ox,oy = self.hitbox_data[self.facing]
        self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
    
    

