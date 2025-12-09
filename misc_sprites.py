import pygame

class Ward(pygame.sprite.Sprite):
    """
    Single ward sprite that:
      - has an animation of frames (5x3 grid, frame size 192x192)
      - plays first 5 frames, then PAUSES (paused=True)
      - when .resume() is called (after player hitbox intersects ward.hitbox), it continues
        the animation until the end then kills itself.
      - provides a small rectangular .hitbox (64 tall x 32 wide, located 32 px down from top)
    """
    def __init__(self, center_pos, spritesheet, frame_w=192, frame_h=192, cols=5, rows=3,
                 anim_delay=12, scale=1.0):
        super().__init__()
        self.center = pygame.Vector2(center_pos)
        self.spritesheet = spritesheet
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.cols = cols
        self.rows = rows
        self.scale = scale

        # build frame rects (assume spritesheet origin at 0,0 and frames laid row-major)
        total_frames = cols * rows
        self.frame_rects = [pygame.Rect((i % cols) * frame_w, (i // cols) * frame_h, frame_w, frame_h)
                            for i in range(total_frames)]

        self.anim_delay = anim_delay
        self.anim_timer = 0
        self.frame_index = 0
        self.paused = False           # becomes True after initial 5 frames
        self.finished = False

        # prepare initial image
        rect = self.frame_rects[0]
        frame = self.spritesheet.subsurface(rect)
        if scale != 1.0:
            frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
        self.image = frame
        self.rect = self.image.get_rect(center=self.center)

        # hitbox: "roughly a 64 tall by 32 wide rectangle which is 32 pixels down from the top"
        # We'll compute in world coords and update on rect changes.
        hw = 192
        hh = 192
        # relative top-left offset from sprite top-left to hitbox top-left
        # 32 px down from top -> y offset = 32*scale
        # horizontally center the small hitbox
        self.hitbox = pygame.Rect(self.rect.left,
                                  self.rect.top,
                                  hw, hh)

    def update(self):
        if self.finished:
            return

        # advance animation only if not paused
        if not self.paused:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.frame_index += 1
                if self.frame_index >= len(self.frame_rects):
                    # animation finished -> remove
                    self.finished = True
                    self.kill()
                    return

                # set new image and preserve center
                rect = self.frame_rects[self.frame_index]
                frame = self.spritesheet.subsurface(rect)
                if self.scale != 1.0:
                    frame = pygame.transform.scale(frame, (int(frame.get_width() * self.scale),
                                                           int(frame.get_height() * self.scale)))
                old_center = self.rect.center
                self.image = frame
                self.rect = self.image.get_rect(center=old_center)

                # update hitbox location after resizing/frame change
                self.hitbox = pygame.Rect(self.rect.left,
                                          self.rect.top,
                                          self.hitbox.width, self.hitbox.height)

                # Pause automatically after the first 5 frames (index 0..4 -> after index 4)
                if self.frame_index >= 4 and not self.paused:
                    # Pause at frame index 4 (that's the 5th frame)
                    self.paused = True
                    # keep the image on that 5th frame until resumed
                    # do NOT advance further until .resume() is called

    def resume(self):
        """Resume the paused animation; if not paused this is a no-op."""
        if self.paused:
            self.paused = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # debug draw hitbox (optional)
        pygame.draw.rect(surface, (255,0,255), self.hitbox, 2)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, position, spritesheet, frame_rects, scale=2, anim_delay=3):
        super().__init__()

        self.frame_rects = frame_rects
        self.spritesheet = spritesheet
        self.scale = scale
        self.anim_delay = anim_delay
        
        self.frames = []
        for rect in frame_rects:
            frame = spritesheet.subsurface(rect).copy()
            if scale != 1:
                frame = pygame.transform.scale(frame, (rect.w * scale, rect.h * scale))
            self.frames.append(frame)

        self.frame_index = 0
        self.timer = 0

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=position)

        # --------------------
        # HITBOX DEFINITION
        # Sprite final size is 64*scale.
        # Hitbox = 32×32 area positioned 32px down.
        # --------------------
        hit_w = 64 * scale
        hit_h = 32 * scale
        offset_y = 32 * scale

        # Center horizontally inside the 64×64 frame
        hit_x = self.rect.x + (self.rect.width - hit_w) // 2
        hit_y = self.rect.y + offset_y

        self.hitbox = pygame.Rect(hit_x, hit_y, hit_w, hit_h)

    def update(self):
        self.timer += 1
        if self.timer >= self.anim_delay:
            self.timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                # Explosion finished → remove itself
                self.kill()
                return
            
            # Update frame image
            old_center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=old_center)

            # --- Update hitbox position every frame ---
            hit_w = 32 * self.scale
            hit_h = 32 * self.scale
            offset_y = 32 * self.scale
            hit_x = self.rect.x + (self.rect.width - hit_w) // 2
            hit_y = self.rect.y + offset_y
            self.hitbox.update(hit_x, hit_y, hit_w, hit_h)
    
