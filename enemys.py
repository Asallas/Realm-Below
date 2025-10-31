import pygame
from character import Character
class MeleeEnemy(Character):
    def __init__(self, position, scale):
        super().__init__(position, scale)
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/MeleeEnemy/Walk.png", "walk"),
            "idle" : self.load_sheet("Spritesheets/MeleeEnemy/Idle.png", "idle"),
            "attack1" : self.load_sheet("Spritesheets/MeleeEnemy/Attack2.png", "attack1"),
            "attack2" : self.load_sheet("Spritesheets/MeleeEnemy/Attack2.png", "attack2"),
            "attack3" : self.load_sheet("Spritesheets/MeleeEnemy/Attack3.png", "attack3"),
            "castspell" : self.load_sheet("Spritesheets/MeleeEnemy/CastSpell.png", "castspell"),
            "idle2" : self.load_sheet("Spritesheets/MeleeEnemy/Idle2.png", "idle2"),
            "AttackRun" : self.load_sheet("Spritesheets/MeleeEnemy/AttackRun.png", "AttackRun"),
            "special1" : self.load_sheet("Spritesheets/MeleeEnemy/Special1.png", "special1"),
            "special2" : self.load_sheet("Spritesheets/MeleeEnemy/Special2.png", "special2"),
            "hit": self.load_sheet("Spritesheets/MeleeEnemy/TakeDamage.png", "hit"),
            "death" : self.load_sheet("Spritesheets/MeleeEnemy/Die.png", "death") 
        }
        
        self.target = None
        self.attack_range = 75
        self.attack_cooldown = 1500
        self.last_attack_time = 0
        self.speed = 5

                # --------------------- Hitboxes ------------------
        self.scale_base = .5 # Scale at which the original hitbox values were set
        self.scale_ratio = self.scale_base / self.scale
        # (width, height, x offset, y offset)
        self.hitbox_data = {
            "north": (58 * self.scale_ratio, 102 * self.scale_ratio, 105 * self.scale_ratio, 73 * self.scale_ratio),
            "south": (58 * self.scale_ratio, 99 * self.scale_ratio, 101 * self.scale_ratio, 83 * self.scale_ratio),
            "east" : (51 * self.scale_ratio, 98 * self.scale_ratio, 110 * self.scale_ratio, 78 * self.scale_ratio),
            "west" : (47 * self.scale_ratio, 98 * self.scale_ratio, 100 * self.scale_ratio, 78 * self.scale_ratio),
            "northeast" : (45 * self.scale_ratio, 100 * self.scale_ratio, 110 * self.scale_ratio, 75 * self.scale_ratio),
            "northwest" : (50 * self.scale_ratio, 100 * self.scale_ratio, 98 * self.scale_ratio, 72 * self.scale_ratio),
            "southeast" : (55 * self.scale_ratio, 95 * self.scale_ratio, 105 * self.scale_ratio, 83 * self.scale_ratio),
            "southwest" : (42 * self.scale_ratio, 100 * self.scale_ratio, 108 * self.scale_ratio, 81 * self.scale_ratio)
        }
        w,h,ox,oy = self.hitbox_data[self.facing]

        self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
        
        basePoints = [
            (0, 0), (0,-8), (-70,-8),(-70, -55), (20, -55), (40, -50), (55,-45),(115, -10),
            (110, 45), (90, 55), (50,80)

        ]
        # pause frame 6
        self.attack_hitbox_points = [
            (x * self.scale_ratio, y * self.scale_ratio) for (x,y) in basePoints
        ]

        self.animation_timer = 0
        self.animation_delay = 5
        
        self.non_interruptible = {"attack1", "death", "hit"}
        self.looping = {"walk", "idle"}

        self.current_animation = "idle"
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
        self.rect = self.image.get_rect(topleft = position) 

    def update(self):
        if self.is_dead:
            return
        if self.is_dying:
            self.update_animations()
            return
        
        now = pygame.time.get_ticks()
        
        if self.target:
            to_target = pygame.Vector2(
                self.target.centerx - self.rect.centerx,
                self.target.centery - self.rect.centery
            )
            
            dist = to_target.length()
            
            if dist > 0:
                facing_vect = to_target.normalize()
                self.facing = self._get_vector_facing(facing_vect)
            else:
                if self.facing is None:
                    self.facing = "south"
                    print("Error would have occurred")

            if not self.locked:
                if dist > self.attack_range:
                    move_vec = to_target.normalize() * self.speed
                    self.rect.centerx += move_vec.x
                    self.rect.centery += move_vec.y
                    self.set_animation("walk") 
            
                else:
                    if now - self.last_attack_time >= self.attack_cooldown:
                        self.last_attack_time = now
                        self.attack()
                    else:
                        self.set_animation("idle")
        
        else:
            self.set_animation("idle")
        
        prev_frame = self.frame_index
        self.update_animations()
        if self.current_animation == 'attack1':
            if prev_frame < 6 <= self.frame_index and not self.attack_active:
                self._activate_attack_hitbox(15)
        self._update_hitboxes()
        self.update_attack()
        
    def attack(self):
        if not self.locked:
            self.frame_index = 0
            self.locked = True
            self.set_animation("attack1")
        

class RangeEnemy(Character):
    def __init__(self, position, scale=2):
        super().__init__(position, scale)
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/RangeEnemy/Walk.png", "walk"),
            "idle" : self.load_sheet("Spritesheets/RangeEnemy/Idle.png", "idle"),
            "attack1" : self.load_sheet("Spritesheets/RangeEnemy/Attack1.png", "attack1"),
            "attack2" : self.load_sheet("Spritesheets/RangeEnemy/Attack2.png", "attack2"),
            "attack3" : self.load_sheet("Spritesheets/RangeEnemy/Attack3.png", "attack3"),
            "castspell" : self.load_sheet("Spritesheets/RangeEnemy/CastSpell.png", "castspell"),
            "idle2" : self.load_sheet("Spritesheets/RangeEnemy/Idle2.png", "idle2"),
            "AttackRun" : self.load_sheet("Spritesheets/RangeEnemy/AttackRun.png", "AttackRun"),
            "special1" : self.load_sheet("Spritesheets/RangeEnemy/Special1.png", "special1"),
            "special2" : self.load_sheet("Spritesheets/RangeEnemy/Special2.png", "special2"), # Literally casting a fireball
            "hit": self.load_sheet("Spritesheets/RangeEnemy/TakeDamage.png", "hit"),
            "death" : self.load_sheet("Spritesheets/RangeEnemy/Die.png", "death")
        }
        
        self.target = None
        self.preferred_distance = 275
        self.min_distance = 50
        self.max_distance = 350
        self.attack_cooldown = 2000
        self.last_attack_time = 0
        self.speed = 3
        
        # --------------------- Hitboxes ------------------
        self.scale_base = .5 # Scale at which the original hitbox values were set
        self.scale_ratio = self.scale_base / self.scale
        # (width, height, x offset, y offset)
        self.hitbox_data = {
            "north": (58 * self.scale_ratio, 102 * self.scale_ratio, 113 * self.scale_ratio, 76 * self.scale_ratio),
            "south": (48 * self.scale_ratio, 101 * self.scale_ratio, 98 * self.scale_ratio, 86 * self.scale_ratio),
            "east" : (53 * self.scale_ratio, 98 * self.scale_ratio, 110 * self.scale_ratio, 90 * self.scale_ratio),
            "west" : (54 * self.scale_ratio, 98 * self.scale_ratio, 96 * self.scale_ratio, 78 * self.scale_ratio),
            "northeast" : (45 * self.scale_ratio, 102 * self.scale_ratio, 114 * self.scale_ratio, 85 * self.scale_ratio),
            "northwest" : (57 * self.scale_ratio, 102 * self.scale_ratio, 100 * self.scale_ratio, 72 * self.scale_ratio),
            "southeast" : (57 * self.scale_ratio, 95 * self.scale_ratio, 100 * self.scale_ratio, 95 * self.scale_ratio),
            "southwest" : (42 * self.scale_ratio, 101 * self.scale_ratio, 101 * self.scale_ratio, 82 * self.scale_ratio)
        }
        w,h,ox,oy = self.hitbox_data[self.facing]

        self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
        
        self.animation_timer = 0
        self.animation_delay = 5
        
        self.non_interruptible = {"attack1", "death", "hit"}
        self.looping = {"walk", "idle"}

        self.current_animation = "idle"
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
        self.rect = self.image.get_rect(topleft = position) 
    
    def update(self):
        if self.is_dead:
            return
        if self.is_dying:
            self.update_animations()
            return
        now = pygame.time.get_ticks()
        
        if self.target:
            to_target = pygame.Vector2(
                self.target.centerx - self.rect.centerx,
                self.target.centery - self.rect.centery
            )
            
            dist = to_target.length()
            
            if dist > 0:
                facing_vect = to_target.normalize()
                self.facing = self._get_vector_facing(facing_vect)
            else:
                if self.facing is None:
                    self.facing = "south"
                    print("Error would have occurred")

            move_vec = pygame.Vector2(0,0)
            
            zone = 50
            close = dist < self.preferred_distance - zone
            far = dist > self.preferred_distance + zone
            if not self.locked:
                if close:
                    move_vec = -to_target.normalize() * self.speed
                    self.set_animation("walk") 
                elif far:
                    move_vec = to_target.normalize() * self.speed
                    self.set_animation("walk")
            
                else:
                    if now - self.last_attack_time >= self.attack_cooldown:
                        self.set_animation("attack1")
                        self.locked = True
                        self.last_attack_time = now
                    else:
                        self.set_animation("idle")
                self.rect.centerx += move_vec.x
                self.rect.centery += move_vec.y
        
        else:
            self.set_animation("idle")
        
        self.update_animations()
        self._update_hitboxes()