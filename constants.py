# Screen consts
SCREEN_W, SCREEN_H = 1320,720
FPS = 60 

# Color consts
BLACK = 0,0,0
WHITE = 255,255,255
MAROON = 128, 0, 0
RED = 255,0,0
GREEN = 0,255,0
DARK_GREEN =  0, 100,0 
LIGHT_GREEN = 90,180,80 
GREEN_BG = LIGHT_GREEN 
ACCENT = 255, 255, 255
HOVER = 200, 255, 200
BOX = 20, 90, 40

BG_COLOR =    60,200,120 
BLOCK_COLOR = DARK_GREEN

# Game object consts

""" Represents the borders width (if its verticle) or its height (if its horizontal) """
BORDER_SIZE = 30

""" Represents the sizes of squares where all the game objects such as holes and obstacles """
SQUARE_SIZE = 20

BALL_RADIUS = 15 
HOLE_RADIUS = 30
BALL_COLOR = WHITE 
HOLE_COLOR = BLACK

FRICTION = 0.01
MAX_VELOCITY = 500 

STEP_BY = 1/FPS


# UI Constants
BACKGROUND_IMAGE = './assets/iamge.png'
MUSIC_ICON_PATH = './assets/icon_music.png'
SFX_ICON_PATH = './assets/icon_sfx.png'
LEVELS_PATH = './levels/'
CUSTOM_FONT_FILENAMES = ["game_font.ttf", "pixel_font.ttf", "arcade_font.ttf"]
INTRO_DURATION = 3
BUTTON_STAGGER = [1,1.5, 2]
CLICK_PAD = 8
ICON_SIZE = (40, 40)   # requested tiny icon size
MAX_ZOOM = 1.06  # or 1.10 if you want more zoom
MIN_ZOOM = 1.00
current_zoom = MIN_ZOOM

# UI geometry
BUTTON_W, BUTTON_H = 380, 84
BUTTON_X = (SCREEN_W - BUTTON_W) // 2
PLAY_Y = 220
LEVEL_Y = PLAY_Y + BUTTON_H + 18
SETTINGS_Y = LEVEL_Y + BUTTON_H + 18

# Animation
ANIM_SPEED = 4.5

# Misc
MOUSE_BUTTON_ONE = 1

HOVER_SPEED = 8.0


def load_levels_dict():
    import os
    import json
    if not os.path.exists(LEVELS_PATH): return []
    levels = []
    files = os.listdir(LEVELS_PATH)
    for file_name in sorted(files):
        with open(LEVELS_PATH+'/'+file_name,'r') as file:
            conts = file.read()
            contents = json.loads(conts)
            levels.append(contents)

    return levels
    
LEVELS_DICTS = load_levels_dict()


# Editor UI Constants
BUTTON_NORMAL = DARK_GREEN
BUTTON_SELECTED = GREEN
BUTTON_HOVERED = LIGHT_GREEN
