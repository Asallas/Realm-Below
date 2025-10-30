import pygame
from character import Character
class MeleeEnemy(Character):
    def __init__(self, position, scale):
        super().__init__(position, scale)
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/MeleeEnemy/Walk.png", "walk"),
            "idle" : self.load_sheet("Spritesheets/MeleeEnemy/Idle.png", "idle"),
            "attack1" : self.load_sheet("Spritesheets/MeleeEnemy/Attack2.png", "attack1")
        }
        
        self.target = None
        self.attack_range = 100
        self.attack_cooldown = 1500
        self.last_attack_time = 0
        self.speed = 5
        
        self.health = 5

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
        
        self.animation_timer = 0
        self.animation_delay = 5
        
        self.non_interruptible = {"attack1"}
        self.looping = {"walk", "idle"}

        self.current_animation = "idle"
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
        self.rect = self.image.get_rect(topleft = position) 

    def update(self):
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
                        self.set_animation("attack1")
                        self.locked = True
                        self.last_attack_time = now
                    else:
                        self.set_animation("idle")
        
        else:
            self.set_animation("idle")
        
        self.update_animations()
        self._update_hitboxes()
        
        
            
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
        

class RangeEnemy(Character):
    def __init__(self, position, scale=2):
        super().__init__(position, scale)
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/RangeEnemy/Walk.png", "walk"),
            "idle" : self.load_sheet("Spritesheets/RangeEnemy/Idle.png", "idle"),
            "attack1" : self.load_sheet("Spritesheets/RangeEnemy/Attack3.png", "attack1")
        }
        
        self.target = None
        self.attack_range = 100
        self.attack_cooldown = 1500
        self.last_attack_time = 0
        self.speed = 5
        
        self.health = 5

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
        
        self.animation_timer = 0
        self.animation_delay = 5
        
        self.non_interruptible = {"attack1"}
        self.looping = {"walk", "idle"}

        self.current_animation = "idle"
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
        self.rect = self.image.get_rect(topleft = position) 
    
    def update(self):
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
                        self.set_animation("attack1")
                        self.locked = True
                        self.last_attack_time = now
                    else:
                        self.set_animation("idle")
        
        else:
            self.set_animation("idle")
        
        self.update_animations()
        self._update_hitboxes()
        
        
            
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