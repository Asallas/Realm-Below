import pygame,os, math

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

        self.max_health = 100
        self.health = self.max_health
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = 30

        self.is_dead = False
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 75

        self.knockback_velocity = pygame.Vector2(0,0)
        self.knockback_decay = 0.85

        self.hitbox_data = {}
        self.hitbox = None
        self.attack_hitbox = None
        self.attack_hitbox_points = []

        self.attack_active = False
        self.attack_registered = False
        self.attack_timer = 0

        self.non_interruptible = {}
        self.looping = {}
        

    # -------------- Sprite & Animation -----------------
    def load_sheet(self, path, name, w = 128,h = 128):
        directions_order = [
            "east", "southeast", "south", "southwest",
            "west", "northwest", "north", "northeast"
        ]
        directions = {d: i * h for i,d in enumerate(directions_order)}
        if not os.path.exists(path):
            raise FileNotFoundError(f"Spritesheet not found {path}")
        
        self.animations[name] = {d: {} for d in directions}
        for i in range(15):
            for direct, y in directions.items():
                self.animations[name][direct][i] = (w * i, y, w, h)
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
        if animation_name == "idle":
            self.attack_registered = False

    # ------------- Animate the Sprites ----------------
    def update_animations(self):
        # Force dying animation if dying
        if self.is_dying:
            if self.current_animation != "death":
                self.set_animation("death")

            self.animation_timer += 1
            if self.animation_timer >= self.animation_delay:
                self.frame_index += 1
                self.animation_timer = 0
                frames = len(self.animations["death"][self.facing])
                if self.frame_index >= frames:
                    self.frame_index = frames - 1  # stay on last frame
            self.image = self.get_frame("death", self.facing, self.frame_index)
            return  
        
        self.animation_timer += 1

        if self.facing is None or self.current_animation is None:
            print(f"[WARN] Invalid animation state: anim={self.current_animation}, facing={self.facing}")
            return


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
                # finish animation
                if self.current_animation in self.looping:
                    self.frame_index = 0

                elif self.current_animation == "hit":
                    self.frame_index = frames - 1
                    self.locked = False
                    self.set_animation("idle")

                elif self.current_animation in self.non_interruptible:
                    self.frame_index = frames - 1
                    
                    if self.current_animation.startswith("att"):
                        self.attack_registered = False
                    
                    self.locked = False
                    self.set_animation("idle")
                    
                    if getattr(self, "pending_hit", False):
                        self.pending_hit = False
                        self.set_animation("hit")
                        self.locked = True
                else:
                    self.frame_index = 0

        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)

    # ------------- Movement ---------------
    def move(self, direction):
        if self.locked:
            return
        self.facing = direction
        if direction in ("northeast", "northwest", "southwest", "southeast"):
            delta = self.distance / math.sqrt(2)
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

    # ------------------ Damage --------------------
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
        self.locked = True
        self.hit_stun_timer = 0
        self.hit_stun_duration = 15

        if getattr(self, "current_animation", "") in getattr(self, "non_interruptible", set()):
            self.pending_hit = True
        else:
            self.pending_hit = False
            self.set_animation("hit")
        if self.health <= 0:
            self.health = 0
            self.die()
    
    def die(self):
        self.is_dying = True
        print(f"{self.__class__.__name__} started dying")
        self.death_timer = 0
        self.set_animation("death")
    
    # ---------------- Update Hit logic ------------
    def update_knockback(self):
        if self.knockback_velocity.length_squared() > 0.1:
            self.rect.x += self.knockback_velocity.x
            self.rect.y += self.knockback_velocity.y
            self.knockback_velocity *= self.knockback_decay
    def update_death(self):
        if self.is_dying:
            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.is_dying = False
                self.is_dead = True
                print(f"{self.__class__.__name__} has died")
    def update_invulnerability(self):
        if self.invulnerable:
            self.invuln_timer += 1
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0
    
    def update_hit_stun(self):
        if getattr(self, "hit_stun_timer", None) is not None and self.locked:
            self.hit_stun_timer += 1
            if self.hit_stun_timer >= getattr(self, "hit_stun_duration", 0):
                self.hit_stun_timer = 0
    
    def update_attack(self):
        if self.attack_active:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attack_active = False
                self.attack_hitbox = None

    # ---------------- Helpers ----------------------
    def _activate_attack_hitbox(self,duration):
        self.attack_active = True
        self.attack_timer = duration
        
        cx, cy = self.rect.center
        
        facing_angles = {
            "east" : 0,
            "southeast": 45,
            "south": 90,
            "southwest": 135,
            "west": 180,
            "northwest": 225,
            "north": 270,
            "northeast": 315
        }
        angle = facing_angles[self.facing]

        rotated_points = self._rotate_points(self.attack_hitbox_points, angle)
        self.attack_hitbox = [(cx + x, cy + y) for x,y in rotated_points]

    def _update_hitboxes(self):
        if self.facing not in self.hitbox_data:
            print(f"[WARN] Invalid facing '{self.facing}' in _update_hitboxes(), defaulting to 'south'")
            self.facing = "south"

        if self.hitbox:
            w,h,ox,oy = self.hitbox_data[self.facing]
            self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
        if self.attack_hitbox and self.attack_active:
            cx, cy = self.rect.center
            rotated_points = self._rotate_points(self.attack_hitbox_points, self._get_facing_angle())
            self.attack_hitbox = [(cx + x, cy + y) for x,y in rotated_points]
    
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
    
    def _get_vector_facing(self, vec):
        angle = vec.angle_to(pygame.Vector2(1,0))
        
        if -22.5 <= angle < 22.5:
            return 'east'
        elif 22.5 <= angle < 67.5:
            return 'northeast'
        elif 67.6 <= angle < 112.5:
            return 'north'
        elif 112.5 <= angle < 157.5:
            return 'northwest'
        elif angle >= 157.5 or angle < -157.5:
            return 'west'
        elif -157.5 <= angle < -112.5:
            return 'southwest'
        elif -112.5 <= angle < -67.5:
            return 'south'
        elif -67.5 <= angle < -22.5:
            return 'southeast'
    
    def _rotate_points(self, points, angle_deg):
        angle_rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        return [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in points]

    def _get_facing_angle(self):
        facing_angles = {
            "east": 0, "southeast": 45, "south": 90, "southwest": 135,
            "west": 180, "northwest": 225, "north": 270, "northeast": 315
        }
        return facing_angles.get(self.facing, 0)

    # -------------- Debug draw ------------------------
    def draw(self, screen):
        if self.rect:
            pygame.draw.rect(screen, pygame.Color("white"), self.rect,2)
        if self.hitbox:
            pygame.draw.rect(screen, pygame.Color("yellow"), self.hitbox, 2)
        if self.attack_hitbox:
            pygame.draw.polygon(screen, pygame.Color("blue"), self.attack_hitbox, 2)
    
    def draw_healthbar(self, screen):
        bar_width = 100
        bar_height = 6
        x = self.rect.centerx - bar_width // 2
        y = self.rect.centery - 15
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255,0,0), (x,y, bar_width, bar_height))
        pygame.draw.rect(screen, (0,255,0), (x,y, bar_width * ratio, bar_height))
        if self.invulnerable and self.invuln_timer % 6 < 3:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)

    def draw_translucent_polygon(self, surface, points, color=(255, 0, 0, 80)):
        if not points: return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(overlay, color, points)
        surface.blit(overlay, (0, 0))
