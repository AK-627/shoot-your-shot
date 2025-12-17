import pygame
from constants import *
from ball import Ball
from block import Block
from enum import Enum

import time


class LevelState(Enum): 
    PLAYING = 1
    WON = 2

"""
    Manages everything realted to a specific level (like collisions, drawing, drawing menus etc)
"""
class Level:
    def __init__(self,screen,start,end,objs,switchstateonwin=None,is_premade:bool=False,level_num=None):
        self.screen = screen
        self.ball_start = start
        self.ball = Ball(self.screen,start[0],start[1])
        self.ball_end = end
        self.objects = objs
        self.is_premade = is_premade
        self.level_num = level_num

        self.state = LevelState.PLAYING
        # This stores the initial and final/current position of the mouse when it was first clicked at the start of every shot
        self.mouse_initial_pos = None
        self.mouse_final_pos = None

        self.num_strokes = 0
        self.start_time = time.time()

        # text stuff (make sure you call pygame.font.init() before)
        # default_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(None,40)

        self.level_end_anim = 0.0

        def onlevelwin():
            self.state = LevelState.WON
            self.ball.rect.x = self.ball_end[0]
            self.ball.rect.y = self.ball_end[1]
            self.level_end_anim = 0.0

        self.onlevelwin = onlevelwin
        self.switchstateonwin = None

    def draw(self):

        if self.mouse_initial_pos is not None and self.mouse_final_pos is not None :
            mouse_pos_initial_v = pygame.math.Vector2(self.mouse_initial_pos or (self.ball.rect.x,self.ball.rect.y))
            mouse_pos_final_v = pygame.math.Vector2(self.mouse_final_pos or (self.ball.rect.x,self.ball.rect.y))
            dir_v =  mouse_pos_initial_v - mouse_pos_final_v
            if dir_v.magnitude() != 0:

                x_vector = pygame.math.Vector2(1,0)

                theta = dir_v.angle_to(x_vector)

                dir_ = dir_v.normalize()
                rect = self.ball.rect
                radius = self.ball.radius
                o = pygame.math.Vector2(rect.x+radius,rect.y+radius)
                p1_ = pygame.math.Vector2(BALL_RADIUS,0)
                p2_ = pygame.math.Vector2(-BALL_RADIUS,0)
                p3_ = pygame.math.Vector2(0,-BALL_RADIUS) 

                p1 = o + p1_.rotate(90-theta)
                p2 = o + p2_.rotate(90-theta)
                p3 = o + p3_.rotate(90-theta) *  max(2,dir_v.magnitude()//50) 
                pygame.draw.polygon(self.screen,WHITE,[p1,p2,p3])

        for obj in self.objects:
            obj.draw()
        pygame.draw.circle(self.screen,BLACK,self.ball_end,HOLE_RADIUS)
        
        self.ball.draw()

        text_surface = self.font.render('Number of strokes: {}'.format(self.num_strokes),True,WHITE)
        self.screen.blit(text_surface,(BORDER_SIZE+10,30))




    def update(self):
        if self.state == LevelState.WON and self.level_end_anim == 1.0 and self.switchstateonwin: 
            self.switchstateonwin()

        end_rect = pygame.Rect(self.ball_end[0],self.ball_end[1],HOLE_RADIUS,HOLE_RADIUS)

        ball_rect = self.ball.rect
        if ball_rect.colliderect(end_rect):
            self.state = LevelState.WON
            self.onlevelwin()
            
        match self.state:
            case LevelState.PLAYING:
                self.ball.update(self.objects)
                for obj in self.objects:
                    obj.update()
            case LevelState.WON:
                if self.ball.radius > 1.0:
                   self.ball.radius -= 0.5 * self.ball.radius/10
                else:
                    if self.switchstateonwin:
                        self.switchstateonwin()
                    
    """
        Handles Mouse Events.
        RETURNS True if the event was used by it, else False
    """
    def handle_mouse_event(self,event):
        if self.ball.is_moving(): return False
        if self.mouse_initial_pos is not None:
            self.mouse_final_pos = pygame.mouse.get_pos()
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                btn = event.button
                pos = event.pos
                if btn == MOUSE_BUTTON_ONE:
                    self.mouse_initial_pos = pos
                return True
            case pygame.MOUSEBUTTONUP:
                if not self.mouse_initial_pos or not self.mouse_final_pos: return False
                btn = event.button
                pos = event.pos
                if btn == MOUSE_BUTTON_ONE:
                    self.mouse_final_pos = pos
                    self.ball.calc_force(self.mouse_initial_pos or (0,0),self.mouse_final_pos or (0,0))
                    if (pygame.math.Vector2(self.mouse_initial_pos)-pygame.math.Vector2(self.mouse_final_pos)).magnitude() != 0:
                        self.num_strokes += 1
                self.mouse_initial_pos = None
                self.mouse_final_pos = None
                return True
        return False

    def handle_input(self,event):
        return self.handle_mouse_event(event)

    def from_dict(self,dict_):
        # We can also just error out if we dont find any of these
        start = dict_.get('ball_start') or (0,0)
        self.ball_start = start
        self.ball = Ball(self.screen,start[0],start[1])
        self.ball_end = dict_.get('ball_end') or (10,10)
        objs = [  Block(self.screen,None) for _ in range(len(dict_.get('objects') or [])) ]
        for i,o in enumerate(dict_.get('objects') or []):
            objs[i].from_dict(o)
        self.objects = objs

        # These things i dont think we'll be using
        self.state = LevelState.PLAYING
        self.mouse_initial_pos = None
        self.mouse_final_pos = None
        self.num_strokes = 0
    def to_dict(self):
        d = {}
        d['ball_start'] = self.ball_start
        d['ball_end'] = self.ball_end
        d['ball'] = self.ball.to_dict()
        d['objects'] = [obj.to_dict() for obj in self.objects]
        return d
