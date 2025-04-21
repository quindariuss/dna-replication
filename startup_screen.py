import pygame
import sys

WHITE = (255, 255, 255)
RED = (255, 100, 100)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("comicsans", 36)

# Button class
class Button:
    def __init__(self, rect, text, target_state):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.target_state = target_state

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        txt_surf = font.render(self.text, True, BLACK)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_startup_screen(screen, width, height):
    # Draw background (optional)
    # screen.blit(background_image, (0, 0))  # Uncomment if you want to add a background image

    # Draw title text
    title_surf = font.render("DNA Pizzeria", True, RED)
    title_rect = title_surf.get_rect(center=(width // 2, height // 3))
    screen.blit(title_surf, title_rect)

    # Draw Start Button
    start_button = Button((width // 2 - 100, height // 2, 200, 50), "Start Game", "template")
    start_button.draw(screen)

    return start_button
