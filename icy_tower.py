import pygame
import sys
import random
import math

# Inicjalizacja PyGame
pygame.init()

# Stałe gry
WIDTH = 800
HEIGHT = 600
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLATFORM_HEIGHT = 10
COIN_CHANCE = 0.2 
SPIKE_HIT_RANGE = 15
CAMERA_SPEED = 0.1
CAMERA_FOLLOW_HEIGHT = 0.4 

# Ustawienia ekranu
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Icy Tower Clone")

# Kolory 
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'BLUE': (20, 100, 200),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'YELLOW': (255, 255, 0),
    'GOLD': (255, 215, 0),
    'PURPLE': (255, 100, 255),
    'READY': (255, 165, 0)  # Pomarańczowy
}

# Regiony
REGIONS = [
    {
        "name": "Podstawa",
        "height": -4000,
        "color": (30, 30, 70),
        "gap_y": 70, 
        "platform_width": (120, 200), 
        "platform_types": {"moving": 0.0, "slippery": 0.0, "spikes": 0.0},  
        "platform_speed": [-2, -1, 1, 2]
    },
    {
        "name": "Środek",
        "height": -10000,
        "color": (70, 50, 100),
        "gap_y": 85,
        "platform_width": (100, 180),
        "platform_types": {"moving": 0.2, "slippery": 0.1, "spikes": 0.05},  
        "platform_speed": [-3, -2, 2, 3]
    },
    {
        "name": "Wyżyny",
        "height": -18000,
        "color": (40, 70, 120),
        "gap_y": 100,
        "platform_width": (90, 160),
        "platform_types": {"moving": 0.3, "slippery": 0.2, "spikes": 0.1}, 
        "platform_speed": [-4, -3, 3, 4]
    },
    {
        "name": "Chmury",
        "height": -28000,
        "color": (20, 50, 100),
        "gap_y": 120,
        "platform_width": (80, 140),
        "platform_types": {"moving": 0.4, "slippery": 0.3, "spikes": 0.15}, 
        "platform_speed": [-5, -4, 4, 5]
    },
    {
        "name": "Stratosfera",
        "height": float('-inf'),
        "color": (10, 20, 60),
        "gap_y": 140,
        "platform_width": (70, 120),
        "platform_types": {"moving": 0.5, "slippery": 0.4, "spikes": 0.2}, 
        "platform_speed": [-6, -5, 5, 6]
    }
]

# Ustawienia poziomów trudności
DIFFICULTY_SETTINGS = {
    "No Lava": {"lava_speed": 0, "lava_start": float('inf')},
    "Casual": {"lava_speed": 2.0, "lava_start": HEIGHT + 500}, 
    "Hard": {"lava_speed": 5.0, "lava_start": HEIGHT + 300} 
}

# Stałe dla typów platform i ich prawdopodobieństw
PLATFORM_TYPES = {
    "NORMAL": {"range": (0.6, 1.0), "color": COLORS['BLUE']},
    "SPIKES": {"range": (0.0, 0.1), "color": COLORS['BLUE']},
    "MOVING": {"range": (0.1, 0.4), "color": (50, 200, 50)},
    "SLIPPERY": {"range": (0.4, 0.6), "color": (100, 200, 255)}
}

# Ustawienia gracza
class Player:
    def __init__(self):
        # Podstawowe atrybuty
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 150  # Pozycja startowa nad platformą startową
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -20
        self.gravity = 0.8
        
        # Stan gracza
        self.is_jumping = False
        self.on_ground = False
        self.first_jump_made = False
        self.jump_cooldown = 0
        self.on_slippery = False
        self.hit_by_spike = False
        self.last_platform_slippery = False
        
        # System punktacji i regionów
        self.score = 0
        self.highest_platform = 0
        self.screen_y = self.y
        self.prev_y = self.y
        self.current_region = 0
        
        # System hiper skoku
        self.coins = 0
        self.max_coins = 5
        self.hyper_jump_charges = 0
        self.max_hyper_jump_charges = 1
        self.hyper_jump_active = False
        self.hyper_jump_power = -35
        self.hyper_jump_effect_time = 0
        self.character_state = "normal"

    def update(self, platforms, camera_y, lava_height):
        self.prev_y = self.y
        
        # Aktualizacja fizyki
        self.vel_y += self.gravity
        self.y += self.vel_y
        self.x += self.vel_x
        self.vel_x *= 0.9
        
        # Aktualizacja pozycji na ekranie
        self.screen_y = self.y - camera_y
        self.x = max(0, min(self.x, WIDTH - self.width))
        
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
            
        # Resetowanie flag
        self.on_ground = False
        self.on_slippery = False
        self.hit_by_spike = False
        
        # Kolizje z platformami
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.prev_y + self.height <= platform.y and 
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and 
                self.vel_y > 0):
                
                if platform.has_spikes:
                    player_center_x = self.x + self.width / 2
                    spike_x = platform.x + platform.spike_offset
                    if abs(player_center_x - spike_x) < 15:
                        return False
                
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
                self.on_slippery = platform.is_slippery
                self.last_platform_slippery = platform.is_slippery
                
                if platform.y < self.highest_platform:
                    self.score += int((self.highest_platform - platform.y) / 10)
                    self.highest_platform = platform.y
                break
        
        # Aktualizacja regionu na podstawie wysokości
        for i, region in enumerate(REGIONS):
            if self.highest_platform > region["height"]:
                self.current_region = i
                break
        
        # Aktualizacja efektu hiper skoku
        if self.hyper_jump_effect_time > 0:
            self.hyper_jump_effect_time -= 1
            if self.hyper_jump_effect_time == 0:
                self.character_state = "charged" if self.hyper_jump_charges > 0 else "normal"
        
        # Aktualizacja stanu postaci
        if self.coins >= self.max_coins and self.character_state == "normal":
            self.character_state = "charged"
            self.hyper_jump_charges = 1
        
        # Sprawdzenie kolizji z lawą lub spadnięcia
        return not (self.y > camera_y + HEIGHT or self.y + self.height > lava_height)

    def jump(self):
        if self.on_ground and self.jump_cooldown == 0:
            jump_force = self.hyper_jump_power if (self.hyper_jump_active and self.hyper_jump_charges > 0) else self.jump_power
            
            if self.on_slippery:
                jump_force *= 1.2  
                direction = 1 if random.random() > 0.5 else -1
                self.vel_x += direction * random.uniform(8.0, 12.0)  
            
            if self.hyper_jump_active and self.hyper_jump_charges > 0:
                self.hyper_jump_charges -= 1
                self.hyper_jump_active = False
                self.hyper_jump_effect_time = 30
                self.character_state = "hyper"
                self.coins = 0
            
            self.vel_y = jump_force
            self.on_ground = False
            self.is_jumping = True
            self.jump_cooldown = 5
            self.first_jump_made = True

    def activate_hyper_jump(self):
        if self.hyper_jump_charges > 0 and not self.hyper_jump_active:
            self.hyper_jump_active = True
            self.character_state = "ready"
            return True
        return False

    def draw(self, camera_y):
        # Wybierz kolor gracza na podstawie stanu
        player_colors = {
            "normal": COLORS['RED'],
            "charged": COLORS['GOLD'],
            "ready": COLORS['READY'], 
            "hyper": COLORS['PURPLE']
        }
        player_color = player_colors[self.character_state]
        
        # Rysuj postać
        pygame.draw.rect(screen, player_color, (self.x, self.y - camera_y, self.width, self.height))
        
        # Oczy
        pygame.draw.rect(screen, COLORS['WHITE'], (self.x + 5, self.y - camera_y + 10, 5, 5))
        pygame.draw.rect(screen, COLORS['WHITE'], (self.x + 20, self.y - camera_y + 10, 5, 5))
        
        # Efekty specjalne dla charged/hyper stanu
        if self.character_state == "charged":
            # Strzałka nad głową
            pygame.draw.polygon(screen, COLORS['GOLD'], [
                (self.x + self.width // 2, self.y - camera_y - 20),
                (self.x + self.width // 2 - 10, self.y - camera_y - 10),
                (self.x + self.width // 2 + 10, self.y - camera_y - 10)
            ])
        elif self.character_state == "hyper":
            # Efekt prędkości
            pygame.draw.polygon(screen, COLORS['PURPLE'], [
                (self.x + 5, self.y - camera_y + self.height),
                (self.x + self.width - 5, self.y - camera_y + self.height),
                (self.x + self.width // 2, self.y - camera_y + self.height + 15)
            ])

# Ustawienia platform
class Platform:
    def __init__(self, x, y, width, region=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT
        self.region = region
        self.vertical_gap = 0
        
        # Właściwości platformy
        self.has_coin = False
        self.coin_collected = False
        self.coin_animation_offset = random.random() * 6.28
        
        # Domyślne wartości
        self.is_moving = False
        self.is_slippery = False
        self.has_spikes = False
        self.spike_offset = 0  
        self.color = COLORS['BLUE']
        
        # Ustawienia platformy na podstawie regionu
        region_data = REGIONS[region]["platform_types"]
        
        # Losowanie typu platformy (normalna/ruchoma/śliska)
        rand_val = random.random()
        if rand_val < region_data["moving"]:
            self.is_moving = True
            self.color = (50, 200, 50)
            self.vel_x = random.choice(REGIONS[region]["platform_speed"])
            self.move_range = random.randint(100, 200)
            self.start_x = x
            self.left_limit = max(0, self.start_x - self.move_range)
            self.right_limit = min(WIDTH - self.width, self.start_x + self.move_range)
        elif rand_val < region_data["moving"] + region_data["slippery"]:
            self.is_slippery = True
            self.color = (100, 200, 255)
            self.shine_positions = [random.randint(int(x + 10), int(x + width - 10)) for _ in range(3)]
            
        # Niezależne losowanie kolców
        if random.random() < region_data["spikes"]:
            self.has_spikes = True
            self.spike_offset = width // 2  
            
        # Losowanie monety
        if not self.has_spikes and random.random() < COIN_CHANCE:
            self.has_coin = True

    def update(self):
        if self.is_moving:
            self.x += self.vel_x
            if (self.x >= self.right_limit) or (self.x <= self.left_limit):
                self.vel_x *= -1
                self.x = min(max(self.x, self.left_limit), self.right_limit)
                
    def draw(self, camera_y):
        # Rysuj podstawową platformę
        platform_rect = pygame.Rect(self.x, self.y - camera_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, platform_rect)
        pygame.draw.rect(screen, COLORS['WHITE'], platform_rect, 1)
        
        # Rysowanie kolców jeśli są 
        if self.has_spikes:
            spike_x = self.x + self.spike_offset
            pygame.draw.polygon(screen, (200, 50, 50), [
                (spike_x, self.y - camera_y - 10),
                (spike_x - 5, self.y - camera_y),
                (spike_x + 5, self.y - camera_y)
            ])
        
        # Rysowanie monet jeśli są
        if self.has_coin and not self.coin_collected:
            coin_x = self.x + self.width / 2
            coin_y = self.y - 30 + math.sin(pygame.time.get_ticks() / 1000.0 * 2 + self.coin_animation_offset) * 1.5
            pygame.draw.circle(screen, COLORS['GOLD'], (int(coin_x), int(coin_y - camera_y)), 8)
            pygame.draw.circle(screen, (255, 235, 100), (int(coin_x), int(coin_y - camera_y)), 5)
        
        # Rysowanie wskaźniki dla ruchomej platformy
        if self.is_moving:
            pygame.draw.line(screen, COLORS['YELLOW'], 
                (self.left_limit, self.y - camera_y + self.height/2),
                (self.right_limit + self.width, self.y - camera_y + self.height/2), 1)
        
        # Rysowanie błysków dla śliskiej platformy
        if self.is_slippery:
            for shine_x in self.shine_positions:
                pygame.draw.circle(screen, COLORS['WHITE'], (shine_x, self.y - camera_y + 5), 2)

    def check_coin_collection(self, player):
        if self.has_coin and not self.coin_collected:
            coin_x = self.x + self.width / 2
            coin_y = self.y - 30
            player_center = (player.x + player.width / 2, player.y + player.height / 2)
            distance = ((player_center[0] - coin_x) ** 2 + (player_center[1] - coin_y) ** 2) ** 0.5
            
            if distance < 28:
                self.coin_collected = True
                if player.coins < player.max_coins:
                    player.coins += 1
                    if player.coins >= player.max_coins:
                        player.hyper_jump_charges = min(player.max_hyper_jump_charges, player.hyper_jump_charges + 1)
                        player.character_state = "charged"
                return True
        return False

# Klasa lawy
class Lava:
    def __init__(self, initial_height):
        self.height = initial_height
        self.rise_speed = 1.8
        self.active = False
        
    def update(self):
        if self.active:
            self.height -= self.rise_speed
        
    def draw(self, camera_y):
        lava_top = self.height - camera_y
        if lava_top > HEIGHT:
            return
            
        pygame.draw.rect(screen, (255, 80, 0), (0, lava_top, WIDTH, HEIGHT - lava_top))
        pygame.draw.rect(screen, (255, 200, 0), (0, lava_top - 5, WIDTH, 5))

# Funkcja generująca platformy
def generate_platforms(num_platforms, start_y, current_region=0):
    platforms = []
    y = start_y
    last_center_x = WIDTH // 2
    max_offset = 200  
    
    for i in range(num_platforms):
        region = REGIONS[current_region]
        
        width = random.randint(*region["platform_width"])
        
        new_center = random.randint(
            max(width//2, last_center_x - max_offset),
            min(WIDTH - width//2, last_center_x + max_offset)
        )
        x = new_center - width//2
        
        platform = Platform(x, y, width, current_region)
        platforms.append(platform)
        
        last_center_x = new_center
        y -= region["gap_y"]
    
    return platforms

class Menu:
    def __init__(self):
        self.selected_option = 0
        self.options = list(DIFFICULTY_SETTINGS.keys())
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 48)
        self.title_color = COLORS['GOLD']
        self.selected_color = COLORS['WHITE']
        self.unselected_color = (150, 150, 150)
        
    def draw(self):
        screen.fill(COLORS['BLACK'])
        
        # Tytuł gry
        title = self.font_large.render("ICY TOWER", True, self.title_color)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)
        
        # Podtytuł
        subtitle = self.font_medium.render("Select Difficulty", True, COLORS['WHITE'])
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 60))
        screen.blit(subtitle, subtitle_rect)
        
        # Opcje trudności
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.unselected_color
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
            screen.blit(text, text_rect)
        
        # Instrukcja
        instruction = self.font_medium.render("Press ENTER to start", True, COLORS['WHITE'])
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT * 4 // 5))
        screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return False, self.options[self.selected_option]
        return True, None

def game_loop(difficulty):
    clock = pygame.time.Clock()
    player = Player()
    
    # Stwórz platformę startową na całą szerokość
    starting_platform = Platform(0, HEIGHT - 100, WIDTH, 0)
    starting_platform.color = (50, 50, 100)  # Ciemnoniebieski kolor dla platformy startowej
    
    # Generuj początkowe platformy
    platforms = generate_platforms(30, HEIGHT - 150)
    platforms.insert(0, starting_platform)  # Dodaj platformę startową jako pierwszą
    
    # Ustawienia lawy
    difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
    lava = Lava(difficulty_settings["lava_start"])
    lava.rise_speed = difficulty_settings["lava_speed"]
    
    camera_y = 0
    target_camera_y = 0
    
    score = 0
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    large_font = pygame.font.SysFont(None, 72)
    game_over = False
    paused = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    return True
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    return True
        
        if not game_over and not paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.vel_x = -player.speed
            if keys[pygame.K_RIGHT]:
                player.vel_x = player.speed
            if keys[pygame.K_SPACE]:
                player.jump()
            if keys[pygame.K_UP]:
                player.activate_hyper_jump()
            
            if player.y < camera_y + HEIGHT * CAMERA_FOLLOW_HEIGHT:
                target_camera_y = player.y - HEIGHT * CAMERA_FOLLOW_HEIGHT
            
            camera_y += (target_camera_y - camera_y) * CAMERA_SPEED
            
            # Aktywuj lawę po pierwszym skoku
            if player.first_jump_made and difficulty != "No Lava":
                lava.active = True
            
            for platform in platforms:
                platform.update()
            
            lava.update()
            
            for platform in platforms:
                platform.check_coin_collection(player)
            
            alive = player.update(platforms, camera_y, lava.height)
            if not alive:
                game_over = True
            
            # Usuń platformy poza ekranem
            platforms = [p for p in platforms if p.y > camera_y - 100 and p.y < camera_y + HEIGHT + 200]
            
            # Generuj nowe platformy jeśli potrzeba
            if len(platforms) < 30:  
                new_platforms_needed = 30 - len(platforms)
                if platforms:
                    highest_platform = min(platforms, key=lambda p: p.y)
                    region = REGIONS[player.current_region]
                    start_y = highest_platform.y - region["gap_y"]  
                    new_platforms = generate_platforms(new_platforms_needed, 
                                                    start_y, 
                                                    player.current_region)
                    platforms.extend(new_platforms)
            
            score = player.score
        
        screen.fill(COLORS['BLACK'])
        
        # Proste ustawienie koloru tła na podstawie aktualnego regionu
        current_region = player.current_region
        bg_color = REGIONS[current_region]["color"]
        screen.fill(bg_color)
        
        for platform in platforms:
            platform.draw(camera_y)
        
        lava.draw(camera_y)
        player.draw(camera_y)
        
        # Wyświetlanie informacji o poziomie trudności
        score_text = font.render(f"Score: {score}", True, COLORS['WHITE'])
        screen.blit(score_text, (10, 10))
        
        difficulty_text = small_font.render(f"Difficulty: {difficulty}", True, COLORS['WHITE'])
        screen.blit(difficulty_text, (WIDTH - difficulty_text.get_width() - 10, 40))
        
        region_name = REGIONS[player.current_region]["name"]
        region_text = small_font.render(f"Region: {region_name}", True, COLORS['WHITE'])
        screen.blit(region_text, (10, 40))  # Przesunięte niżej
        
        # Pasek energii do hyper skoku
        coin_bar_width = 150
        coin_bar_height = 15
        coin_bar_x = 10
        coin_bar_y = 90  # Przesunięte wyżej
        
        pygame.draw.rect(screen, (200, 200, 200), (coin_bar_x, coin_bar_y, coin_bar_width, coin_bar_height))
        
        fill_width = int((player.coins / player.max_coins) * coin_bar_width)
        if fill_width > 0:
            for i in range(fill_width):
                ratio = i / coin_bar_width
                if ratio < 0.5:
                    r = int(255 * (ratio * 2))
                    g = 255
                    b = 0
                else:
                    r = 255
                    g = int(255 * (1 - (ratio - 0.5) * 2))
                    b = 0
                
                pygame.draw.line(screen, (r, g, b), 
                                 (coin_bar_x + i, coin_bar_y), 
                                 (coin_bar_x + i, coin_bar_y + coin_bar_height))
        
        pygame.draw.rect(screen, (255, 255, 255), (coin_bar_x, coin_bar_y, coin_bar_width, coin_bar_height), 1)
        
        coin_text = small_font.render("Hyper Jump Energy", True, COLORS['WHITE'])
        screen.blit(coin_text, (coin_bar_x, coin_bar_y - 20))
        
        if player.hyper_jump_active:
            active_text = small_font.render("HYPER JUMP READY!", True, COLORS['PURPLE'])
            screen.blit(active_text, (WIDTH - active_text.get_width() - 10, 10))
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("GAME OVER", True, COLORS['RED'])
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
            
            score_big_text = large_font.render(f"SCORE: {score}", True, COLORS['WHITE'])
            screen.blit(score_big_text, (WIDTH // 2 - score_big_text.get_width() // 2, HEIGHT // 2 - 20))
            
            restart_text = font.render("Press R to Restart", True, COLORS['WHITE'])
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
        
        if paused and not game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            paused_text = large_font.render("PAUSED", True, COLORS['WHITE'])
            screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 50))
            
            resume_text = font.render("Press P to Resume", True, COLORS['WHITE'])
            screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    return False

def main():
    menu = Menu()
    running = True
    
    while running:
        menu_active = True
        while menu_active:
            menu_active, selected_difficulty = menu.handle_input()
            if not menu_active and selected_difficulty is None:
                pygame.quit()
                sys.exit()
            menu.draw()
            
        if selected_difficulty:
            restart = game_loop(selected_difficulty)
            if not restart:
                running = False

if __name__ == "__main__":
    main() 