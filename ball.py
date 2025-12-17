import pygame
from serde import *
from constants import *

from debug import is_debug

class Ball:
    def __init__(self,screen,x,y):
        self.screen = screen
        self.rect = pygame.Rect(x,y,2*BALL_RADIUS,2*BALL_RADIUS)
        # You may wonder why we represent velocity as a scalar but also have a dir vector component. it just works better this way
        self.dir = pygame.math.Vector2(0,0)
        self.velocity = 0.0 


        self.radius = BALL_RADIUS

    def draw(self):
        # pygame draws the circle form the center, unlike a rect which it draws from the top left corner. So to avoid a discrepency, we offset the circle by self.radius
        pygame.draw.circle(self.screen,BALL_COLOR,(self.rect.x+self.radius,self.rect.y+self.radius),self.radius)

        # border
        pygame.draw.circle(self.screen,BLACK,(self.rect.x+self.radius,self.rect.y+self.radius),self.radius,2)

        # debug rect
        if is_debug:
            pygame.draw.rect(self.screen,BLACK,self.rect,2)
   
    def update(self,objects):
        # So we predict if the next position where our ball is going to be is gonna collide with something
        # We create a dummy rectangle to test our predicitions with and assign it the values our actual ball would take if we didnt check for collisions
        has_collided = False

        for obj in objects:
            rect = self.rect.copy()
            rect_x = rect.copy()
            rect_y = rect.copy()
            rect_x.x += self.velocity * self.dir.x 
            rect_y.y += self.velocity * self.dir.y

            # Now, now, theres 4 cases.
            # 1.Ball collides a block with its top surface touching the block's bottom surface (ball makes contact with an object above it)
            # 2.Ball collides a block with its bottom surface touching the block's top surface
            # 3.Ball collides a block with its left surface touching the block's right surface
            # 4.Ball collides a block with its right surface touching the block's left surface

            # Depending on the situation, we need to change the ball's velocity accordingly.
            # Example: If the ball touches an object on its right, we change the velocity (or here, the dir)'s x component to be the opposite of that
            # that is, dir.x = -dir.x

            obj_rect = obj.rect()

            # NOTES FOR DEEK:
            # add playing sounds INSIDE the if statement if its true

            # check for x-axis collision:
            if rect_x.colliderect(obj_rect):
                has_collided = True
                self.dir.x *= -1
            # check for y-axis collision:
            if rect_y.colliderect(obj_rect):
                has_collided = True
                self.dir.y *= -1
        self.move()

    def move(self):
        self.rect.x += self.velocity  * self.dir.x 
        self.rect.y += self.velocity * self.dir.y 

        if abs(self.velocity) > 1:
            self.velocity -= FRICTION * -1 if self.velocity < 0 else 1
        else:
            self.velocity = 0
    def is_moving(self):
        return self.velocity != 0
    
    """ Calculates the force (with its direction) when initial and final position of the mouse are given. This is what we use when we drag and release the mouse to shoot the ball """
    def calc_force(self,initial_pos,final_pos):
        initial_pos = pygame.math.Vector2(initial_pos)
        final_pos = pygame.math.Vector2(final_pos)

        # In our game, force and velocity mean the same thing ok (just simplyifes things)
        vel = min((initial_pos - final_pos).magnitude(),MAX_VELOCITY)
        if vel == 0: return

        dir_ = (initial_pos-final_pos).normalize()
        self.velocity = vel * 0.1
        self.dir = dir_

    def from_dict(self,dict_):
        self.rect = rect_from_dict(dict_.get('rect'))
        self.velocity = dict_.get('velocity') or 0
        self.dir = vector2_from_dict(dict_.get('vector2'))

    def to_dict(self):
        d = {}
        d['rect'] = rect_to_dict(self.rect)
        d['velocity'] = self.velocity 
        d['dir'] = vector2_to_dict(self.dir)
        return d


