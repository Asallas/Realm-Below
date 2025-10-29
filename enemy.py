import pygame
from character import Character
class Enemy(Character):
    def __init__(self, position, scale):
        super().__init__(self, position, scale)
        self.sheets = {
            "walk" : self.load_sheets("Spritesheets/MeleeEnemy/Walk.png"),
            "idle" : self.load_sheets("Spritesheets/MeleeEnemy/Idle.png")
        }

        self.health = 5

