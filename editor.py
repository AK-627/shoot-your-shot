"""
    Level Editor for the project
"""

import math
from dataclasses import dataclass

from enum import Enum
import pygame
import pygame_gui

from constants import *
import level
import block

pygame.init()
pygame.font.init()

PLAY_SCREEN_W = SCREEN_W
PLAY_SCREEN_H = SCREEN_H
SCREEN_W,SCREEN_H = 1500,720

SNAP_BY = BORDER_SIZE

class ObjType(Enum):
    StaticBlock = 1,
    MovingBlock = 2,
    Hole        = 3,
    BallStart   = 4,

class Object:
    def __init__(self,ty:ObjType,x:float,y:float,w:float,h:float,editable:bool):
        self.rect = pygame.Rect(x,y,w,h)
        self.type = ty
        self.editable = editable 

    def draw(self,screen):
        match self.type:
            case ObjType.StaticBlock:
                pygame.draw.rect(screen,BLOCK_COLOR,self.rect) 
            case ObjType.MovingBlock:
                pygame.draw.rect(screen,BLOCK_COLOR,self.rect) 
            case ObjType.Hole:
                pygame.draw.circle(screen,HOLE_COLOR,(self.rect.x+HOLE_RADIUS,self.rect.y+HOLE_RADIUS),HOLE_RADIUS)
            case ObjType.BallStart:
                pygame.draw.circle(screen,BALL_COLOR,(self.rect.x+BALL_RADIUS,self.rect.y+BALL_RADIUS),BALL_RADIUS)

class ToolType(Enum):
    Object = 1,
    Eraser = 2

class Tool():
    def __init__(self,ttype:ToolType,extra:ObjType = None):
        self.type = ttype
        self.extra = extra
        if ttype == ToolType.Object:
            assert extra != None, "Cannot have extra be None when given type is not ToolType.Object"
            match extra:
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
        if self.type == ToolType.Object and (self.extra == ObjType.Hole or self.extra == ObjType.BallStart):
            for obj in objs:
                if obj.type == self.extra:
                    is_ok = False
                    break
            
        self.is_ok = is_ok
        

    def use(self,objects):
        if self.type == ToolType.Eraser:
            self.use_eraser(objects)
            return

        if not self.is_ok: return
        rect = self.rect
        obj = Object(self.extra,rect.x,rect.y,rect.w,rect.h,True)
        objects.append(obj)

    def use_eraser(self,objects):
        rect = self.rect
        for (i,obj) in enumerate(objects):
            if obj.rect.colliderect(rect):
                objects.pop(i)
                break
    def draw_preview(self,screen,objs):
        if self.type == ToolType.Eraser:
            rect = self.rect
            for obj in objs:
                if rect.colliderect(obj.rect):
                    match obj.type:
                        case ObjType.StaticBlock | ObjType.MovingBlock:
                            nrect = self.rect.copy()
                            nrect.w = BORDER_SIZE
                            nrect.h = BORDER_SIZE
                            pygame.draw.rect(screen,BLACK,nrect,7)
                        case ObjType.Hole:
                            pygame.draw.circle(screen,BLACK,(rect.x+HOLE_RADIUS,rect.y+HOLE_RADIUS),HOLE_RADIUS,5)
                            
                        case ObjType.BallStart:
                            pygame.draw.circle(screen,BLACK,(rect.x+BALL_RADIUS,rect.y+BALL_RADIUS),BALL_RADIUS,5)

                    return
            pygame.draw.rect(screen,BLACK,(rect.x,rect.y,SNAP_BY,SNAP_BY),5)

            return 

        match self.extra:
            case ObjType.StaticBlock:
               color = BLOCK_COLOR if self.is_ok else RED
               pygame.draw.rect(screen,color,self.rect)  
               pygame.draw.rect(screen,BLACK,self.rect,5)  
            case ObjType.MovingBlock:
               color = BLOCK_COLOR if self.is_ok else RED
               pygame.draw.rect(screen,color,self.rect,border_radius=10)
               pygame.draw.rect(screen,BLACK,self.rect,5,border_radius=10)  
            case ObjType.Hole:
               color = HOLE_COLOR if self.is_ok else RED
               pygame.draw.circle(screen,color,(self.rect.x+HOLE_RADIUS,self.rect.y+HOLE_RADIUS),HOLE_RADIUS)
            case ObjType.BallStart:
               color = BALL_COLOR if self.is_ok else RED
               pygame.draw.circle(screen,color,(self.rect.x+BALL_RADIUS,self.rect.y+BALL_RADIUS),BALL_RADIUS)

def create_borders():
    rects = [
            (0,0,PLAY_SCREEN_W,BORDER_SIZE), 
            (0,PLAY_SCREEN_H-BORDER_SIZE,PLAY_SCREEN_W,BORDER_SIZE), 
            (0,BORDER_SIZE,BORDER_SIZE,PLAY_SCREEN_H-BORDER_SIZE), 
            (PLAY_SCREEN_W-BORDER_SIZE,BORDER_SIZE,BORDER_SIZE,PLAY_SCREEN_H)    
            ]
    return [ Object(ObjType.StaticBlock,v[0],v[1],v[2],v[3],False) for v in rects ]

class Editor:
    def __init__(self):
        self.objects = create_borders()
        self.tool = Tool(ToolType.Object,ObjType.StaticBlock)

        self.file_name = False

    def draw(self,screen):
        for obj in self.objects:
            obj.draw(screen)
        self.tool.draw_preview(screen,self.objects)

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
        import filedialpy
        self.file_name =  filedialpy.saveFile()
        if not self.file_name: return False
        import json
        level = self.into_level()
        with open(self.file_name,'w') as f:
            json.dump(level.to_dict(),f)
        return True

    def process_event(self,event) -> bool:
        keys = pygame.key.get_pressed()
        
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
        if event.type == pygame.MOUSEBUTTONDOWN or pygame.mouse.get_pressed()[0]:
            self.tool.use(self.objects)

        return False


    def into_level(self) -> level.Level:
        if not self.validate_level(): return None
        objs = []
        ball_start = ()
        ball_end = ()
        for obj in self.objects:
            if obj.type == ObjType.Hole:
                ball_end = obj.rect.x,obj.rect.y
                continue
            if obj.type == ObjType.BallStart:
                ball_start = obj.rect.x,obj.rect.y
                continue
            if obj.type == ObjType.StaticBlock:
                rect = obj.rect
                b = block.StaticBlock(rect.x,rect.y,rect.w,rect.h)
            if obj.type == ObjType.MovingBlock:
                rect = obj.rect
                b = block.MovingBlock(rect.x,rect.y,rect.w,rect.h,None,[])

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


def main():
    screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
    clock = pygame.time.Clock()
    running = True
    editor = Editor()
    while running:
        time_delta = clock.tick(FPS)/1000
        for event in pygame.event.get():
            if editor.process_event(event): break
            match event.type:
                case pygame.QUIT:
                    level = editor.into_level()
                    if level:
                        print(level.to_dict()) 
                    else: 
                        print("Invalid level")
                    running = False

        editor.update()
        screen.fill(BG_COLOR)
        editor.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
