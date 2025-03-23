import pygame
import sys
from .button import Button

pygame.init()

# screen dimensions
WINDOW_DIMS = (32 * 32, 32 * 32)
SCREEN_WIDTH, SCREEN_HEIGHT = WINDOW_DIMS

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Menu")

BG = pygame.image.load("res/imgs/Background.png")
BG = pygame.transform.scale(BG, (SCREEN_WIDTH, SCREEN_HEIGHT))

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def render_auto_scaled_text(text, color, max_width, max_font_size, min_font_size):
    font_size = max_font_size
    font = get_font(font_size)
    text_surface = font.render(text, True, color)
    while text_surface.get_width() > max_width and font_size > min_font_size:
        font_size -= 1
        font = get_font(font_size)
        text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect(), font_size

def play(start_game_callback):
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100), 
                           text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu(start_game_callback)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu(start_game_callback)

        pygame.display.update()

def options(start_game_callback):
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        # Render auto-scaled text for the OPTIONS screen
        options_text_surface, options_text_rect, _ = render_auto_scaled_text(
            text="This is the OPTIONS screen.",
            color="Black",
            max_width=SCREEN_WIDTH - 40,
            max_font_size=60,
            min_font_size=12
        )
        options_text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        SCREEN.blit(options_text_surface, options_text_rect)

        # Create a "BACK" button
        OPTIONS_BACK = Button(
            image=None,
            pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100),
            text_input="BACK",
            font=get_font(50),
            base_color="Black",
            hovering_color="Green"
        )

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu(start_game_callback)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu(start_game_callback)

        pygame.display.update()

def main_menu(start_game_callback):
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("ROGUE GAME", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("res/imgs/Play Rect.png"), pos=(SCREEN_WIDTH // 2, 250), 
                             text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("res/imgs/Options Rect.png"), pos=(SCREEN_WIDTH // 2, 400), 
                                text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("res/imgs/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 550), 
                             text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    start_game_callback()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options(start_game_callback)
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()