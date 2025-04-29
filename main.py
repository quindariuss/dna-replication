import pygame
import random
from os.path import join

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Station states
STARTUP_SCREEN = 0
STATION_TEMPLATE = 1
STATION_UNZIP = 2
STATION_BUILD = 3
STATION_DELIVERY = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)

# Base pair mappings
BASE_PAIRS = {"A": "T", "T": "A", "C": "G", "G": "C"}

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DNA Pizzeria")
clock = pygame.time.Clock()

# Load assets
background_startup = pygame.image.load(join("assets", "restaurant.png"))  # Custom background image
logo_image = pygame.image.load(join("assets", "logo.png"))  # Logo image for the title
logo_rect = logo_image.get_rect(center=(WIDTH // 2, HEIGHT // 3))  # Center the logo

# Create a semi-transparent white overlay (alpha = 128 out of 255 for 50% transparency)
overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((255, 255, 255, 128))  # RGB color with alpha (255 is white, 128 is the transparency)

# Customer images (delivery zone, template background, and delivery background)
customer_data = {
    "Pent.S.": {
        "delivery_zone": "3.png",
        "background": "Pent_s_bubble.png",
        "delivery_bg": "Pent_s.png"
    },
    "Nitro.B.": {
        "delivery_zone": "1.png",
        "background": "Nitro_b_bubble.png",
        "delivery_bg": "Nitro_b.png"
    },
    "Phos.G.": {
        "delivery_zone": "2.png",
        "background": "Phos_g_bubble.png",
        "delivery_bg": "Phos_g.png"
    }
}


# Classes
class Customer:
    def __init__(self, name, delivery_zone, background, delivery_bg):
        self.name = name
        self.template = self.generate_template()
        self.delivery_zone = delivery_zone
        self.background = background
        self.delivery_bg = delivery_bg

    def generate_template(self):
        return ''.join(random.choices(list(BASE_PAIRS.keys()), k=8))

    def get_complement(self):
        return ''.join(BASE_PAIRS[b] for b in self.template)


class DNAProduct:
    def __init__(self):
        self.visible = False
        self.x = 640
        self.y = 360
        self.velocity = 5

    def draw(self, surface):
        if self.visible:
            pygame.draw.rect(surface, BLACK, (self.x, self.y, 50, 30))

    def reset_position(self):
        self.x = 640
        self.y = 360


class Pizza:
    def __init__(self):
        self.player_strand = [""] * 8


# Functions
def draw_startup_screen():
    # Draw the background image
    screen.blit(background_startup, (0, 0))

    # Apply the semi-transparent white overlay
    screen.blit(overlay, (0, 0))

    # Logo image
    screen.blit(logo_image, logo_rect)

    # Button for starting the game
    button_width = 200
    button_height = 50
    start_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50, button_width, button_height)

    # Button color change on hover
    if start_button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, start_button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, start_button_rect)

    # Button text
    font = pygame.font.Font(None, 36)
    button_text = font.render("Start Game", True, BLACK)
    screen.blit(button_text, (start_button_rect.x + (button_width - button_text.get_width()) // 2,
                             start_button_rect.y + (button_height - button_text.get_height()) // 2))

    # Handle button click
    if pygame.mouse.get_pressed()[0] and start_button_rect.collidepoint(pygame.mouse.get_pos()):
        global current_station
        current_station = STATION_TEMPLATE
        reset_game()


def draw_station():
    screen.blit(station_background_image, (0, 0))

    if current_station == STATION_TEMPLATE:
        draw_template_station()
    elif current_station == STATION_UNZIP:
        draw_unzip_station()
    elif current_station == STATION_BUILD:
        draw_build_station()
    elif current_station == STATION_DELIVERY:
        draw_delivery_station()

    draw_station_buttons()


def draw_station_buttons():
    button_width = 180
    button_height = 50
    y_position = HEIGHT - button_height - 10
    buttons = [
        ("Template", STATION_TEMPLATE),
        ("Unzip", STATION_UNZIP),
        ("Build", STATION_BUILD),
        ("Delivery", STATION_DELIVERY)
    ]

    for i, (text, station) in enumerate(buttons):
        x_position = i * (button_width + 10) + 10
        rect = pygame.Rect(x_position, y_position, button_width, button_height)

        # Button color change on hover
        if rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, rect)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, rect)

        # Button text
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, BLACK)
        screen.blit(text_surface, (x_position + (button_width - text_surface.get_width()) // 2,
                                   y_position + (button_height - text_surface.get_height()) // 2))

        # Handle button click
        if pygame.mouse.get_pressed()[0] and rect.collidepoint(pygame.mouse.get_pos()):
            global current_station
            current_station = station
            update_backgrounds()


def draw_template_station():
    font = pygame.font.Font(None, 36)
    template_text = font.render(f"Can I get {current_customer.template}", True, BLACK)
    screen.blit(template_text, (100, 100))


def draw_unzip_station():
    font = pygame.font.Font(None, 36)
    unzip_text = font.render("Unzipping Template Strand...", True, BLACK)
    screen.blit(unzip_text, (100, 100))


def draw_build_station():
    font = pygame.font.Font(None, 36)
    build_text = font.render("Building Complementary Strand:", True, BLACK)
    screen.blit(build_text, (100, 100))

    for i, base in enumerate(pizza.player_strand):
        base_text = font.render(base if base else "_", True, BLACK)
        screen.blit(base_text, (100 + i * 40, 200))


def draw_delivery_station():
    screen.blit(delivery_background_image, (0, 0))
    product.draw(screen)


def reset_game():
    pizza.player_strand = [""] * 8
    global current_customer, delivery_zone_image, station_background_image, delivery_background_image
    current_customer_name = random.choice(list(customer_data.keys()))
    customer_info = customer_data[current_customer_name]
    current_customer = Customer(
        current_customer_name,
        customer_info["delivery_zone"],
        customer_info["background"],
        customer_info["delivery_bg"]
    )
    delivery_zone_image = pygame.image.load(join("assets", current_customer.delivery_zone))
    station_background_image = pygame.image.load(join("assets", current_customer.background))
    delivery_background_image = pygame.image.load(join("assets", current_customer.delivery_bg))
    global current_station
    current_station = STATION_TEMPLATE
    product.reset_position()
    product.visible = False


def update_backgrounds():
    global station_background_image, delivery_background_image
    customer_info = customer_data[current_customer.name]
    station_background_image = pygame.image.load(join("assets", customer_info["background"]))
    delivery_background_image = pygame.image.load(join("assets", customer_info["delivery_bg"]))


# Initialize game state
current_station = STARTUP_SCREEN
pizza = Pizza()
product = DNAProduct()

# Load the first customer
current_customer_name = random.choice(list(customer_data.keys()))
customer_info = customer_data[current_customer_name]
current_customer = Customer(
    current_customer_name,
    customer_info["delivery_zone"],
    customer_info["background"],
    customer_info["delivery_bg"]
)
delivery_zone_image = pygame.image.load(join("assets", current_customer.delivery_zone))
station_background_image = pygame.image.load(join("assets", current_customer.background))
delivery_background_image = pygame.image.load(join("assets", current_customer.delivery_bg))


# Main game loop
def main():
    global current_station
    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if current_station == STARTUP_SCREEN:
            draw_startup_screen()  # Draw the startup screen
        else:
            draw_station()  # Draw the current station

        pygame.display.flip()

    pygame.quit()


# Start the game loop
main()