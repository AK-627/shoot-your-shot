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
import editor
from editor import Editor
from block import Block, StaticBlock, MovingBlock
from level_over_menu import LevelOverMenu


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

class AppState(Enum):
    Menu = 1,
    Playing = 2,
    Editor = 3,
    LevelWon = 4,

class App:
    def __init__(self):
        self.state = AppState.Menu
        
        def oneditor():
            SCREEN = pygame.display.set_mode((editor.SCREEN_W,editor.SCREEN_H))
            self.inner = Editor(SCREEN)
            self.state = AppState.Editor
        def play():
            selected_level = self.inner.selected_level
            level = self.inner.selected_level.to_level()
            def onlevelwin():
                self.state = AppState.LevelWon
                def newlevel():
                    from main_menu import SelectedLevelType, SelectedLevel
                    level_num = self.inner.next_level_num or 0
                    self.inner = SelectedLevel(SelectedLevelType.Premade,level_num).to_level()
                    self.inner.switchstateonwin = onlevelwin
                def backtomenu():
                    self.state = AppState.Menu
                    self.inner = Menu(play,oneditor) 
                self.inner = LevelOverMenu(selected_level,self.inner.num_strokes,newlevel,backtomenu,self.inner.level_num+1)
            level.switchstateonwin = onlevelwin
            self.inner = level
            self.state = AppState.Playing
        self.inner = Menu(play,oneditor)

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
