import pygame
import time
from enum import Enum


# pygame setup
pygame.init()
pygame.font.init()

# Screen consts
SCREEN_W, SCREEN_H = 1280,720

# Color consts
BLACK = 0,0,0
WHITE = 255,255,255
MAROON = 128, 0, 0
RED = 255,0,0
DARK_GREEN =  0, 100,0 
LIGHT_GREEN =  45, 207, 70

BG_COLOR = 45,207,70
BLOCK_COLOR = DARK_GREEN

# Game object consts

""" Represents the borders width (if its verticle) or its height (if its horizontal) """
BORDER_SIZE = 30

""" Represents the sizes of squares where all the game objects such as holes and obstacles """
SQUARE_SIZE = 20

BALL_RADIUS = 15 
BALL_COLOR = RED

FRICTION = 0.1 
MAX_VELOCITY = 750

STEP_BY = 0.01

# Misc
MOUSE_BUTTON_ONE = 1

class Ball:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,BALL_RADIUS,BALL_RADIUS)
        # You may wonder why we represent velocity as a scalar but also have a dir vector component. it just works better this way
        self.dir = pygame.math.Vector2(0,0)
        self.velocity = 0.0 

    def draw(self,screen):
        pygame.draw.circle(screen,BALL_COLOR,(self.rect.x,self.rect.y),BALL_RADIUS)

        # border
        pygame.draw.circle(screen,BLACK,(self.rect.x,self.rect.y),BALL_RADIUS,2)

    def update(self,objects):
        # So we predict if the next position where our ball is going to be is gonna collide with something
        # We create a dummy rectangle to test our predicitions with and assign it the values our actual ball would take if we didnt check for collisions
        rect = self.rect
        rect.x += self.velocity * self.dir.x * STEP_BY 
        rect.y += self.velocity * self.dir.y * STEP_BY 

        for obj in objects:
            # Now, now, theres 4 cases.
            # 1.Ball collides a block with its top surface touching the block's bottom surface (ball makes contact with an object above it)
            # 2.Ball collides a block with its bottom surface touching the block's top surface
            # 3.Ball collides a block with its left surface touching the block's right surface
            # 4.Ball collides a block with its right surface touching the block's left surface

            # Depending on the situation, we need to change the ball's velocity accordingly.
            # Example: If the ball touches an object on its right, we change the velocity (or here, the dir)'s x component to be the opposite of that
            # that is, dir.x = -dir.x
            

            obj_rect = obj.rect.copy()
            
            if not rect.colliderect(obj_rect): continue

            dx = rect.centerx - obj_rect.centerx
            dy = rect.centery - obj_rect.centery

            overlap_x = (rect.width + obj_rect.width)/2 - abs(dx)
            overlap_y = (rect.height + obj_rect.height)/2 - abs(dy)

            if overlap_x < overlap_y:
                self.dir.x *= -1
            else:
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
         


class StaticBlock:
    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)
        
    def draw(self,screen):
        pygame.draw.rect(screen,BLOCK_COLOR,self.rect)

    def update(self):
        pass

class MovingBlock:
    def __init__(self,x,y,w,h,speed:float,checkpoints:[pygame.Vector2]):
        if len(checkpoints) == 0:
            checkpoints = [pygame.Vector2(x,y)]
        self.rect = pygame.Rect(x,y,w,h)
        self.checkpoints = checkpoints 
        self.current_checkpoint = 0
        self.speed = speed

    def draw(self,screen):
        pygame.draw.rect(screen,BLOCK_COLOR,self.rect)

    def update(self):
        to = self.checkpoints[self.current_checkpoint]
        rect_v = pygame.math.Vector2(self.rect.x,self.rect.y)

        if (rect_v - to).magnitude() < 5:
            self.current_checkpoint = (self.current_checkpoint + 1)  % len(self.checkpoints)
        dir_ = (pygame.math.Vector2(self.rect.x,self.rect.y) - self.checkpoints[self.current_checkpoint]).normalize()
        self.rect.x -= dir_.x * self.speed 
        self.rect.y -= dir_.y * self.speed

class LevelState(Enum):
    PLAYING = 1
    WON_ANIM = 2
    WON  = 3

class Level:
    def __init__(self,start,end,objs):
        self.ball_start = start
        self.ball = Ball(start[0],start[1])
        self.ball_end = end
        self.objects = objs

        self.state = LevelState.PLAYING
        # This stores the initial and final/current position of the mouse when it was first clicked at the start of every shot
        self.mouse_initial_pos = None
        self.mouse_final_pos = None

        self.num_strokes = 0
        self.start_time = time.time()

        # text stuff (make sure you call pygame.font.init() before)
        # default_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(None,40)
    
    def draw(self,screen):

        mouse_pos_initial_v = pygame.math.Vector2(self.mouse_initial_pos or (self.ball.rect.x,self.ball.rect.y))
        mouse_pos_final_v = pygame.math.Vector2(self.mouse_final_pos or (self.ball.rect.x,self.ball.rect.y))
        dir_v =  mouse_pos_initial_v - mouse_pos_final_v


        if self.mouse_initial_pos is not None and  dir_v.magnitude != 0:
            x_vector = pygame.math.Vector2(1,0)
            
            theta = dir_v.angle_to(x_vector)

            dir_ = dir_v.normalize()
            rect = self.ball.rect
            o = pygame.math.Vector2(rect.x,rect.y)
            p1_ = pygame.math.Vector2(BALL_RADIUS,0)
            p2_ = pygame.math.Vector2(-BALL_RADIUS,0)
            p3_ = pygame.math.Vector2(0,-BALL_RADIUS) 
            
            p1 = o + p1_.rotate(90-theta)
            p2 = o + p2_.rotate(90-theta)
            p3 = o + p3_.rotate(90-theta) *  max(2,dir_v.magnitude()//50) 
            pygame.draw.polygon(screen,WHITE,[p1,p2,p3])

        self.ball.draw(screen)

            
        for obj in self.objects:
            obj.draw(screen)
        pygame.draw.circle(screen,BLACK,self.ball_end,BALL_RADIUS)
        

        text_surface = self.font.render('Your score: {}'.format(self.num_strokes),True,WHITE)
        screen.blit(text_surface,(BORDER_SIZE+10,30))


    def update(self):
        end_rect = pygame.Rect(self.ball_end[0],self.ball_end[1],BALL_RADIUS,BALL_RADIUS)

        ball_rect = self.ball.rect
        if ball_rect.colliderect(end_rect):
            self.state = LevelState.WON
            
        match self.state:
            case LevelState.PLAYING:
                self.ball.update(self.objects)
                for obj in self.objects:
                    obj.update()
            case LevelState.WON:
                pass

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
                self.num_strokes += 1
                btn = event.button
                pos = event.pos
                if btn == MOUSE_BUTTON_ONE:
                    self.mouse_final_pos = pos
                self.ball.calc_force(self.mouse_initial_pos or (0,0),self.mouse_final_pos or (0,0))
                self.mouse_initial_pos = None
                self.mouse_final_pos = None
                return True
        return False




def create_borders():
    rects = [
            (0,0,SCREEN_W,BORDER_SIZE), 
            (0,SCREEN_H-BORDER_SIZE,SCREEN_W,BORDER_SIZE), 
            (0,0,BORDER_SIZE,SCREEN_H), 
            (SCREEN_W-BORDER_SIZE,0,BORDER_SIZE,SCREEN_H)    
            ]
    return [ StaticBlock(v[0],v[1],v[2],v[3]) for v in rects ]

def test_create_moving_block():
    rects = [
            (0,0), 
            (SCREEN_W-50,0), 
            (SCREEN_W-50,SCREEN_H-50), 
            (0,SCREEN_H-50)    
            ]
    return MovingBlock(0,0,50,50,10,[pygame.Vector2(x,y) for (x,y) in rects])

def draw_bg_squares(screen):
    start_x, end_x = BORDER_SIZE, SCREEN_W - BORDER_SIZE
    start_y, end_y = BORDER_SIZE, SCREEN_H - BORDER_SIZE

    count = 0 

    for y in range(start_y, end_y,SQUARE_SIZE):
        for x in range(start_x,end_x,SQUARE_SIZE):
            r = pygame.Rect(x,y,SQUARE_SIZE,SQUARE_SIZE)
            #c = LIGHT_GREEN if count % 2 == 0 else DARK_GREEN
            c = BG_COLOR 
            pygame.draw.rect(screen,c,r)
            count += 1


objs = create_borders()
MB_W = 200
objs.append(MovingBlock(50,100,MB_W,50,20,[pygame.math.Vector2(50,100),pygame.math.Vector2(SCREEN_W-50,100)]))
LEVEL_0 = Level((SCREEN_W/2,SCREEN_H/2),(SCREEN_W/2,BORDER_SIZE+BALL_RADIUS + 5),objs)


class GameState(Enum):
    MAIN_MENU=1
    LEVEL_SELECTOR=2


def main():

    screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
    clock = pygame.time.Clock()
    running = True

    current_level = LEVEL_0

    while running:
        for event in pygame.event.get():
            if current_level.handle_mouse_event(event): break
            match event.type:
                case pygame.QUIT:
                    running = False

        current_level.update()


        screen.fill(BG_COLOR)

        current_level.draw(screen)

        pygame.display.flip()

        clock.tick(60)  

    pygame.quit()

if __name__ == "__main__":
    main()
