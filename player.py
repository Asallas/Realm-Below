import pygame, os
from math import sqrt

class Player(pygame.sprite.Sprite):
    def __init__(self, position, scale=2):
        # Load the image file sprite sheet
        self.sheets = {
            "walk" : self.load_sheet("Spritesheets/PlayerAnimations/Walk.png"),
            "run" : self.load_sheet("Spritesheets/PlayerAnimations/Run.png"),
            "idle": self.load_sheet("Spritesheets/PlayerAnimations/Idle.png")
        }
        
        # Scaling factor for sprites
        self.scale = scale
        
        # Initialize a frame counter
        self.frame_index = 0

        # Set walking distance  (Current default will be around 7)
        self.distance = 7
        
        # Set initial standing position
        self.facing = 'south'
        
        # Animation timing delay
        self.animation_timer = 0
        self.animation_delay = 0
        
        self.animations = {}
        # Define directions for animations
        directions = {
            "south":256,
            "southeast": 128,
            "east": 0,
            "northeast": 896,
            "north": 768,
            "northwest": 640,
            "west": 512,
            "southwest": 384
        }
        for anim_name, sheet in self.sheets.items():
            self.animations[anim_name] = {direc for direc in directions}
            for i in range(15):
                for direct, y in directions.items():
                    self.animations[anim_name][direct][i] = (128 * i, y, 128, 128)

                
        # Set default animation
        self.current_animation = "idle"
        self.image = self.get_frame(self.current_animation, self.facing, self.frame_index)
    
    def load_sheet(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Spritesheet not found {path}")
        return pygame.image.load(path).convert_alpha()
            

    def get_frame(self, animation_name, direction, frame_set):
        rect = self.animations[animation_name][direction][frame_set]
        frame = self.sheets[animation_name].subsurface(rect)
        if self.scale != 1:
            w,h = frame.get_size()
            frame = pygame.transform.scale(frame, (int(w // self.scale), int(h // self.scale)))
        return frame
    
    def update_animations(self):
        
        pass
    
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
        scaled_size = (int(original_size[0] // self.scale), int(original_size[1] // self.scale))
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