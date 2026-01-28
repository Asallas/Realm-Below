import pygame
from character import Character
from misc_sprites import Explosion, Ward

class Boss(Character):
    def __init__(self, position, scale=2, SCREEN_WIDTH = 1920, SCREEN_HEIGHT = 1080):
        super().__init__(position, scale)
        # ----------------------- Spritesheets ------------------------
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/BossEnemy/Walk.png", "walk", 192, 192),
            "run" : self.load_sheet("Spritesheets/BossEnemy/Run.png", "run",192,192),
            "idle" : self.load_sheet("Spritesheets/BossEnemy/Idle.png", "idle", 192,192),
            "attack1" : self.load_sheet("Spritesheets/BossEnemy/Attack1.png", "attack1",192,192),
            "attack2" : self.load_sheet("Spritesheets/BossEnemy/Attack2.png", "attack2",192,192),
            "attack3" : self.load_sheet("Spritesheets/BossEnemy/Attack3.png", "attack3",192,192),
            "crouch" : self.load_sheet("Spritesheets/BossEnemy/CrouchIdle.png", "crouch",192,192),
            "castspell" : self.load_sheet("Spritesheets/BossEnemy/CastSpell.png", "castspell",192,192),
            "idle2" : self.load_sheet("Spritesheets/BossEnemy/Idle2.png", "idle2",192,192),
            "AttackRun" : self.load_sheet("Spritesheets/BossEnemy/AttackRun.png", "AttackRun",192,192),
            "special1" : self.load_sheet("Spritesheets/BossEnemy/Special1.png", "special1",192,192),
            "special2" : self.load_sheet("Spritesheets/BossEnemy/Special2.png", "special2",192,192),
            "hit" : self.load_sheet("Spritesheets/BossEnemy/TakeDamage.png", "hit", 192,192),
            "death" : self.load_sheet("Spritesheets/BossEnemy/Die.png", "death", 192,192)
        }
        self.explosion_spritesheet = pygame.image.load("Spritesheets/BossEnemy/Retro Impact Effect Pack 5 A.png").convert_alpha()
        self.explosion_frame_rects = [
            pygame.Rect(i * 64, 1216, 64, 64) for i in range(8)
        ]
         # ----------------- Attacks ------------------
        self.target = None
        self.attack_range = 100
        self.attack_cooldown = 3000
        self.last_attack_time = 0
        self.speed = 3

        #------ Special Sequence flage --------
        self.arena_center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.attack_seq_state = None
        self.warning_alpha = 0
        self.last_special_start = pygame.time.get_ticks()
        
        # Explosion spawning
        self.cast_spawn_trigger_frame = 10
        self.cast_spawn_interval_frames = 3
        self.cast_spawn_steps = 8
        self.cast_spawn_spacing = 64
        self.dirs = [
            pygame.Vector2(0, -1),   # N
            pygame.Vector2(1, -1).normalize(),  # NE
            pygame.Vector2(1, 0),    # E
            pygame.Vector2(1, 1).normalize(),   # SE
            pygame.Vector2(0, 1),    # S
            pygame.Vector2(-1, 1).normalize(),  # SW
            pygame.Vector2(-1, 0),   # W
            pygame.Vector2(-1, -1).normalize()  # NW
        ]

        self.explosions = pygame.sprite.Group()
        
        # ---------- Summon Flags ---------------
        self.summon_phase_started = False
        self.summon_state = None
        self.pending_spawns = []
        self._spawn_positions = []
        self._spawn_scale = 1.0
        self.summon_spawn_delay = 1000
        self.next_summon_time = 0
        self._spawn_queue = []
        self._spawn_refs_total = []

        # ----------- Ward Flags ------------
        self.wards = pygame.sprite.Group()
        self.ward_spritesheet = pygame.image.load("Spritesheets/BossEnemy/ward-Effect.png")
        self.ward_frame_w = 192
        self.ward_frame_h = 192
        self.ward_cols = 5
        self.ward_rows = 3
        self.ward_scale = 1.0
        self.ward_anim_delay = 6
        self._ward_phase_started = False


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
        
        #-------------- Animations -------------------

        self.animation_timer = 0
        self.animation_delay = 5
        
        self.non_interruptible = {"attack1", "attack2", "attack3", "castspell", "AttackRun", "special1", "special2", "hit"}
        self.looping = {"walk", "idle", "run", "crouch"}

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

        self.check_enter_summon_phase()

        self.check_enter_ward_phase()
        if self.summon_state == "wards_active":
            self.update_wards()
            self.update_animations()
            #self._update_hitboxes()
            self.wards.update()
            return

        if self.attack_seq_state is not None:
            self.run_attack_sequence()
            self.update_animations()
            #self._update_hitboxes()
            self.explosions.update()
            return
        
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
                self._activate_attack_hitbox(30)


        if self.summon_state == "spawning":
            if now >= self.next_summon_time and self._spawn_queue:
                self._spawn_one_from_queue()
                self.next_summon_time = now + self.summon_spawn_delay
            if not self._spawn_queue:
                self.summon_state = "spawned_waiting"
                print("Boss has finished spawning")
        self._update_hitboxes()
        self.update_attack()

    def attack(self):
        if not self.locked:
            self.frame_index = 0
            self.locked = True
            self.set_animation("attack1")

    def start_attack_sequence(self):
        # Teleport to center
        self.rect.center = self.arena_center_pos

        self.suppress_auto_idle = True
        self.locked = True
        self.facing = "south"
    
        self.set_animation("hit")
        self.frame_index = 0
        self.attack_seq_state = "charge_up"
        self.sequence_timer = 0
        self.warning_alpha = 0

        self.cast_num_waves = 14
        self.cast_wave_interval = 4
        self._cast_wave_index = 0
        self._cast_wave_timer = 0

        self._cast_wave_spawned = [
            [False] * self.cast_num_waves for _ in range(len(self.dirs))
        ]

        self.freeze_animation = False

        print("Boss special attack sequence started")
    
    def run_attack_sequence(self):
        if not self.attack_seq_state:
            return
        
        state = self.attack_seq_state
        if state == "charge_up":
            if self.frame_index >= 13:
                self.attack_seq_state = "warning_line"
                self.sequence_timer = 0
                self.freeze_animation = True
                self.frame_index = 13
                print("Boss entered warning phase")
            return
        
        if state == "warning_line":
            self.sequence_timer += 1

            alpha = min(255, int((self.sequence_timer / 160.0) * 255))
            self.warning_alpha = alpha
            if self.sequence_timer >= 120:
                self.freeze_animation = False
                self.set_animation("castspell")
                self.frame_index = 0
                self.attack_seq_state = "cast_spell"
                self._cast_wave_index = 0
                self._cast_wave_timer = 0

                print("Boss is now casting")
            return
        
        if state == "cast_spell":
            self._cast_wave_timer += 1

            if self._cast_wave_timer >= self.cast_wave_interval and self._cast_wave_index < self.cast_num_waves:
                wave = self._cast_wave_index
                # spawn one ring at distance = (wave + 1) * spacing
                dist = (wave + 1) * self.cast_spawn_spacing
                for d_idx, dvec in enumerate(self.dirs):
                    # spawn only once per dir/wave
                    if not self._cast_wave_spawned[d_idx][wave]:
                        spawn_pos = pygame.Vector2(self.rect.center) + dvec * dist
                        exp = Explosion(
                            position=spawn_pos,
                            spritesheet=self.explosion_spritesheet,
                            frame_rects=self.explosion_frame_rects,
                            scale=2,
                            anim_delay=3
                        )
                        self.explosions.add(exp)
                        self._cast_wave_spawned[d_idx][wave] = True
                # consumed this wave; advance
                self._cast_wave_index += 1
                self._cast_wave_timer = 0

            # Update explosions each frame (they will self-kill at animation end)
            self.explosions.update()

            cast_anim_len = len(self.animations.get("castspell", {}).get(self.facing, []))
            waves_done = (self._cast_wave_index >= self.cast_num_waves)
            no_explosions_left = (len(self.explosions) == 0)
            if waves_done and no_explosions_left:
                self.suppress_auto_idle = False
                self.set_animation("idle")
                self.locked = False
                self.attack_seq_state = None

                print("Boss attack sequence finished")
            return

    def draw_warning_lines(self, screen, center, dirs, length, a, width =6):
        if a <= 0:
            return
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        color = (255,0,0, max(0, min(255, int(a))))
        cx,cy = int(center[0]), int(center[1])
    
        for d in dirs:
            ex = cx + int(d.x * length)
            ey = cy + int(d.y * length)
            pygame.draw.line(overlay, color, (cx, cy), (ex,ey), width)

            taper_color = (255,0,0,max(0,min(255, int(a * .35))))
            inner_ex = cx + int(d.x * (length * 0.6))
            inner_ey = cy + int(d.y * (length * 0.6))
            pygame.draw.line(overlay, taper_color, (cx,cy), (inner_ex, inner_ey), max(1, width //3))
        
        screen.blit(overlay, (0,0))
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.attack_seq_state == 'warning_line':
            self.draw_warning_lines(screen, self.rect.center, self.dirs, length=900, a=self.warning_alpha, width=32)
        if len(self.explosions) > 0:
            self.explosions.draw(screen)
        if len(self.wards) > 0:
            self.wards.draw(screen)

    
    # ---------- Summon phase helpers ----------
    def check_enter_summon_phase(self):
        """
        Called from update() to detect the health threshold and start the sequence.
        Boss will only start the summon after finishing idle/walk (i.e. not mid-attack).
        """
        if self.summon_phase_started:
            return

        # only trigger when hp <= 50% and boss is currently idle/walk
        if self.health <= (self.max_health * 0.5):
            if self.current_animation in ("idle", "walk") and not self.locked:
                # ready to teleport + crouch
                self.begin_summon_phase()
                self.summon_phase_started = True

    def begin_summon_phase(self):
        """Teleport to center, play crouch animation, and prepare the spawn list."""
        # teleport instantly
        self.rect.center = self.arena_center_pos

        # make boss invulnerable and locked while the phase runs
        self.invulnerable = True
        self._hitbox_debug = True
        self.disable_hitbox(manual=True)
        self.locked = True
        self.attack_hitbox = None

        # set facing and play crouch
        self.facing = "south"
        self.set_animation("crouch")
        self.frame_index = 0

        # prepare spawn world positions relative to boss center:
        cx, cy = pygame.Vector2(self.arena_center_pos)
        east = (cx + 300, cy)
        west = (cx - 300, cy)
        south = (cx, cy + 300)

        self._spawn_queue = [
        ("range", east),
        ("melee", south),
        ("range", west),
    ]

        # clear any prior holders
        self.pending_spawns = []         # will hold instances created THIS FRAME for main to pick up
        self._spawn_refs_total = []      # will accumulate all spawned refs for later checking

        self.summon_state = "spawning"
        self.next_summon_time = pygame.time.get_ticks() + self.summon_spawn_delay
        print("Boss: begin_summon_phase() - teleported + crouch started")

    def _spawn_one_from_queue(self):
        """Create a single enemy instance from the queue and append it to self.pending_spawns."""
        if not self._spawn_queue:
            return

        typ, pos = self._spawn_queue.pop(0)  # FIFO

    # local import (avoids circular import issues)
        from enemys import MeleeEnemy, RangeEnemy

        if typ == "range":
            inst = RangeEnemy(tuple(pos), scale=1)
        else:
            inst = MeleeEnemy(tuple(pos), scale=1)

        # Add to pending_spawns so main will pick it up this frame
        self.pending_spawns.append(inst)

        # Also add to our local total refs so we can detect when they're dead
        self._spawn_refs_total.append(inst)
        print(f"Boss: queued minion spawned -> {typ} at {pos}")


    # ------------- Ward summoning ------------
    def check_enter_ward_phase(self):
        """Trigger the ward phase at <=25% HP, only when in idle/walk and not locked."""
        if self._ward_phase_started:
            return
        if self.health <= (self.max_health * 0.25):
            if self.current_animation in ("idle", "walk") and not self.locked:
                self.begin_ward_phase()
                self._ward_phase_started = True

    def begin_ward_phase(self):
        """Teleport to center, become invulnerable + crouch, spawn four wards at cardinal positions."""
        # teleport instantly
        self.rect.center = self.arena_center_pos

        # boss locked & invulnerable during ward phase
        self.invulnerable = True
        self.disable_hitbox(manual=True)
        self.locked = True
        self.attack_hitbox = None

        # facing south & play crouch
        self.facing = "south"
        self.set_animation("crouch")
        self.frame_index = 0

        # ward positions (cardinals) - distance from boss center
        spacing = 300
        cx, cy = pygame.Vector2(self.arena_center_pos)
        positions = [
            (cx, cy - spacing),  # north
            (cx + spacing, cy),  # east
            (cx, cy + spacing),  # south
            (cx - spacing, cy),  # west
        ]

        # create and add ward instances to self.wards
        self.wards.empty()
        for pos in positions:
            w = Ward(center_pos=pos,
                     spritesheet=self.ward_spritesheet,
                     frame_w=self.ward_frame_w, frame_h=self.ward_frame_h,
                     cols=self.ward_cols, rows=self.ward_rows,
                     anim_delay=self.ward_anim_delay,
                     scale=self.ward_scale)
            self.wards.add(w)

        # record we are in ward phase
        self.summon_state = "wards_active"

        now = pygame.time.get_ticks()
        self.ward_start_time = now
        self.ward_duration_ms = 15_000
        self.ward_tick_interval_ms = 2_000
        self._next_ward_tick = now + self.ward_tick_interval_ms
        self.ward_failed = False

        print("Boss: began ward phase - spawned 4 wards; boss crouched/invulnerable")

    def update_wards(self):
        """Advance and manage ward group (called each update while ward phase active)."""
        now = pygame.time.get_ticks()
        # update ward animations
        self.wards.update()

        if now >= getattr(self, "_next_ward_tick", 0) and not self.ward_failed:
            for step in range(self.cast_spawn_steps):
                dist = (step + 1) * self.cast_spawn_spacing
                for dvec in self.dirs:
                    spawn_pos = pygame.Vector2(self.rect.center) + dvec * dist
                    exp = Explosion(
                        position=spawn_pos,
                        spritesheet=self.explosion_spritesheet,
                        frame_rects=self.explosion_frame_rects,
                        scale=2,
                        anim_delay=3
                    )
                    self.explosions.add(exp)
            self._next_ward_tick = now + self.ward_tick_interval_ms

        self.explosions.update()

        if not self.ward_failed:
            elapsed = now - getattr(self, "ward_start_time", now)
            if elapsed >= getattr(self, "ward_duration_ms", 15000):
                if len(self.wards) > 0:
                    self.ward_failed = True

                    for step in range(self.cast_spawn_steps):
                        dist = (step + 1) * self.cast_spawn_spacing
                        for dvec in self.dirs:
                            spawn_pos = pygame.Vector2(self.rect.center) + dvec * dist
                            exp = Explosion(
                                position=spawn_pos,
                                spritesheet=self.explosion_spritesheet,
                                frame_rects=self.explosion_frame_rects,
                                scale=4, anim_delay=3
                            )
                            self.explosions.add(exp)

        # If no wards left, end phase
        if len(self.wards) == 0 and not self.ward_failed:
            self.summon_state = None
            self.invulnerable = False
            self.enable_hitbox(manual=True)
            self.locked = False
            print("Boss: ward phase finished - resume normal behavior")
