import pygame
import random
from os.path import join

pygame.init()

# Settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Stations
STARTUP_SCREEN = 0
STATION_TEMPLATE = 1
STATION_UNZIP = 2
STATION_BUILD = 3
STATION_DELIVERY = 4

# Music
pygame.mixer.init()
pygame.mixer.music.load(join("assets", "bgmusic.ogg"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)
GRAY = (200, 200, 200)
RED = (255, 100, 100)

# Base pair mappings
BASE_PAIRS = {"A": "T",
              "T": "A",
              "C": "G",
              "G": "C"}

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DNA Pizzeria")
clock = pygame.time.Clock()

# Load font once
font_main = pygame.font.Font(join("assets", "fonts", "Ldfcomicsansbold-zgma.ttf"), 36)

# Load assets
background_startup = pygame.image.load(join("assets", "restaurant.png"))
logo_image = pygame.image.load(join("assets", "logo.png"))
logo_rect = logo_image.get_rect(center=(WIDTH // 2, HEIGHT // 3))

background_unzip_1 = pygame.image.load(join("assets", "zipped.png"))
background_unzip_2 = pygame.image.load(join("assets", "unzipped.png"))
background_build = pygame.image.load(join("assets", "unzipped.png"))

overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((255, 255, 255, 128))  # 50% transparent white

customer_data = {
    "Pent.S.": {"delivery_zone": "3.png", "background": "Pent_s_bubble.png", "delivery_bg": "Pent_s.png"},
    "Nitro.B.": {"delivery_zone": "1.png", "background": "Nitro_b_bubble.png", "delivery_bg": "Nitro_b.png"},
    "Phos.G.": {"delivery_zone": "2.png", "background": "Phos_g_bubble.png", "delivery_bg": "Phos_g.png"}
}

# Draggable base class
class DraggableBase:
    def __init__(self, base, pos):
        self.base = base
        self.original_pos = pos
        self.rect = pygame.Rect(pos[0], pos[1], 40, 40)
        self.dragging = False
        self.offset = (0, 0)

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY , self.rect)
        txt_surf = font_main.render(self.base, True, BLACK)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def reset_position(self):
        self.rect.topleft = self.original_pos

# Draggable bases (A, T, C, G)
draggable_bases = []
base_options = ["A", "T", "C", "G"]
for i, base in enumerate(base_options):
    x = 600
    y = 150 + i * 60
    draggable_bases.append(DraggableBase(base, (x, y)))

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


class Pizza:
    def __init__(self):
        self.player_strand = [""] * 8  # For the player's complementary strand
        self.dragging_base = None  # To track which base is being dragged
        self.base_positions = [(100 + i * 40, 200) for i in range(8)]  # Target locations for the complementary strand
        self.dragged_bases = []  # To track the base pairs to be dragged

    def create_draggable_bases(self):
        self.dragged_bases = [
            {"letter": letter, "rect": pygame.Rect(100 + i * 50, 300, 40, 40)}
            for i, letter in enumerate(["A", "T", "C", "G"])
        ]

    def check_drop(self, mouse_pos):
        for i, base_rect in enumerate(self.dragged_bases):
            if base_rect["rect"].collidepoint(mouse_pos):
                return i  # Return the index of the base being dragged
        return None

    def update_base_position(self, base_index, target_position):
        base = self.dragged_bases[base_index]
        base["rect"].topleft = target_position

    def reset_base_positions(self):
        for base in self.dragged_bases:
            base["rect"].topleft = (100 + self.dragged_bases.index(base) * 50, 300)

    def draw(self, surface):
        for base in self.dragged_bases:
            pygame.draw.rect(surface, (0, 0, 0), base["rect"])  # Draw the base

        # Draw player strand
        for i, base in enumerate(self.player_strand):
            base_text = font_main.render(base if base else "_", True, BLACK)
            surface.blit(base_text, self.base_positions[i])


def draw_startup_screen():
    screen.blit(background_startup, (0, 0))
    screen.blit(overlay, (0, 0))
    screen.blit(logo_image, logo_rect)

    button_width, button_height = 200, 50
    start_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50, button_width, button_height)

    color = BUTTON_HOVER_COLOR if start_button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, color, start_button_rect)

    button_text = font_main.render("Start Game", True, BLACK)
    screen.blit(button_text, (start_button_rect.x + (button_width - button_text.get_width()) // 2,
                              start_button_rect.y + (button_height - button_text.get_height()) // 2))

    if pygame.mouse.get_pressed()[0] and start_button_rect.collidepoint(pygame.mouse.get_pos()):
        global current_station
        current_station = STATION_TEMPLATE
        reset_game()


def draw_station():
    if current_station == STATION_TEMPLATE:
        screen.blit(station_background_image, (0, 0))
    elif current_station == STATION_UNZIP:
        screen.blit(current_unzip_background, (0, 0))
    elif current_station == STATION_BUILD:
        screen.blit(background_build, (0, 0))
    elif current_station == STATION_DELIVERY:
        screen.blit(delivery_background_image, (0, 0))

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
    button_width, button_height = 180, 50
    y = HEIGHT - button_height - 10
    buttons = [("Template", STATION_TEMPLATE), ("Unzip", STATION_UNZIP),
               ("Build", STATION_BUILD), ("Delivery", STATION_DELIVERY)]

    for i, (text, station) in enumerate(buttons):
        x = i * (button_width + 10) + 10
        rect = pygame.Rect(x, y, button_width, button_height)
        color = BUTTON_HOVER_COLOR if rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect)

        txt = font_main.render(text, True, BLACK)
        screen.blit(txt, (x + (button_width - txt.get_width()) // 2, y + (button_height - txt.get_height()) // 2))

        if pygame.mouse.get_pressed()[0] and rect.collidepoint(pygame.mouse.get_pos()):
            global current_station
            current_station = station
            update_backgrounds()


def draw_template_station():
    template_text = font_main.render(f"Can I get {current_customer.template}", True, BLACK)
    screen.blit(template_text, (150, 50))


def draw_unzip_station():
    button_width, button_height = 50, 300
    button_rect = pygame.Rect(WIDTH // 7 - button_width // 1, HEIGHT // 6, button_width, button_height)
    color = (139, 69, 19) if button_rect.collidepoint(pygame.mouse.get_pos()) else (160, 82, 45)
    pygame.draw.rect(screen, color, button_rect)

    button_text = font_main.render(" ", True, BLACK)
    screen.blit(button_text, (button_rect.x + (button_width - button_text.get_width()) // 2,
                              button_rect.y + (button_height - button_text.get_height()) // 2))

    if pygame.mouse.get_pressed()[0] and button_rect.collidepoint(pygame.mouse.get_pos()):
        global current_unzip_background
        current_unzip_background = background_unzip_2


def draw_build_station():
    # Template strand
    for i, base in enumerate(current_customer.template):
        base_surf = font_main.render(base, True, RED)
        screen.blit(base_surf, (WIDTH // 2 - 100, 150 + i * 40))

    # Player's strand
    for i, base in enumerate(pizza.player_strand):
        char = base if base else "_"
        base_surf = font_main.render(char, True, WHITE)
        screen.blit(base_surf, (WIDTH//2 + 100, 150 + i * 40))

    # Draggable bases
    for base in draggable_bases:
        base.draw(screen)


def draw_delivery_station():
    screen.fill(WHITE)

    correct_strand = current_customer.get_complement()
    player_strand = ''.join(pizza.player_strand)

    if player_strand == correct_strand:
        review_text = "Great Job! Customer is happy! Perfect!"
    else:
        review_text = "Customer is upset! They got a weird Pizza?"

    review_surface = font_main.render(review_text, True, BLACK)
    screen.blit(review_surface, (WIDTH // 2 - review_surface.get_width() // 2, HEIGHT // 2 - 50))

    # Draw "Next Customer" button
    button_width, button_height = 250, 60
    next_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50, button_width, button_height)

    color = BUTTON_HOVER_COLOR if next_button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, color, next_button_rect)

    button_text = font_main.render("Next Customer", True, BLACK)
    screen.blit(button_text, (next_button_rect.x + (button_width - button_text.get_width()) // 2,
                              next_button_rect.y + (button_height - button_text.get_height()) // 2))

    # Handle button click
    if pygame.mouse.get_pressed()[0] and next_button_rect.collidepoint(pygame.mouse.get_pos()):
        reset_game()


def reset_game():
    pizza.player_strand = [""] * 8
    global current_customer, delivery_zone_image, station_background_image, delivery_background_image
    current_customer_name = random.choice(list(customer_data.keys()))
    info = customer_data[current_customer_name]
    current_customer = Customer(current_customer_name, info["delivery_zone"], info["background"], info["delivery_bg"])
    station_background_image = pygame.image.load(join("assets", current_customer.background))
    delivery_background_image = pygame.image.load(join("assets", current_customer.delivery_bg))
    global current_station, current_unzip_background
    current_station = STATION_TEMPLATE
    current_unzip_background = background_unzip_1


def update_backgrounds():
    global station_background_image, delivery_background_image
    info = customer_data[current_customer.name]
    station_background_image = pygame.image.load(join("assets", info["background"]))
    delivery_background_image = pygame.image.load(join("assets", info["delivery_bg"]))


# Initialize game state
current_station = STARTUP_SCREEN
pizza = Pizza()
product = None  # Not used in Build Station yet


# Game Loop
def main():
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle mouse events for draggable bases
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for base in draggable_bases:
                    if base.rect.collidepoint(pos):
                        base.dragging = True
                        mouse_x, mouse_y = pos
                        offset_x = base.rect.x - mouse_x
                        offset_y = base.rect.y - mouse_y
                        base.offset = (offset_x, offset_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                pos = event.pos
                for base in draggable_bases:
                    if base.dragging:
                        base.dragging = False
                        for i in range(len(pizza.player_strand)):
                            slot_rect = pygame.Rect(WIDTH // 2 + 100, 150 + i * 40, 30, 30)
                            if slot_rect.collidepoint(base.rect.center):
                                pizza.player_strand[i] = base.base
                                break
                        base.reset_position()

            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                for base in draggable_bases:
                    if base.dragging:
                        base.rect.x = pos[0] + base.offset[0]
                        base.rect.y = pos[1] + base.offset[1]

        if current_station == STARTUP_SCREEN:
            draw_startup_screen()
        else:
            draw_station()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
