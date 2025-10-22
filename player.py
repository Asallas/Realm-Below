import pygame
class Player(pygame.sprite.Sprite):
    def __init__(self, position, scale=2):
        # Load the image file sprite sheet
        self.sheet = pygame.image.load('Soldier-Blue.png')
        
        # Define the area of a single sprite
        self.sheet.set_clip(pygame.Rect(0,0,32,32))
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        
        # Scaling original image
        original_size = self.image.get_size()
        scaled_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        self.image = pygame.transform.scale(self.image, scaled_size)
        
        # Get and set the rectangle of the current sprite image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        
        # Initialize a frame counter
        self.frame = 0
        
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
            #                           (L,   T, H,  W)
        
    def update(self, direction):
        if direction == 'N':
            pass
        if direction == 'E':
            pass
        if direction == 'S':
            pass
        if direction == 'W':
            pass
        if direction == 'NE':
            pass
        if direction == 'NW':
            pass
        if direction == 'SE':
            pass
        if direction == 'SW':
            pass
        
    def handle_event(self, event):
        pass        
        
        
        
        
    pass