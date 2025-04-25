import pygame
import random
from os.path import join

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DNA Pizzeria")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)  # Use default font for web compatibility

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
    def __init__(self, name, delivery_zone):
        self.name = name
        self.template = self.generate_template()
        self.delivery_zone = delivery_zone

    def generate_template(self):
        return ''.join(random.choices(list(BASE_PAIRS.keys()), k=8))

    def get_complement(self):
        return ''.join(BASE_PAIRS[b] for b in self.template)

# Product class
class Product:
    def __init__(self, pos):
        self.rect = pygame.Rect(pos[0], pos[1], 120, 50)
        self.original_pos = pos
        self.dragging = False
        self.offset = (0, 0)
        self.visible = False
        self.label = "DNA Pizza"

    def draw(self, surface):
        if self.visible:
            pygame.draw.rect(surface, (150, 200, 255), self.rect)
            txt = font.render(self.label, True, BLACK)
            txt_rect = txt.get_rect(center=self.rect.center)
            surface.blit(txt, txt_rect)

    def reset_position(self):
        self.rect.topleft = self.original_pos

product = Product((WIDTH // 2 - 60, 400))

# Initial customer and delivery zones
customer_data = {
    "Pent.S.": "3.png",
    "Nitro.B.": "1.png",
    "Phos.G.": "2.png"
}
current_customer_name = random.choice(list(customer_data.keys()))
current_customer = Customer(current_customer_name, customer_data[current_customer_name])

delivery_zone_image = pygame.image.load(join("assets", current_customer.delivery_zone))

# Buttons for navigation
button_width, button_height = 120, 50
button_padding = 20
buttons = [
    Button((button_padding, HEIGHT - button_height - button_padding, button_width, button_height), "Order", STATION_TEMPLATE),
    Button((button_padding * 2 + button_width, HEIGHT - button_height - button_padding, button_width, button_height), "Unzip", STATION_UNZIP),
    Button((button_padding * 3 + button_width * 2, HEIGHT - button_height - button_padding, button_width, button_height), "Build", STATION_BUILD),
    Button((button_padding * 4 + button_width * 3, HEIGHT - button_height - button_padding, button_width, button_height), "Send", STATION_TERMINATE),
]

# Draggable bases (A, T, C, G)
draggable_bases = []
base_options = ["A", "T", "C", "G"]
for i, base in enumerate(base_options):
    x = 600
    y = 150 + i * 60
    draggable_bases.append(DraggableBase(base, (x, y)))

DROP_ZONE = pygame.Rect(WIDTH // 2 - 50, 50, 100, 50)
background_image = pygame.image.load(join("assets", "restaurant.png"))

def draw_station():
    screen.fill(WHITE)

    if current_station == STARTUP_SCREEN:
        draw_startup_screen()

    elif current_station == STATION_TEMPLATE:
        draw_text_below(f"{current_customer.name}'s Order:", 320)
        draw_text_below(f"DNA Template: {current_customer.template}", 360)

    elif current_station == STATION_UNZIP:
        template = current_customer.template
        for i, base in enumerate(template):
            base_surf = font.render(base, True, RED)
            x = WIDTH // 2 - 100
            y = 150 + i * 40
            screen.blit(base_surf, (x, y))

        for i in range(len(template)):
            base_surf = font.render("_", True, BLACK)
            x = WIDTH // 2 + 100
            y = 150 + i * 40
            screen.blit(base_surf, (x, y))

    elif current_station == STATION_BUILD:
        for i, base in enumerate(current_customer.template):
            base_surf = font.render(base, True, RED)
            screen.blit(base_surf, (WIDTH // 2 - 100, 150 + i * 40))

        for i, base in enumerate(pizza.player_strand):
            char = base if base else "_"
            base_surf = font.render(char, True, BLACK)
            screen.blit(base_surf, (WIDTH // 2 + 100, 150 + i * 40))

        for base in draggable_bases:
            base.draw(screen)

    elif current_station == STATION_TERMINATE:
        check_order_correctness()
        pygame.draw.rect(screen, RED, DROP_ZONE, 2)
        product.draw(screen)

        # Scale the delivery zone image and position it at the drop zone location
        scaled_delivery_zone_image = pygame.transform.scale(delivery_zone_image, (250, 250))
        screen.blit(scaled_delivery_zone_image, (DROP_ZONE.centerx - 137, DROP_ZONE.centery - 90))

    if current_station != STARTUP_SCREEN:  # Show station buttons only after startup screen
        for button in buttons:
            button.draw(screen)

def draw_startup_screen():
    screen.blit(background_image, (0, 0))
    title_surf = font.render("DNA Pizzeria", True, RED)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_surf, title_rect)

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

    if player_strand == correct_strand:
        draw_text_center("Order Sent! Correct DNA!", screen)
        product.label = "Perfect DNA Pizza"
    else:
        draw_text_center("Oops! Still a Pizza...", screen)
        product.label = "Weird DNA Pizza"

    product.visible = True

def reset_game():
    pizza.player_strand = [""] * 8
    global current_customer, delivery_zone_image
    current_customer_name = random.choice(list(customer_data.keys()))
    current_customer = Customer(current_customer_name, customer_data[current_customer_name])
    delivery_zone_image = pygame.image.load(join("assets", current_customer.delivery_zone))
    global current_station
    current_station = STATION_TEMPLATE
    product.reset_position()
    product.visible = False

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
                    base.offset = (base.rect.x - mouse_x, base.rect.y - mouse_y)

            if product.visible and product.rect.collidepoint(pos):
                product.dragging = True
                mouse_x, mouse_y = pos
                product.offset = (product.rect.x - mouse_x, product.rect.y - mouse_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            for base in draggable_bases:
                if base.dragging:
                    base.dragging = False
                    for i in range(len(pizza.player_strand)):
                        slot_rect = pygame.Rect(WIDTH // 2 + 100, 150 + i * 40, 30, 30)
                        if slot_rect.collidepoint(base.rect.center):
                            pizza.player_strand[i] = base.base
                            break
                    base.reset_position()

            if product.dragging:
                product.dragging = False
                if DROP_ZONE.collidepoint(product.rect.center):
                    reset_game()
                else:
                    product.reset_position()

        elif event.type == pygame.MOUSEMOTION:
            for base in draggable_bases:
                if base.dragging:
                    mouse_x, mouse_y = event.pos
                    base.rect.x = mouse_x + base.offset[0]
                    base.rect.y = mouse_y + base.offset[1]

            if product.dragging:
                mouse_x, mouse_y = event.pos
                product.rect.x = mouse_x + product.offset[0]
                product.rect.y = mouse_y + product.offset[1]

    draw_station()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
