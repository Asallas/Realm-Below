# projectile.py
import pygame, math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, target_pos, speed=12, color=(255, 0, 0), radius=10):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=position)

        # Compute direction vector toward the target
        direction = pygame.Vector2(target_pos) - pygame.Vector2(position)
        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)
        self.velocity = direction.normalize() * speed



    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        screen_w, screen_h = 1920, 1080
        if (
            self.rect.right < 0
            or self.rect.left > screen_w
            or self.rect.bottom < 0
            or self.rect.top > screen_h
        ):
            self.kill()

