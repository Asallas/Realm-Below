import pygame
import math
import os

class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, target_pos, speed=12, radius=10,
                 img_folder="Spritesheets/RangeEnemy/2"):
        super().__init__()

        # ---------- Load all frames ----------
        # Files named: 1_0.png, 1_1.png, ..., 1_29.png
        self.frames = []
        for i in range(30):
            path = os.path.join(img_folder, f"1_{i}.png")
            img = pygame.image.load(path).convert_alpha()
            self.frames.append(img)

        self.frame_index = 0
        self.frame_delay = 2     # how fast animation cycles
        self.frame_timer = 0

        # ---------- Original hitbox (same as old ball) ----------
        self.base_radius = radius
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = position

        # Used for collision — same as original ball
        self.collision_rect = pygame.Rect(self.rect)

        # ---------- Compute direction ----------
        direction = pygame.Vector2(target_pos) - pygame.Vector2(position)
        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)
        self.velocity = direction.normalize() * speed

        # ---------- Precompute rotation angle ----------
        # atan2 gives angle where 0 deg is to the right
        self.angle = -math.degrees(math.atan2(self.velocity.y, self.velocity.x))

        # Render first rotated frame
        self.image = pygame.transform.rotate(self.frames[0], self.angle)


    def update(self):

        # ---------- Move like original projectile ----------
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Keep collision rect centered correctly
        self.collision_rect.center = self.rect.center

        # ---------- Animate ----------
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # Rotate current frame to match trajectory direction
        self.image = pygame.transform.rotate(self.frames[self.frame_index], self.angle)

        # ---------- Off-screen kill ----------
        if (
            self.rect.right < 0
            or self.rect.left > 1920
            or self.rect.bottom < 0
            or self.rect.top > 1080
        ):
            self.kill()
