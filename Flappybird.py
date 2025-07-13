from pygame import *
import random

# --- Ініціалізація ---
font.init()
mixer.init()
win_width = 800
win_height = 600
display.set_caption("Swimming Axolotl")
window = display.set_mode((win_width, win_height))
clock = time.Clock()

# --- Зображення ---
img_back = "1752269209344.png"
img_hero = "IMG_20250705_224209.png"
img_pipe_bottom = "BackgroundEraser_20250706_101302857.png"
img_start_bg = "Screenshot_20250711-234839_1.png"
img_level_bg = "1752262627624.png"
img_lock = "BackgroundEraser_20250712_002801347.png"
img_settings_icon = "BackgroundEraser_20250712_064457507.png"
img_back_icon = "BackgroundEraser_20250712_054724276.png"

background = transform.scale(image.load(img_back), (win_width, win_height))
hero_img = image.load(img_hero)
pipe_bottom_img = image.load(img_pipe_bottom)
start_background = transform.scale(image.load(img_start_bg), (win_width, win_height))
level_background = transform.scale(image.load(img_level_bg), (win_width, win_height))
lock_img = transform.scale(image.load(img_lock), (40, 40))
settings_icon = transform.scale(image.load(img_settings_icon), (40, 40))
back_icon = transform.scale(image.load(img_back_icon), (40, 40))

font_score = font.SysFont("Lato", 36)
font_start = font.SysFont("Lato", 72)
#kdferfhethrhgrhythytht
language = "EN"
#kdferfhethrhgrhythytht
# --- Класи ---
class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__()
        self.image = transform.scale(img, (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        self.rect.x -= self.speed

class Player(GameSprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__(img, x, y, w, h, speed)
        self.y_speed = 0
        self.collision_rect = self.rect.inflate(-100, -100)

    def update(self):
        self.y_speed += 0.5
        self.rect.y += self.y_speed
        self.collision_rect.center = self.rect.center

    def jump(self):
        self.y_speed = -10

class SinglePipe(GameSprite):
    def __init__(self, x, speed):
        self.width = 330
        height = win_height
        y = 0
        img = transform.scale(pipe_bottom_img, (self.width, height))
        super().__init__(img, x, y, self.width, height, speed)

# --- Налаштування ---
PIPE_SPEED = 4
PIPE_DELAY = 100
pipe_timer = 0

PLAYER_WIDTH = 140
PLAYER_HEIGHT = 170
player = Player(hero_img, 100, 250, PLAYER_WIDTH, PLAYER_HEIGHT, 0)

pipes = []
score = 0
game = True
game_over = False

game_state = "start"
unlocked_levels = [1]
selected_level = None

# --- Кнопки рівнів ---
level_buttons = []
button_size = 80
gap = 20
start_x = win_width//2 - (button_size*4 + gap*3)//2
start_y = win_height//2 - button_size//2
for i in range(4):
    rect = Rect(start_x + i*(button_size + gap), start_y, button_size, button_size)
    level_buttons.append(rect)

def reset_game_for_level(level):
    global pipes, score, game, game_over, pipe_timer, player
    player.rect.y = 250
    player.y_speed = 0
    pipes.clear()
    score = 0
    game = True
    game_over = False
    pipe_timer = 0
    global PIPE_SPEED, PIPE_DELAY
    PIPE_SPEED = 4 + level
    PIPE_DELAY = max(60, 100 - level*10)

def toggle_language():
    global language
    language = "UA" if language == "EN" else "UK"

def show_start_screen():
    window.blit(start_background, (0, 0))
    title_text = font_start.render("Swimming Axolotl", True, (255, 255, 255))
    window.blit(title_text, (win_width//2 - title_text.get_width()//2, win_height//3))

    play_btn = Rect(win_width//2 - 100, win_height//2 - 40, 200, 50)
    draw.rect(window, (0, 180, 100), play_btn)
    play_text = font_score.render("Play", True, (255, 255, 255))
    window.blit(play_text, (play_btn.x + play_btn.w//2 - play_text.get_width()//2,
                            play_btn.y + play_btn.h//2 - play_text.get_height()//2))

    settings_btn = Rect(win_width - 60, 20, 40, 40)
    window.blit(settings_icon, (settings_btn.x, settings_btn.y))

    return play_btn, settings_btn

def draw_level_select():
    window.blit(level_background, (0, 0))
    title = font_start.render("Select Level", True, (255, 255, 255))
    window.blit(title, (win_width//2 - title.get_width()//2, 100))

    for i, rect in enumerate(level_buttons, start=1):
        if i in unlocked_levels:
            draw.rect(window, (0, 200, 0), rect)
            num_text = font_score.render(str(i), True, (255, 255, 255))
            window.blit(num_text, (rect.x + rect.w//2 - num_text.get_width()//2,
                                   rect.y + rect.h//2 - num_text.get_height()//2))
        else:
            draw.rect(window, (100, 100, 100), rect)
            window.blit(lock_img, (rect.x + rect.w//2 - lock_img.get_width()//2,
                                   rect.y + rect.h//2 - lock_img.get_height()//2))

    # кнопка назад
    back_btn = Rect(20, 20, 40, 40)
    window.blit(back_icon, (back_btn.x, back_btn.y))
    return back_btn

def show_game_over():
    text = font_score.render("Game Over! Press R to Restart", True, (255, 0, 0))
    window.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2))

def show_settings_screen():
    window.fill((30, 30, 30))
    title = font_start.render("Settings", True, (255, 255, 255))
    window.blit(title, (win_width//2 - title.get_width()//2, 50))

    lang_text = font_score.render(f"Language: {language}", True, (255, 255, 255))
    window.blit(lang_text, (100, 150))
    lang_btn = Rect(400, 150, 150, 40)
    draw.rect(window, (100, 100, 100), lang_btn)
    window.blit(font_score.render("Toggle", True, (0, 0, 0)), (lang_btn.x + 25, lang_btn.y + 5))

    music_text = font_score.render("Music: Change Track", True, (255, 255, 255))
    window.blit(music_text, (100, 250))
    music_btn = Rect(400, 250, 150, 40)
    draw.rect(window, (100, 100, 100), music_btn)
    window.blit(font_score.render("Next", True, (0, 0, 0)), (music_btn.x + 35, music_btn.y + 5))

    back_btn = Rect(20, 20, 40, 40)
    window.blit(back_icon, (back_btn.x, back_btn.y))

    return lang_btn, music_btn, back_btn

# --- Основний цикл ---
while True:
    for e in event.get():
        if e.type == QUIT:
            quit()

        if game_state == "start":
            play_btn, settings_btn = show_start_screen()
            if e.type == MOUSEBUTTONDOWN:
                if play_btn.collidepoint(e.pos):
                    game_state = "level_select"
                elif settings_btn.collidepoint(e.pos):
                    game_state = "settings"

        elif game_state == "settings":
            lang_btn, music_btn, back_btn = show_settings_screen()
            if e.type == MOUSEBUTTONDOWN:
                if lang_btn.collidepoint(e.pos):
                    toggle_language()
                elif back_btn.collidepoint(e.pos):
                    game_state = "start"

        elif game_state == "level_select":
            back_btn = draw_level_select()
            if e.type == MOUSEBUTTONDOWN:
                mx, my = e.pos
                if back_btn.collidepoint(mx, my):
                    game_state = "start"
                for i, rect in enumerate(level_buttons, start=1):
                    if rect.collidepoint(mx, my) and i in unlocked_levels:
                        selected_level = i
                        reset_game_for_level(selected_level)
                        game_state = "playing"

        elif game_state == "playing":
            if e.type == KEYDOWN:
                if e.key == K_SPACE and not game_over:
                    player.jump()
                if e.key == K_r and game_over:
                    reset_game_for_level(selected_level)
                    game_over = False
                    game = True

    if game_state == "start":
        show_start_screen()

    elif game_state == "settings":
        show_settings_screen()

    elif game_state == "level_select":
        draw_level_select()

    elif game_state == "playing":
        if game:
            window.blit(background, (0, 0))
            player.update()
            player.reset()

            pipe_timer += 1
            if pipe_timer >= PIPE_DELAY:
                pipe_timer = 0
                pipe_x = win_width + 100
                pipes.append(SinglePipe(pipe_x, PIPE_SPEED))

            for pipe in pipes:
                pipe.update()
                pipe.reset()

            for pipe in pipes:
                pipe_collision_rect = pipe.rect.inflate(-0, -50)
                if player.collision_rect.colliderect(pipe_collision_rect):
                    game = False
                    game_over = True

            pipes = [p for p in pipes if p.rect.right > 0]

            if player.rect.y > win_height or player.rect.y < 0:
                game = False
                game_over = True

            score += 0.01
            score_text = font_score.render(f"Score: {int(score)}", True, (255, 255, 255))
            window.blit(score_text, (10, 10))
        else:
            show_game_over()

    display.update()
    clock.tick(60)
