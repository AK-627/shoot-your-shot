from enum import Enum
import time

import pygame, os
pygame.font.init()

from constants import *
SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
CLOCK = pygame.time.Clock()

from main_menu import *
from ui_misc import *
from serde import *
from ball import Ball
from level import Level
from block import Block, StaticBlock, MovingBlock


pygame.display.set_caption("Shoot Your Shot")


def create_borders():
    rects = [
            (0,0,SCREEN_W,BORDER_SIZE), 
            (0,SCREEN_H-BORDER_SIZE,SCREEN_W,BORDER_SIZE), 
            (0,BORDER_SIZE,BORDER_SIZE,SCREEN_H-BORDER_SIZE), 
            (SCREEN_W-BORDER_SIZE,BORDER_SIZE,BORDER_SIZE,SCREEN_H)    
            ]
    return [ Block(SCREEN,StaticBlock(v[0],v[1],v[2],v[3])) for v in rects ]



objs = create_borders()
LEVEL_0 = Level(SCREEN,(SCREEN_W/2,SCREEN_H/2),(SCREEN_W/2,BORDER_SIZE+BALL_RADIUS + 5),objs)
LEVEL_1 = Level(SCREEN,(SCREEN_W/2,SCREEN_H/2),(SCREEN_W/2,BORDER_SIZE+BALL_RADIUS + 5),objs)
LEVEL_1.from_dict(
{'ball_start': (660, 240), 'ball_end': (150, 270), 'ball': {'rect': {'x': 660, 'y': 240, 'w': 15, 'h': 15}, 'velocity': 0.0, 'dir': {'x': 0.0, 'y': 0.0}}, 'objects': [{'inner': {'rect': {'x': 0, 'y': 0, 'w': 1280, 'h': 30}}}, {'inner': {'rect': {'x': 0, 'y': 690, 'w': 1280, 'h': 30}}}, {'inner': {'rect': {'x': 0, 'y': 30, 'w': 30, 'h': 690}}}, {'inner': {'rect': {'x': 1250, 'y': 30, 'w': 30, 'h': 720}}}, {'inner': {'rect': {'x': 300, 'y': 210, 'w': 30, 'h': 30}}}, {'inner': {'rect': {'x': 360, 'y': 240, 'w': 30, 'h': 30}}}, {'inner': {'rect': {'x': 390, 'y': 240, 'w': 30, 'h': 30}}}, {'inner': {'rect': {'x': 360, 'y': 300, 'w': 30, 'h': 30}}}, {'inner': {'rect': {'x': 480, 'y': 240, 'w': 30, 'h': 30}}}, {'inner': {'rect': {'x': 420, 'y': 300, 'w': 30, 'h': 30}}}]}
)

#LEVELS = [LEVEL_0,LEVEL_1]

class AppState(Enum):
    Menu = 1,
    Playing = 2

class App:
    def __init__(self):
        self.state = AppState.Menu
        def play():
            level = self.inner.selected_level.to_level()
            self.inner = level
            self.state = AppState.Playing
        self.inner = Menu(play)

    def handle_input(self,event):
        return self.inner.handle_input(event)

    def update(self):
        self.inner.update()
    
    def draw(self):
        self.inner.draw()

    def switch_to_level(self,level):
        self.state = AppState.Playing
        self.inner = level


def main_loop():
    app = App()
    running = True

    while running:
        SCREEN.fill(BG_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break 
            if app.handle_input(event):
                continue
        app.update()
        app.draw()


        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main_loop()
