import pygame
from math import sqrt
class Player(pygame.sprite.Sprite):
    def __init__(self, position, scale=3):
        # Load the image file sprite sheet
        self.sheet = pygame.image.load('Soldier-Blue.png')
        
        # Define the area of a single sprite
        self.sheet.set_clip(pygame.Rect(0,0,32,32))
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        
        # Scaling original image
        self.scale = scale
        original_size = self.image.get_size()
        scaled_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        self.image = pygame.transform.scale(self.image, scaled_size)
        
        # Get and set the rectangle of the current sprite image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        
        # Initialize a frame counter
        self.frame = 0

        # Set walking distance  (Current default will be around 7)
        self.distance = 30
        
        # Set initial standing position
        self.facing = 'south'
        # Animation timing delay
        self.animation_timer = 0
        self.animation_delay = 7
        
        # Define states of animations
        directions = {
            "south":0,
            "southeast": 32,
            "east": 64,
            "northeast": 96,
            "north": 128,
            "northwest": 160,
            "west": 192,
            "southwest": 224
        }
        self.states = {name: {} for name in directions}

        # Add different states from spritesheet below
        for i in range(4):
            for name,y in directions.items():
                self.states[name][i] = (32*i, y, 32,32)

    def get_frame(self, frame_set):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.frame = (self.frame + 1) % len(frame_set)
            self.animation_timer = 0
        return frame_set[self.frame]
    
    def clip(self, clipped_rect):
        if type(clipped_rect) is dict:
            self.sheet.set_clip(pygame.Rect(self.get_frame(clipped_rect)))
        else:
            self.sheet.set_clip(pygame.Rect(clipped_rect))
        return clipped_rect
    
    def update(self, direction):

        diagonal = self.distance / sqrt(2)

        if direction == 'N':
            self.facing = 'north'
            self.clip(self.states["north"])
            self.rect.y -= self.distance

        if direction == 'E':
            self.facing = 'east'
            self.clip(self.states["east"])
            self.rect.x += self.distance
            
        if direction == 'S':
            self.facing = 'south'
            self.clip(self.states["south"])
            self.rect.y += self.distance

        if direction == 'W':
            self.facing = 'west'
            self.clip(self.states["west"])
            self.rect.x -= self.distance

        if direction == 'NE':
            self.facing = 'northeast'
            self.clip(self.states["northeast"])
            self.rect.x += diagonal
            self.rect.y -= diagonal

        if direction == 'NW':
            self.facing = 'northwest'
            self.clip(self.states["northwest"])
            self.rect.x -= diagonal
            self.rect.y -= diagonal

        if direction == 'SE':
            self.facing = 'southeast'
            self.clip(self.states["southeast"])
            self.rect.x += diagonal
            self.rect.y += diagonal
            
        if direction == 'SW':
            self.facing = 'southwest'
            self.clip(self.states["southwest"])
            self.rect.x -= diagonal
            self.rect.y += diagonal
        
        if direction == 'stand':
            self.clip(self.states[self.facing][0])
        
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        original_size = self.image.get_size()
        scaled_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
        self.image = pygame.transform.scale(self.image, scaled_size)
            
        
    def handle_event(self, event):
        if event.type == pygame.KEYUP: 
            self.update('stand')
        if event.type in (pygame.KEYDOWN,pygame.KEYUP):
            keys = pygame.key.get_pressed()
            direction = 'stand'
            if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
                direction = 'NE'
            elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
                direction = 'NW'
            elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
                direction = 'SE'
            elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
                direction = 'SW'
            elif keys[pygame.K_UP]:
                direction = 'N'
            elif keys[pygame.K_DOWN]:
                direction = 'S'
            elif keys[pygame.K_RIGHT]:
                direction = 'E'
            elif keys[pygame.K_LEFT]:
                direction = 'W'
            
            self.update(direction)