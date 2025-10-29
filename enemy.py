import pygame
from character import Character
class Enemy(Character):
    def __init__(self, position, scale):
        super().__init__(self, position, scale)
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/MeleeEnemy/Walk.png", "walk"),
            "idle" : self.load_sheet("Spritesheets/MeleeEnemy/Idle.png", "idle")
        }
        
        self.target = None
        self.attack_range = 50
        self.attack_cooldown = 1500
        self.last_attack_time = 0
        self.speed = 5
        
        self.health = 5
        
        self.animation_timer = 0
        self.animation_delay = 5

    def update(self):
        now = pygame.time.get_ticks()
        
        if self.target:
            to_target = pygame.Vector2(
                self.target.rect.centerx - self.rect.centerx,
                self.target.rect.centery - self.rect.centery
            )
            
            dist = to_target.length()
            
            if dist > 0:
                facing_vect = to_target.normalize()
                self.facing = self._get_vector_facing(facing_vect)
            
            if dist > self.attack_range:
                move_vec = to_target.normalize() * self.speed
                self.rect.centerx = move_vec.x
                self.rect.centery = move_vec.y
                self.set_animation("walk") 
            
            else:
                if now - self.last_attack_time >= self.attack_cooldown:
                    self.set_animation("attack")
                    self.last_attack_time = now
                else:
                    self.set_animation("idle")
        
        else:
            self.set_animation("idle")
        
        
            
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
        
