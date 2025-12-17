import pygame
from constants import *
from level import Level
from ui_misc import *
from main import SCREEN,CLOCK,LEVEL_0

from math import sin
from enum import Enum

class MenuState(Enum):
    Intro = 1,
    Main = 2,
    Levels = 3,
    Settings = 4,
    Editor = 5

class Menu:
    def __init__(self,onplaybuttonclicked,oneditorbuttonclicked):
        self.state = MenuState.Intro
        self.selected_level = SelectedLevel(SelectedLevelType.Premade,0)
        self.settings = {"music": True, "sfx": True}
        self.ui_drawn = None

        self.hover_state = {"play": 0.0, "editor": 0.0, "settings": 0.0}
        self.settings_anim = {"music": 0.0, "sfx": 0.0}

        self.intro_start_time = pygame.time.get_ticks() / 1000.0
        self.onplaybuttonclicked = onplaybuttonclicked
        self.oneditorbuttonclicked = oneditorbuttonclicked

    def draw(self):

        now = pygame.time.get_ticks() / 1000.0
        intro_progress = min(1.0, max(0.0, (now - self.intro_start_time) / INTRO_DURATION))
        dt = CLOCK.get_time() / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        update_hover_states(mouse_pos, dt,self.hover_state,self.settings,self.settings_anim)

        match self.state:
            case MenuState.Intro:
                ui_drawn = draw_main_menu_with_intro(mouse_pos, intro_progress,self.hover_state)
                if intro_progress >= 1.0:
                    self.state = MenuState.Main 
            case MenuState.Main:
                ui_drawn = draw_main_menu_normal(mouse_pos,self.hover_state)
            case MenuState.Settings:
                ui_drawn = draw_settings_menu(mouse_pos,self.settings_anim,self.settings)
            case MenuState.Levels:
                ui_drawn = draw_level_selector(mouse_pos,self.hover_state)
            case _:
                ui_drawn = draw_main_menu_normal(mouse_pos,self.hover_state)
        self.ui_drawn = ui_drawn

    def handle_input(self,event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == MenuState.Main:
                    running = False
                else:
                    self.state = MenuState.Main 
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                # MAIN screen clicks (use drawn rects if available)
                if self.state in (MenuState.Intro,MenuState.Main):
                    play_r = get_inflated_drawn(self.ui_drawn, "play")
                    editor_r = get_inflated_drawn(self.ui_drawn, "editor")
                    settings_r = get_inflated_drawn(self.ui_drawn, "settings")
                    if play_r.collidepoint(pos):
                        self.state = MenuState.Levels
                        return True
                    elif editor_r.collidepoint(pos):
                        if self.oneditorbuttonclicked:
                            self.oneditorbuttonclicked()
                        #self.state = MenuState.Levels
                        return True
                    elif settings_r.collidepoint(pos):
                        self.state = MenuState.Settings
                        return True

                elif self.state == MenuState.Settings:
                    toggles = self.ui_drawn["toggles"]
                    # Toggle music if clicked on its box or pill
                    music_box = toggles["music"]["box"]
                    music_pill = toggles["music"]["pill"]
                    if music_box.collidepoint(pos) or music_pill.collidepoint(pos):
                        self.settings["music"] = not self.settings.get("music", True)
                        return True
                    # Toggle SFX similarly
                    sfx_box = toggles["sfx"]["box"]
                    sfx_pill = toggles["sfx"]["pill"]
                    if sfx_box.collidepoint(pos) or sfx_pill.collidepoint(pos):
                        self.settings["sfx"] = not self.settings.get("sfx", True)
                        return True
                    # Back
                    if self.ui_drawn["back"].collidepoint(pos):
                        print('here')
                        self.state = MenuState.Main 
                        return True
                                                
                elif self.state == MenuState.Levels:
                    levels = self.ui_drawn["levels"]
                    for lvl, r in levels.items():
                        if r.collidepoint(pos):
                            self.selected_level = SelectedLevel(SelectedLevelType.Premade,lvl) 
                            
                            if self.onplaybuttonclicked: self.onplaybuttonclicked()

                            return True
                    if self.ui_drawn["custom"].collidepoint(pos):
                        import filedialpy
                        file = filedialpy.openFile()
                        if not file: return True
                        self.selected_level = SelectedLevel(SelectedLevelType.Custom,file)

                        if self.onplaybuttonclicked: self.onplaybuttonclicked()

                    if self.ui_drawn["back"].collidepoint(pos):
                        print('maybe here')
                        self.state = MenuState.Main
                        return True
        return False
    def update(self):
        # show selected level hint on main
        if self.state == MenuState.Main and self.selected_level:
            txt = SMALL_FONT.render(f"Selected Level: {self.selected_level}", True, ACCENT)
            SCREEN.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SETTINGS_Y + 90))


# Title with layered shadow + cyan main color
def draw_title(surface, y_offset=0, color=(100,255,255)):
    title_text = "SHOOT YOUR SHOT"
    title_main = TITLE_FONT.render(title_text, True, color)
    shadow3 = TITLE_FONT.render(title_text, True, (60,60,60))
    shadow2 = TITLE_FONT.render(title_text, True, (30,30,30))
    shadow1 = TITLE_FONT.render(title_text, True, (0,0,0))
    surface.blit(shadow3, shadow3.get_rect(center=(SCREEN_W//2 + 8, 110 + 8 + y_offset)))
    surface.blit(shadow2, shadow2.get_rect(center=(SCREEN_W//2 + 5, 110 + 5 + y_offset)))
    surface.blit(shadow1, shadow1.get_rect(center=(SCREEN_W//2 + 3, 110 + 3 + y_offset)))
    surface.blit(title_main, title_main.get_rect(center=(SCREEN_W//2, 110 + y_offset)))

# Draw main menu during intro (returns drawn rects)
def draw_main_menu_with_intro(mouse_pos, intro_t,hover_state):
    zoom = 1.05 + 0.08 * sin(pygame.time.get_ticks() / 1900)

    blit_bg_with_zoom(SCREEN, BG_IMG, zoom)
    draw_geometric_overlay(SCREEN)

    # title slide
    start_y, end_y = -120, 0
    t_title = min(max((intro_t * 1.05), 0.0), 1.0)
    title_ease = 1 - (1 - t_title) ** 9
    y_offset = int(start_y * (1 - title_ease) + end_y * title_ease)
    draw_title(SCREEN, y_offset=y_offset)

    bases = [
        pygame.Rect(BUTTON_X, PLAY_Y, BUTTON_W, BUTTON_H),
        pygame.Rect(BUTTON_X, LEVEL_Y, BUTTON_W, BUTTON_H),
        pygame.Rect(BUTTON_X, SETTINGS_Y, BUTTON_W, BUTTON_H)
    ]
    labels = ["PLAY", "EDITOR", "SETTINGS"]
    drawn = {}
    for i, base in enumerate(bases):
        s_norm = min(1.0, max(0.0, BUTTON_STAGGER[i] / INTRO_DURATION))
        p = 0.0 if intro_t <= s_norm else min(1.0, (intro_t - s_norm) / (1.0 - s_norm))
        p_ease = 1 - (1 - p) ** 3
        scale_override = 0.5 + 0.5 * p_ease
        key = ("play","editor","settings")[i]
        rect_drawn = draw_button_scaled(SCREEN, base, labels[i], hover_state[key], scale_override=scale_override)
        drawn[key] = rect_drawn

    hint = SMALL_FONT.render("Press ESC to go back / quit", True, ACCENT)
    SCREEN.blit(hint, (12, SCREEN_H - 28))
    return drawn

# Draw normal main menu (post-intro)
def draw_main_menu_normal(mouse_pos,hover_state):
    blit_bg_with_zoom(SCREEN, BG_IMG, 1.06)
    draw_geometric_overlay(SCREEN)
    draw_title(SCREEN)

    base_play = pygame.Rect(BUTTON_X, PLAY_Y, BUTTON_W, BUTTON_H)
    base_editor = pygame.Rect(BUTTON_X, LEVEL_Y, BUTTON_W, BUTTON_H)
    base_settings = pygame.Rect(BUTTON_X, SETTINGS_Y, BUTTON_W, BUTTON_H)

    play_drawn = draw_button_scaled(SCREEN, base_play, "PLAY", hover_state["play"])
    editor_drawn = draw_button_scaled(SCREEN, base_editor, "EDITOR", hover_state["editor"])
    settings_drawn = draw_button_scaled(SCREEN, base_settings, "SETTINGS", hover_state["settings"])
    hint = SMALL_FONT.render("Press ESC to go back / quit", True, ACCENT)
    SCREEN.blit(hint, (12, SCREEN_H - 28))
    return {"play": play_drawn, "editor": editor_drawn, "settings": settings_drawn}

# Settings menu: boxed rows, icons, pill toggles (music & sfx)
def draw_settings_menu(mouse_pos,settings_anim,settings):
    blit_bg_with_zoom(SCREEN, BG_IMG, 1.06)
    draw_geometric_overlay(SCREEN)
    title = TITLE_FONT.render("SETTINGS", True, ACCENT)
    SCREEN.blit(title, title.get_rect(center=(SCREEN_W//2, 80)))

    rects = {}
    box_w, box_h = 520, 72
    left_x = SCREEN_W // 2 - box_w // 2
    start_y = 200; gap = 24

    for i, key in enumerate(["music","sfx"]):
        y = start_y + i * (box_h + gap)
        box_rect = pygame.Rect(left_x, y, box_w, box_h)

        anim_val = settings_anim[key]
        pulse = 0.7 + 0.3 * sin(pygame.time.get_ticks() / 200.0)
        glow_alpha = int(110 * anim_val * (0.65 + 0.35 * pulse))
        if glow_alpha > 0:
            glow_surf = pygame.Surface((box_rect.w+20, box_rect.h+20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (160,255,180,glow_alpha), glow_surf.get_rect(), border_radius=16)
            SCREEN.blit(glow_surf, (box_rect.x-10, box_rect.y-10), special_flags=pygame.BLEND_PREMULTIPLIED)

        bg_color = (
            int(BOX[0] + (HOVER[0]-BOX[0]) * anim_val*0.6),
            int(BOX[1] + (HOVER[1]-BOX[1]) * anim_val*0.6),
            int(BOX[2] + (HOVER[2]-BOX[2]) * anim_val*0.6),
        )
        pygame.draw.rect(SCREEN, bg_color, box_rect, border_radius=14)
        pygame.draw.rect(SCREEN, BLACK, box_rect, width=2, border_radius=14)

        # icon area
        icon_rect = pygame.Rect(box_rect.x+16, box_rect.centery-22, 44, 44)
        pygame.draw.rect(SCREEN, (30,30,30), icon_rect, border_radius=10)
        pygame.draw.rect(SCREEN, ACCENT, icon_rect, 1, border_radius=10)
        icon_img = MUSIC_ICON if key=="music" else SFX_ICON
        if icon_img:
            iw, ih = icon_img.get_size()
            pos = (icon_rect.centerx - iw//2, icon_rect.centery - ih//2)
            SCREEN.blit(icon_img, pos)
        else:
            # fallback simple icons
            if key=="music":
                cx, cy = icon_rect.center
                tri = [(icon_rect.left+8, cy-10),(icon_rect.left+8, cy+10),(icon_rect.left+20, cy)]
                pygame.draw.polygon(SCREEN, ACCENT, tri)
                pygame.draw.rect(SCREEN, ACCENT, (icon_rect.left+20, cy-8, 6, 16))
            else:
                cx, cy = icon_rect.center
                pygame.draw.line(SCREEN, ACCENT, (icon_rect.left+12, cy-8),(icon_rect.left+12, cy+8),2)
                pygame.draw.arc(SCREEN, ACCENT, (icon_rect.left+14, cy-12, 18, 24), -1.0, 1.0, 2)

        # label
        label = SETTINGS_FONT.render(key.upper(), True, ACCENT)
        SCREEN.blit(label, (icon_rect.right + 14, box_rect.centery - label.get_height()//2))

        # pill toggle on right (same for music & sfx)
        pill_w, pill_h = 110, 40
        pill_rect = pygame.Rect(box_rect.right - 16 - pill_w, box_rect.centery - pill_h//2, pill_w, pill_h)
        on = bool(settings.get(key, False))
        pygame.draw.rect(SCREEN, (80,220,120) if on else (80,80,80), pill_rect, border_radius=18)
        pygame.draw.rect(SCREEN, ACCENT, pill_rect, width=2, border_radius=18)
        knob_x = pill_rect.left + (pill_rect.w - 18) if on else pill_rect.left + 18
        bob = int(4 * anim_val * sin(pygame.time.get_ticks() / 140.0))
        knob_center = (knob_x, pill_rect.centery + bob)
        pygame.draw.circle(SCREEN, BLACK, knob_center, 12)
        pygame.draw.circle(SCREEN, ACCENT, (knob_center[0], knob_center[1]), 8)

        # store rects for interaction
        rects[key] = {"box": box_rect, "icon": icon_rect, "pill": pill_rect}

    # back button
    back_rect = pygame.Rect(SCREEN_W//2 - 80, SCREEN_H - 100, 160, 50)
    draw_button_scaled(SCREEN, back_rect, "BACK", 0.0)
    rects["back"] = back_rect
    return {"toggles": rects, "back": back_rect}


# Level selector (1..10)
def draw_level_selector(mouse_pos,hover_state):
    blit_bg_with_zoom(SCREEN, BG_IMG, 1.06)
    draw_geometric_overlay(SCREEN)
    title = TITLE_FONT.render("SELECT LEVEL", True, ACCENT)
    SCREEN.blit(title, title.get_rect(center=(SCREEN_W//2, 70)))

    level_rects = {}
    cols = 5
    spacing_x = 20; spacing_y = 30
    card_w = 120; card_h = 80
    start_x = (SCREEN_W - (cols*card_w + (cols-1)*spacing_x)) // 2
    start_y = 160

    num_levels = len(load_levels_dict())

    for i in range(min(10,num_levels)):
        col, row = i % cols, i // cols
        x = start_x + col * (card_w + spacing_x)
        y = start_y + row * (card_h + spacing_y)
        rect = pygame.Rect(x,y,card_w,card_h)
        hover = rect.collidepoint(mouse_pos)
        base_color = (28,110,52) if not hover else (68,150,82)
        pygame.draw.rect(SCREEN, base_color, rect, border_radius=12)
        pygame.draw.rect(SCREEN, ACCENT, rect, 2, border_radius=12)
        num = BUTTON_FONT.render(str(i+1), True, ACCENT)
        SCREEN.blit(num, num.get_rect(center=rect.center))
        level_rects[i+1] = rect

    padding = 40
    back_btn_size = (160,50)
    load_custom_btn_size = (160,50)
    back_rect = pygame.Rect(SCREEN_W//2-padding-back_btn_size[0],SCREEN_H-100,back_btn_size[0],back_btn_size[1])

    load_custom_rect = pygame.Rect(SCREEN_W//2-padding+load_custom_btn_size[0]/2,SCREEN_H-100,load_custom_btn_size[0],load_custom_btn_size[1])
    draw_button_scaled(SCREEN, back_rect, "BACK", 0.0)
    draw_button_scaled(SCREEN,load_custom_rect , "CUSTOM", 0.0)
    return {"levels": level_rects, "back": back_rect,"custom":load_custom_rect}

# update hover states & settings anims (based on base rect positions)
def update_hover_states(mouse_pos, dt,hover_state,settings,settings_anim):
    base_play = pygame.Rect(BUTTON_X, PLAY_Y, BUTTON_W, BUTTON_H)
    base_level = pygame.Rect(BUTTON_X, LEVEL_Y, BUTTON_W, BUTTON_H)
    base_settings = pygame.Rect(BUTTON_X, SETTINGS_Y, BUTTON_W, BUTTON_H)
    targets = {
        "play": 1.0 if base_play.collidepoint(mouse_pos) else 0.0,
        "editor": 1.0 if base_level.collidepoint(mouse_pos) else 0.0,
        "settings": 1.0 if base_settings.collidepoint(mouse_pos) else 0.0
    }
    for k in hover_state.keys():
        cur = hover_state[k]; tgt = targets[k]
        hover_state[k] = cur + (tgt - cur) * min(1.0, HOVER_SPEED * dt)

    # settings anim targets (hovered or ON)
    box_w, box_h = 520, 72; left_x = SCREEN_W//2 - box_w//2; start_y = 200; gap = 24
    for i, key in enumerate(["music","sfx"]):
        y = start_y + i * (box_h + gap)
        box_rect = pygame.Rect(left_x, y, box_w, box_h)
        hovered = box_rect.collidepoint(mouse_pos)
        target = 1.0 if (hovered or settings.get(key, False)) else 0.0
        cur = settings_anim[key]
        settings_anim[key] = cur + (target - cur) * min(1.0, ANIM_SPEED * dt)

class SelectedLevelType(Enum):
    Premade=1,
    Custom=2

class SelectedLevel:
    def __init__(self,ty:SelectedLevelType,val):
        self.val = val
        self.type = ty
    def to_level(self):
        match self.type:
            case SelectedLevelType.Premade:
                idx = self.val-1 if self.val > 0  else 0 
                level_dict = LEVELS_DICTS[idx] 
                level = LEVEL_0
                level.from_dict(level_dict)
                level.level_num = self.val
                level.is_premade = True
                return level
            case SelectedLevelType.Custom:
                import json
                with open(self.val,'r') as f:
                    contents = f.read()
                    contents = json.loads(contents)
                    level = LEVEL_0
                    level.from_dict(contents)
                    return level
 
    def next_level(self):
        return SelectedLevel(SelectedLevelType.Premade,self.val+1)

    def is_premade(self):
        return self.type == SelectedLevelType.Premade
