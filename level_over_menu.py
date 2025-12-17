import pygame
from constants import *
from level import Level
from ui_misc import *
from main import SCREEN,CLOCK

from math import sin
from enum import Enum


WIN_TITLE_FONT = load_game_font(40)

class LevelOverMenu:
    def __init__(self,cur_level,num_strokes,onnextlevelbuttonclicked,onbackbuttonclicked,next_level_num):
        self.onnextlevelbuttonclicked = onnextlevelbuttonclicked  
        self.onbackbuttonclicked = onbackbuttonclicked  
        self.num_strokes = num_strokes
        self.hover_state = {"next":0.0, "back":0.0}
        self.next_level_num = next_level_num
        MENU_SIZE = (500,500)
        PADDING = 50
        BUTTON_H = 75 
        self.is_premade = cur_level.is_premade() 
        
        MENU_POS = (SCREEN_W/2-MENU_SIZE[0]/2,SCREEN_H/2-MENU_SIZE[1]/2)
        self.menu_rect = pygame.Rect(MENU_POS[0],MENU_POS[1],MENU_SIZE[0],MENU_SIZE[1])
        self.title_txt =  WIN_TITLE_FONT.render("You Win!",True,ACCENT)
        self.title_pos = (SCREEN_W//2-self.title_txt.get_width()//2, MENU_POS[1])


        self.num_strokes_txt =  SMALL_FONT.render("Number of strokes:"+str(self.num_strokes),True,ACCENT)
        self.num_strokes_pos =  (SCREEN_W//2-self.num_strokes_txt.get_width()//2,MENU_POS[1]+self.title_txt.get_height()+PADDING)

        play_next_size = (2*MENU_SIZE[0]/3,BUTTON_H)
        self.play_next_rect = pygame.Rect(SCREEN_W//2-play_next_size[0]//2,MENU_POS[1]+self.title_txt.get_height()+2*PADDING,play_next_size[0],play_next_size[1])

        back_to_menu_size = (2*MENU_SIZE[0]/3,BUTTON_H)
        self.back_to_menu_rect = pygame.Rect(SCREEN_W//2-back_to_menu_size[0]//2,MENU_POS[1]+self.title_txt.get_height()+3*PADDING+play_next_size[1],back_to_menu_size[0],back_to_menu_size[1])

    def draw(self):
        now = pygame.time.get_ticks() / 1000.0
        dt = CLOCK.get_time()/1000.0
        mouse_pos = pygame.mouse.get_pos()
        
        pygame.draw.rect(SCREEN,LIGHT_GREEN,self.menu_rect)

        SCREEN.blit(self.title_txt,self.title_pos)
        SCREEN.blit(self.num_strokes_txt,self.num_strokes_pos)
        if self.is_premade and self.next_level_num <= len(LEVELS_DICTS)-1:
            draw_button_scaled(SCREEN,self.play_next_rect,"Play Next",self.hover_state["next"])
        draw_button_scaled(SCREEN,self.back_to_menu_rect,"Back to Menu",self.hover_state["back"])
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(mouse_pos[0],mouse_pos[1],1,1)
        if mouse_rect.colliderect(self.play_next_rect):
            self.hover_state["next"] = 1.0
        else:
            self.hover_state["next"] = 0.0
        if mouse_rect.colliderect(self.back_to_menu_rect):
            self.hover_state["back"] = 1.0
        else:
            self.hover_state["back"] = 0.0

    def handle_input(self,event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mouse_pos = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(mouse_pos[0],mouse_pos[1],1,1)
        if mouse_rect.colliderect(self.play_next_rect):
            if self.onnextlevelbuttonclicked:self.onnextlevelbuttonclicked()
            return True
        if mouse_rect.colliderect(self.back_to_menu_rect):
            if self.onbackbuttonclicked: self.onbackbuttonclicked()
            return True
        return False

