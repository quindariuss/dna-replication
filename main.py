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
STARTUP_SCREEN = "startup"

current_station = STARTUP_SCREEN

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

# Buttons for navigation (repositioned to the bottom)
button_width, button_height = 120, 50
button_padding = 20
buttons = [
    Button((button_padding, HEIGHT - button_height - button_padding, button_width, button_height), "Order",
           STATION_TEMPLATE),
    Button((button_padding * 2 + button_width, HEIGHT - button_height - button_padding, button_width, button_height),
           "Unzip", STATION_UNZIP),
    Button(
        (button_padding * 3 + button_width * 2, HEIGHT - button_height - button_padding, button_width, button_height),
        "Build", STATION_BUILD),
    Button(
        (button_padding * 4 + button_width * 3, HEIGHT - button_height - button_padding, button_width, button_height),
        "Send", STATION_TERMINATE),
]

# Draggable bases (A, T, C, G)
draggable_bases = []
base_options = ["A", "T", "C", "G"]
for i, base in enumerate(base_options):
    x = 600
    y = 150 + i * 60
    draggable_bases.append(DraggableBase(base, (x, y)))

# Drop zone for the final DNA (the customer area) - moved to the top
DROP_ZONE = pygame.Rect(WIDTH // 2 - 50, 50, 100, 50)

# Background Image (if you have one)
background_image = pygame.image.load("B-M0.jpg")  # Path to the image (Replace with your image)


# Drawing functions
def draw_station():
    screen.fill(WHITE)

    # Draw content for current station
    if current_station == STARTUP_SCREEN:
        draw_startup_screen()

    elif current_station == STATION_TEMPLATE:
        draw_text_below(f"{current_customer.name}'s Order:", 320)
        draw_text_below(f"DNA Template: {current_customer.template}", 360)

    elif current_station == STATION_UNZIP:
        # Draw template strand (left)
        template = current_customer.template
        for i, base in enumerate(template):
            base_surf = font.render(base, True, RED)
            x = WIDTH // 2 - 100
            y = 150 + i * 40
            screen.blit(base_surf, (x, y))

        # Draw placeholder for complementary strand (right)
        for i in range(len(template)):
            base_surf = font.render("_", True, BLACK)
            x = WIDTH // 2 + 100
            y = 150 + i * 40
            screen.blit(base_surf, (x, y))

    elif current_station == STATION_BUILD:
        # Template strand
        for i, base in enumerate(current_customer.template):
            base_surf = font.render(base, True, RED)
            screen.blit(base_surf, (WIDTH // 2 - 100, 150 + i * 40))

        # Player's strand
        for i, base in enumerate(pizza.player_strand):
            char = base if base else "_"
            base_surf = font.render(char, True, BLACK)
            screen.blit(base_surf, (WIDTH // 2 + 100, 150 + i * 40))

        # Draggable bases
        for base in draggable_bases:
            base.draw(screen)

    elif current_station == STATION_TERMINATE:
        check_order_correctness()

        # Draw drop zone (now at the top of the screen)
        pygame.draw.rect(screen, RED, DROP_ZONE, 2)
        draw_text_below("Drag the DNA here!", 120)  # Adjusted the position of the text

    # Draw nav buttons at the bottom of the screen
    for button in buttons:
        button.draw(screen)


def draw_startup_screen():
    # Draw background
    screen.blit(background_image, (0, 0))

    # Draw title text
    title_surf = font.render("DNA Pizzeria", True, RED)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_surf, title_rect)

    # Draw Start Button
    start_button = Button((WIDTH // 2 - 100, HEIGHT // 2, 200, 50), "Start Game", STATION_TEMPLATE)
    start_button.draw(screen)


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


def reset_game():
    pizza.player_strand = [""] * 8
    global current_customer
    current_customer = Customer(random.choice(customer_names))

    global current_station
    current_station = STATION_TEMPLATE


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

            if current_station == STARTUP_SCREEN:
                if pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50).collidepoint(pos):
                    current_station = STATION_TEMPLATE

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
                    for i in range(len(pizza.player_strand)):
                        slot_rect = pygame.Rect(WIDTH // 2 + 100, 150 + i * 40, 30, 30)
                        if slot_rect.collidepoint(base.rect.center):
                            pizza.player_strand[i] = base.base
                            break

                    if current_station == STATION_TERMINATE and DROP_ZONE.collidepoint(base.rect.center):
                        check_order_correctness()
                        reset_game()

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