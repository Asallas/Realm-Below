import pygame
from character import Character

class Boss(Character):
    def __init__(self, position, scale=2):
        super().__init__(position, scale)
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/BossEnemy/Walk.png", "walk", 192, 192),
            "idle" : self.load_sheet("Spritesheets/BossEnemy/Idle.png", "idle", 192,192),
            "attack1" : self.load_sheet("Spritesheets/BossEnemy/Attack1.png", "attack1",192,192),
            "attack2" : self.load_sheet("Spritesheets/BossEnemy/Attack2.png", "attack2",192,192),
            "attack3" : self.load_sheet("Spritesheets/BossEnemy/Attack3.png", "attack3",192,192),
            "castspell" : self.load_sheet("Spritesheets/BossEnemy/CastSpell.png", "castspell",192,192),
            "idle2" : self.load_sheet("Spritesheets/BossEnemy/Idle2.png", "idle2",192,192),
            "AttackRun" : self.load_sheet("Spritesheets/BossEnemy/AttackRun.png", "AttackRun",192,192),
            "special1" : self.load_sheet("Spritesheets/BossEnemy/Special1.png", "special1",192,192),
            "special2" : self.load_sheet("Spritesheets/BossEnemy/Special2.png", "special2",192,192),
            "hit" : self.load_sheet("Spritesheets/BossEnemy/TakeDamage.png", "hit", 192,192),
            "death" : self.load_sheet("Spritesheets/BossEnemy/Die.png", "death", 192,192)
        }
        
        self.target = None
        self.attack_range = 100
        self.attack_cooldown = 3000
        self.last_attack_time = 0
        self.speed = 5
        
        # --------------------- Hitboxes ------------------
        self.scale_base = .5 # Scale at which the original hitbox values were set
        self.scale_ratio = self.scale_base / self.scale
        # (width, height, x offset, y offset)
        self.hitbox_data = {
            "north": (95 * self.scale_ratio, 128 * self.scale_ratio, 145 * self.scale_ratio, 117 * self.scale_ratio),
            "south": (98 * self.scale_ratio, 100 * self.scale_ratio, 145 * self.scale_ratio, 170 * self.scale_ratio),
            "east" : (85 * self.scale_ratio, 155 * self.scale_ratio, 180 * self.scale_ratio, 130 * self.scale_ratio),
            "west" : (72 * self.scale_ratio, 155 * self.scale_ratio, 127 * self.scale_ratio, 122 * self.scale_ratio),
            "northeast" : (83 * self.scale_ratio, 150 * self.scale_ratio, 172 * self.scale_ratio, 125 * self.scale_ratio),
            "northwest" : (88 * self.scale_ratio, 145 * self.scale_ratio, 125 * self.scale_ratio, 125 * self.scale_ratio),
            "southeast" : (90 * self.scale_ratio, 130 * self.scale_ratio, 170 * self.scale_ratio, 155 * self.scale_ratio),
            "southwest" : (84 * self.scale_ratio, 130 * self.scale_ratio, 130 * self.scale_ratio, 150 * self.scale_ratio)
        }
        w,h,ox,oy = self.hitbox_data[self.facing]

        self.hitbox = pygame.Rect(self.rect.x + ox, self.rect.y + oy, w, h)
        self.attack_hitbox_points = [
            (0, 0), (20, -105), (90, -85), (135,-65),(180, 0),
            (175, 65), (100, 125), (40,100)
        ]
        
        self.animation_timer = 0
        self.animation_delay = 5
        
        self.non_interruptible = {"attack1", "attack2", "attack3", "castspell", "AttackRun", "special1", "special2", "hit"}
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
                self._activate_attack_hitbox(60)

        self._update_hitboxes()
        self.update_attack()

    def attack(self):
        if not self.locked:
            self.frame_index = 0
            self.locked = True
            self.set_animation("attack1")