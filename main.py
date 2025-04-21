import pygame
import sys
import random

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DNA Pizzeria")

clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 36)

# Define game states
STATION_TEMPLATE = "template"
STATION_UNZIP = "unzip"
STATION_BUILD = "build"
STATION_TERMINATE = "terminate"

current_station = STATION_TEMPLATE

# Define colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 100, 100)

# DNA base pairs
BASE_PAIRS = {
    "A": "T",
    "T": "A",
    "C": "G",
    "G": "C"
}

# Pizza object
class Pizza:
    def __init__(self):
        self.player_strand = [""] * 8
        self.bake_time = 0

pizza = Pizza()

# Button class
class Button:
    def __init__(self, rect, text, target_state):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.target_state = target_state

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        txt_surf = font.render(self.text, True, BLACK)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Draggable base class
class DraggableBase:
    def __init__(self, base, pos):
        self.base = base
        self.original_pos = pos
        self.rect = pygame.Rect(pos[0], pos[1], 40, 40)
        self.dragging = False
        self.offset = (0, 0)

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        txt_surf = font.render(self.base, True, BLACK)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def reset_position(self):
        self.rect.topleft = self.original_pos

# Customer logic
class Customer:
    def __init__(self, name):
        self.name = name
        self.template = self.generate_template()

    def generate_template(self):
        return ''.join(random.choices(list(BASE_PAIRS.keys()), k=8))

    def get_complement(self):
        return ''.join(BASE_PAIRS[b] for b in self.template)

# Initial customer
customer_names = ["Lena", "Max", "Zoe", "Kai", "Dr. Byte"]
current_customer = Customer(random.choice(customer_names))

# Buttons for navigation
buttons = [
    Button((20, 20, 120, 50), "Order", STATION_TEMPLATE),
    Button((150, 20, 120, 50), "Unzip", STATION_UNZIP),
    Button((280, 20, 120, 50), "Build", STATION_BUILD),
    Button((410, 20, 120, 50), "Send", STATION_TERMINATE),
]

# Draggable bases (A, T, C, G)
draggable_bases = []
base_options = ["A", "T", "C", "G"]
for i, base in enumerate(base_options):
    x = 600
    y = 150 + i * 60
    draggable_bases.append(DraggableBase(base, (x, y)))

# Drawing functions
def draw_station():
    screen.fill(WHITE)

    # Draw nav buttons
    for button in buttons:
        button.draw(screen)

    # Draw content for current station
    if current_station == STATION_TEMPLATE:
        draw_text_center("Order Station - DNA template orders", screen)
        draw_text_below(f"{current_customer.name}'s Order:", 320)
        draw_text_below(f"DNA Template: {current_customer.template}", 360)

    elif current_station == STATION_UNZIP:
        draw_text_center("Unzip Station - Unzip the DNA", screen)

        # Left strand (template)
        for i, base in enumerate(current_customer.template):
            base_surf = font.render(base, True, RED)
            screen.blit(base_surf, (WIDTH//2 - 100, 150 + i * 40))

        # Right strand (complement)
        for i, base in enumerate(current_customer.get_complement()):
            base_surf = font.render(base, True, BLACK)
            screen.blit(base_surf, (WIDTH//2 + 100, 150 + i * 40))

    elif current_station == STATION_BUILD:
        draw_text_center("Build Station - Build the DNA", screen)

        # Template strand
        for i, base in enumerate(current_customer.template):
            base_surf = font.render(base, True, RED)
            screen.blit(base_surf, (WIDTH//2 - 100, 150 + i * 40))

        # Player's strand
        for i, base in enumerate(pizza.player_strand):
            char = base if base else "_"
            base_surf = font.render(char, True, BLACK)
            screen.blit(base_surf, (WIDTH//2 + 100, 150 + i * 40))

        # Draggable bases
        for base in draggable_bases:
            base.draw(screen)

    elif current_station == STATION_TERMINATE:
        check_order_correctness()
        draw_text_center("Send Out - Send DNA to customer", screen)

def draw_text_center(text, surface):
    txt_surf = font.render(text, True, BLACK)
    txt_rect = txt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surface.blit(txt_surf, txt_rect)

def draw_text_below(text, y):
    txt_surf = font.render(text, True, BLACK)
    txt_rect = txt_surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(txt_surf, txt_rect)

def check_order_correctness():
    correct_strand = current_customer.get_complement()
    player_strand = "".join(pizza.player_strand)

    # If player's strand matches the complement strand, the order is correct
    if player_strand == correct_strand:
        draw_text_center("Order Sent! Correct DNA!", screen)
    else:
        draw_text_center("Incorrect DNA! Try Again.", screen)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for button in buttons:
                if button.is_clicked(pos):
                    current_station = button.target_state

            for base in draggable_bases:
                if base.rect.collidepoint(pos):
                    base.dragging = True
                    mouse_x, mouse_y = pos
                    offset_x = base.rect.x - mouse_x
                    offset_y = base.rect.y - mouse_y
                    base.offset = (offset_x, offset_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            for base in draggable_bases:
                if base.dragging:
                    base.dragging = False
                    # Try to place on strand
                    for i in range(len(pizza.player_strand)):
                        slot_rect = pygame.Rect(WIDTH//2 + 100, 150 + i * 40, 30, 30)
                        if slot_rect.collidepoint(base.rect.center):
                            pizza.player_strand[i] = base.base
                            break
                    base.reset_position()

        elif event.type == pygame.MOUSEMOTION:
            for base in draggable_bases:
                if base.dragging:
                    mouse_x, mouse_y = event.pos
                    base.rect.x = mouse_x + base.offset[0]
                    base.rect.y = mouse_y + base.offset[1]

    draw_station()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
