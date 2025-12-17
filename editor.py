"""
    Level Editor for the project
"""

import math
from dataclasses import dataclass

from enum import Enum
import pygame

from constants import *

import ui_misc
import level
import block

pygame.init()
pygame.font.init()

PLAY_SCREEN_W = SCREEN_W
PLAY_SCREEN_H = SCREEN_H
SCREEN_W,SCREEN_H = 1510,720

SNAP_BY = BORDER_SIZE

MAX_W = PLAY_SCREEN_W 
MIN_W = BORDER_SIZE 
MAX_H = PLAY_SCREEN_H
MIN_H = BORDER_SIZE 

class ObjType(Enum):
    StaticBlock = 1,
    MovingBlock = 2,
    Hole        = 3,
    BallStart   = 4,

class Object:
    def __init__(self,ty:ObjType,x:float,y:float,w:float,h:float,editable:bool,checkpoints=[]):
        self.rect = pygame.Rect(x,y,w,h)
        self.type = ty
        self.editable = editable 
        self.checkpoints = checkpoints 

    def draw(self,screen):
        match self.type:
            case ObjType.StaticBlock:
                pygame.draw.rect(screen,BLOCK_COLOR,self.rect) 
            case ObjType.MovingBlock:
                pygame.draw.rect(screen,BLOCK_COLOR,self.rect) 
                if len(self.checkpoints) == 0: return 
                for cur,nex in zip(self.checkpoints,self.checkpoints[1:]):
                    pygame.draw.line(screen,BLACK,cur,nex)
                pygame.draw.line(screen,BLACK,self.checkpoints[-1],(self.rect.x,self.rect.y))
            case ObjType.Hole:
                pygame.draw.circle(screen,HOLE_COLOR,(self.rect.x+HOLE_RADIUS,self.rect.y+HOLE_RADIUS),HOLE_RADIUS)
            case ObjType.BallStart:
                pygame.draw.circle(screen,BALL_COLOR,(self.rect.x+BALL_RADIUS,self.rect.y+BALL_RADIUS),BALL_RADIUS)
        
class ToolType(Enum):
    Object = 1,
    Eraser = 2

class Tool():
    def __init__(self,ttype:ToolType,obj_type:ObjType = None):
        self.type = ttype
        self.obj_type = obj_type
        # this will be used only when it is a moving block
        self.checkpoints = []
        
        if ttype == ToolType.Object:
            assert obj_type != None, "Cannot have obj_type be None when given type is not ToolType.Object"
            match obj_type:
                case ObjType.StaticBlock | ObjType.MovingBlock:
                    dims = BORDER_SIZE,BORDER_SIZE
                case ObjType.Hole:
                    dims = HOLE_RADIUS*2,HOLE_RADIUS*2
                case ObjType.BallStart:
                    dims = BALL_RADIUS*2,BALL_RADIUS*2
        elif ttype == ToolType.Eraser:
            dims = 1,1

        self.rect = pygame.Rect(0,0,dims[0],dims[1])
        self.is_ok = False

    def update(self,event,objs):
        mouse_pos = pygame.mouse.get_pos()
        self.rect.x = math.ceil((mouse_pos[0] - self.rect.w/2)/SNAP_BY) * SNAP_BY
        self.rect.y = math.ceil((mouse_pos[1] - self.rect.h/2)/SNAP_BY) * SNAP_BY
        is_ok = True
        rect = self.rect
        if rect.x > PLAY_SCREEN_W:
            is_ok = False
        for obj in objs:
            if rect.colliderect(obj.rect):
                is_ok = False
                break
        if self.type == ToolType.Object and (self.obj_type == ObjType.Hole or self.obj_type == ObjType.BallStart):
            for obj in objs:
                if obj.type == self.obj_type:
                    is_ok = False
                    break
            
        self.is_ok = is_ok
        

    def use(self,objects):

        if self.type == ToolType.Eraser:
            self.use_eraser(objects)
            return

        if not self.is_ok: return

        if self.type == ToolType.Object and self.obj_type == ObjType.MovingBlock:
            if not pygame.key.get_pressed()[pygame.K_RETURN]:
                # if we want to add checkpoints to the current moving block
                rect = self.rect
                self.checkpoints.append(pygame.math.Vector2(rect.x,rect.y))
                return 
            else:
                if len(self.checkpoints) == 0: return
                pos = self.checkpoints[0]
                obj = Object(ObjType.MovingBlock,pos.x,pos.y,self.rect.w,self.rect.h,True,self.checkpoints)
                objects.append(obj)
                self.checkpoints = []
                return

        rect = self.rect
        obj = Object(self.obj_type,rect.x,rect.y,rect.w,rect.h,True,self.checkpoints)
        objects.append(obj)

    def use_eraser(self,objects):
        rect = self.rect
        for (i,obj) in enumerate(objects):
            if obj.rect.colliderect(rect) and obj.editable:
                objects.pop(i)
                break
    def draw_preview(self,screen,objs):
        if self.type == ToolType.Eraser:
            rect = self.rect
            for obj in objs:
                if rect.colliderect(obj.rect):
                    match obj.type:
                        case ObjType.StaticBlock | ObjType.MovingBlock:
                            pygame.draw.rect(screen,BLACK,obj.rect,7)
                        case ObjType.Hole:
                            pygame.draw.circle(screen,BLACK,(rect.x,rect.y),HOLE_RADIUS,5)
                            
                        case ObjType.BallStart:
                            pygame.draw.circle(screen,BLACK,(rect.x+BALL_RADIUS,rect.y+BALL_RADIUS),BALL_RADIUS,5)

                    return
            pygame.draw.rect(screen,BLACK,(rect.x,rect.y,SNAP_BY,SNAP_BY),5)

            return 

        match self.obj_type:
            case ObjType.StaticBlock:
               color = BLOCK_COLOR if self.is_ok else RED
               pygame.draw.rect(screen,color,self.rect)  
               pygame.draw.rect(screen,BLACK,self.rect,5)  
            case ObjType.MovingBlock:
               color = BLOCK_COLOR if self.is_ok else RED
               pygame.draw.rect(screen,color,self.rect,border_radius=10)
               pygame.draw.rect(screen,BLACK,self.rect,5,border_radius=10)  

               if len(self.checkpoints) != 0:
                    for cur,nex in zip(self.checkpoints,self.checkpoints[1:]):
                        pygame.draw.line(screen,BLACK,cur,nex)
                    pygame.draw.line(screen,BLACK,self.checkpoints[-1],(self.rect.x,self.rect.y))

            case ObjType.Hole:
               color = HOLE_COLOR if self.is_ok else RED
               pygame.draw.circle(screen,color,(self.rect.x+HOLE_RADIUS,self.rect.y+HOLE_RADIUS),HOLE_RADIUS)
            case ObjType.BallStart:
               color = BALL_COLOR if self.is_ok else RED
               pygame.draw.circle(screen,color,(self.rect.x+BALL_RADIUS,self.rect.y+BALL_RADIUS),BALL_RADIUS)

def create_borders():
    rects = [
            (0,0,PLAY_SCREEN_W+10,BORDER_SIZE), 
            (0,PLAY_SCREEN_H-BORDER_SIZE,PLAY_SCREEN_W,BORDER_SIZE), 
            (0,BORDER_SIZE,BORDER_SIZE,PLAY_SCREEN_H-BORDER_SIZE+10), 
            (PLAY_SCREEN_W-BORDER_SIZE+10,BORDER_SIZE,BORDER_SIZE,PLAY_SCREEN_H)    
            ]
    return [ Object(ObjType.StaticBlock,v[0],v[1],v[2],v[3],False) for v in rects ]

class UIButton:
    def __init__(self,rect:pygame.Rect,text:str,onclicked=None):
        self.rect = rect
        self.text = text
        self.isclicked = False
        self.onclicked = onclicked

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

    def draw(self,screen):
        hover_val = int(self.is_hovered())
        ui_misc.draw_button_scaled(screen,self.rect,self.text,hover_val)

    def update(self,event):

        self.isclicked = self.is_hovered() and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        if self.isclicked and self.onclicked: self.onclicked()
        return self.isclicked

class Editor:
    def __init__(self,screen):
        self.screen = screen
        self.objects = create_borders()
        self.tool = Tool(ToolType.Object,ObjType.StaticBlock)
        self.redo_buf = []

        tools = [ Tool(ToolType.Eraser),
                 *[Tool(ToolType.Object,o) for o in ObjType]
                 ]

        self.file_name = False
        
        buttons = []
        NUM_BTNS_IN_ROW = 2
        y = BORDER_SIZE
        BUTTON_H = 100
        def change_to_tool_0(): self.tool = tools[0]
        def change_to_tool_1(): self.tool = tools[1]
        def change_to_tool_2(): self.tool = tools[2]
        def change_to_tool_3(): self.tool = tools[3]
        def change_to_tool_4(): self.tool = tools[4]
        
        buttons.append(UIButton(pygame.Rect(PLAY_SCREEN_W+20,100,200,50),"Erase",change_to_tool_0))
        buttons.append(UIButton(pygame.Rect(PLAY_SCREEN_W+20,200,200,50),"Block",change_to_tool_1))
        buttons.append(UIButton(pygame.Rect(PLAY_SCREEN_W+20,300,200,50),"Moving Block",change_to_tool_2))
        buttons.append(UIButton(pygame.Rect(PLAY_SCREEN_W+20,400,200,50),"Hole",change_to_tool_3))
        buttons.append(UIButton(pygame.Rect(PLAY_SCREEN_W+20,500,200,50),"Ball",change_to_tool_4))
        
        self.buttons = buttons 

    def draw(self):
        for obj in self.objects:
            obj.draw(self.screen)
        self.tool.draw_preview(self.screen,self.objects)
        for btn in self.buttons:
            btn.draw(self.screen)

    def update(self):
        self.tool.update(None,self.objects)

    def save(self):
        if not self.file_name: return self.save_as()
        import json
        level = self.into_level()
        with open(self.file_name,'w') as f:
            json.dump(level.to_dict(),f)
        return True

    def save_as(self):

        level = self.into_level()
        if not level: return False

        import filedialpy
        import json

        self.file_name =  filedialpy.saveFile()
        if not self.file_name: return False
        with open(self.file_name,'w') as f:
            json.dump(level.to_dict(),f)
        return True

    def handle_input(self,event)-> bool:
        return self.process_event(event)

    def process_event(self,event) -> bool:
        keys = pygame.key.get_pressed()

        for btn in self.buttons: 
            if btn.update(event): return True 
        if keys[pygame.K_LCTRL]:
            if keys[pygame.K_z]:
                self.undo()
                return True
            if keys[pygame.K_y]:
                self.redo()
                return  True

        if keys[pygame.K_LCTRL] and keys[pygame.K_s] and keys[pygame.K_LSHIFT]:
            return self.save_as()
 
        if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
            return self.save()
           
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.tool = Tool(ToolType.Object,ObjType.StaticBlock)
                return True
            if event.key == pygame.K_2:
                self.tool = Tool(ToolType.Object,ObjType.MovingBlock)
                return True
            if event.key == pygame.K_3:
                self.tool = Tool(ToolType.Object,ObjType.BallStart)
                return True
            if event.key == pygame.K_4:
                self.tool = Tool(ToolType.Object,ObjType.Hole)
                return True
            if event.key == pygame.K_5:
                self.tool = Tool(ToolType.Eraser)
                return True

        if event.type == pygame.MOUSEBUTTONDOWN or pygame.mouse.get_pressed()[0] or keys[pygame.K_RETURN]:
            self.redo_buf = []
            self.tool.use(self.objects)
            return True
        
        if keys[pygame.K_w] or keys[pygame.K_h]:
            if self.tool.type == ToolType.Eraser: return False
            if keys[pygame.K_w]:
                self.tool.rect.w += BORDER_SIZE  * (-1 if keys[pygame.K_LSHIFT] else 1)
                if self.tool.rect.w > MAX_W:
                    self.tool.rect.w = MAX_W
                if self.tool.rect.w < MIN_W:
                    self.tool.rect.w = MIN_W

            if keys[pygame.K_h]:
                self.tool.rect.h += BORDER_SIZE  * (-1 if keys[pygame.K_LSHIFT] else 1)
                if self.tool.rect.h > MAX_H:
                    self.tool.rect.h = MAX_H
                if self.tool.rect.h < MIN_H:
                    self.tool.rect.h = MIN_H
            return True
        return False

    def into_level(self) -> level.Level:
        if not self.validate_level(): return None
        objs = []
        ball_start = ()
        ball_end = ()
        for obj in self.objects:
            if obj.type == ObjType.Hole:
                ball_end = obj.rect.x+HOLE_RADIUS,obj.rect.y+HOLE_RADIUS
                continue
            if obj.type == ObjType.BallStart:
                ball_start = obj.rect.x+BALL_RADIUS,obj.rect.y+BALL_RADIUS
                continue
            if obj.type == ObjType.StaticBlock:
                rect = obj.rect
                b = block.StaticBlock(rect.x,rect.y,rect.w,rect.h)
            if obj.type == ObjType.MovingBlock:
                rect = obj.rect
                b = block.MovingBlock(rect.x,rect.y,rect.w,rect.h,2,obj.checkpoints)
            objs.append(block.Block(None,b))
        return level.Level(None,ball_start,ball_end,objs) 

    def validate_level(self) -> bool:
        valid_start,valid_end = False,False
        for v in self.objects:
            if v.type == ObjType.Hole:
                if valid_end: valid_end = False; break 
                valid_end = True
            if v.type == ObjType.BallStart:
                if valid_start: valid_start = False; break 
                valid_start = True
        return valid_start and valid_end

    def undo(self):
        if not self.objects[-1].editable: return 
        self.redo_buf.append(self.objects.pop())

    def redo(self):
        if len(self.redo_buf) < 1: return
        self.objects.append(self.redo_buf.pop())


def main():
    screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
    clock = pygame.time.Clock()
    running = True
    editor = Editor(screen)
    while running:
        time_delta = clock.tick(FPS)/1000
        for event in pygame.event.get():
            if editor.process_event(event): break
            match event.type:
                case pygame.QUIT:
                    running = False

        editor.update()
        screen.fill(BG_COLOR)
        editor.draw()
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
