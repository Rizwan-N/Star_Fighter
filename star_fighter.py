import pygame
import random
import sys
import os
import math

# Init
pygame.init()
pygame.mixer.init()
GAME_OVER_CHANNEL = pygame.mixer.Channel(0)

# Global Variables
SCREEN = None
GAME_SURFACE = None
IS_FULLSCREEN = False
SCALE_FACTOR = 1.0
OFFSET_X = 0
OFFSET_Y = 0
GAME_OVER_SOUND = None
DEBUG_PRINT = False
fullscreen_debounce_timer = 0
FULLSCREEN_DEBOUNCE_DELAY = 500  # milliseconds

# Screen
WIDTH, HEIGHT = 600, 900
GAME_SURFACE = pygame.Surface((WIDTH, HEIGHT))
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Fighter")

# Background music setup
def load_music(file_path):
    try:
        pygame.mixer.music.load(file_path)
    except pygame.error:
        pass

def play_menu_music():
    global is_menu_music_playing
    if not is_menu_music_playing:
        try:
            # Stop game over sound and music
            if GAME_OVER_SOUND:
                GAME_OVER_SOUND.stop()
            pygame.mixer.music.stop()
            load_music("assets/main_menu.mp3")
            pygame.mixer.music.play(-1)
            is_menu_music_playing = True
        except pygame.error as e:
            if DEBUG_PRINT:
                print(f"Error playing menu music: {e}")
            is_menu_music_playing = False

def play_game_music():
    global is_menu_music_playing
    try:
        # Stop game over sound and music
        if GAME_OVER_SOUND:
            GAME_OVER_SOUND.stop()
        pygame.mixer.music.fadeout(500)
        load_music("assets/game_music.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        is_menu_music_playing = False
    except pygame.error as e:
        if DEBUG_PRINT:
            print(f"Error playing game music: {e}")

# Function to calculate scaling and offsets for centering
def update_fullscreen_scaling():
    global SCALE_FACTOR, OFFSET_X, OFFSET_Y
    if IS_FULLSCREEN:
        # Get the monitor's resolution
        display_info = pygame.display.Info()
        screen_width, screen_height = display_info.current_w, display_info.current_h
        
        # Ensure non-zero dimensions
        screen_width = max(1, screen_width)
        screen_height = max(1, screen_height)
        
        # Calculate scaling factor to fit game within screen while preserving aspect ratio
        scale_x = screen_width / WIDTH
        scale_y = screen_height / HEIGHT
        SCALE_FACTOR = min(scale_x, scale_y)
        
        # Ensure scale factor is positive
        SCALE_FACTOR = max(0.1, SCALE_FACTOR)
        
        # Calculate the scaled game dimensions
        scaled_width = int(WIDTH * SCALE_FACTOR)
        scaled_height = int(HEIGHT * SCALE_FACTOR)
        
        # Calculate offsets to center the game
        OFFSET_X = (screen_width - scaled_width) // 2
        OFFSET_Y = (screen_height - scaled_height) // 2
    else:
        # Reset for windowed mode
        SCALE_FACTOR = 1.0
        OFFSET_X = 0
        OFFSET_Y = 0
    
    if DEBUG_PRINT:
        print(f"Scaling: IS_FULLSCREEN={IS_FULLSCREEN}, SCALE_FACTOR={SCALE_FACTOR}, OFFSET_X={OFFSET_X}, OFFSET_Y={OFFSET_Y}")

def toggle_fullscreen():
    global fullscreen_debounce_timer, IS_FULLSCREEN, SCREEN, SCALE_FACTOR, OFFSET_X, OFFSET_Y
    current_time = pygame.time.get_ticks()
    
    # Allow toggle only if enough time has passed since last toggle
    if fullscreen_debounce_timer == 0 or (current_time - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
        IS_FULLSCREEN = not IS_FULLSCREEN
        try:
            if IS_FULLSCREEN:
                # Switch to fullscreen using the native resolution
                SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                # Switch to windowed mode with fixed resolution
                SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            # Update scaling parameters
            update_fullscreen_scaling()
            # Force display update
            render_game()
            # Reset debounce timer
            fullscreen_debounce_timer = current_time
            if DEBUG_PRINT:
                print(f"Toggled fullscreen: IS_FULLSCREEN={IS_FULLSCREEN}")
        except pygame.error as e:
            # Handle display mode errors
            print(f"Error toggling fullscreen: {e}")
            IS_FULLSCREEN = not IS_FULLSCREEN  # Revert state on failure
            SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            update_fullscreen_scaling()
            render_game()
            fullscreen_debounce_timer = current_time

# Function to render the game surface to the screen
def render_game():
    # Scale and blit the GAME_SURFACE to the SCREEN with centering
    if IS_FULLSCREEN:
        scaled_surface = pygame.transform.scale(GAME_SURFACE, (int(WIDTH * SCALE_FACTOR), int(HEIGHT * SCALE_FACTOR)))
        SCREEN.fill(BLACK)  # Clear screen with black (letterboxes)
        SCREEN.blit(scaled_surface, (OFFSET_X, OFFSET_Y))
    else:
        SCREEN.blit(GAME_SURFACE, (0, 0))
    pygame.display.flip()

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)

# Load sound and image
def load_image(path, fallback_color=BLACK, size=(50, 50)):
    try:
        return pygame.image.load(path)
    except pygame.error:
        surf = pygame.Surface(size)
        surf.fill(fallback_color)
        return surf

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None

# FPS
FPS = 60
clock = pygame.time.Clock()

# Cached surfaces
font = pygame.font.SysFont("arial", 24)
MUZZLE_FLASH_SURFACE = pygame.Surface((10, 10), pygame.SRCALPHA)
pygame.draw.circle(MUZZLE_FLASH_SURFACE, MAGENTA, (5, 5), 5)
TRAIL_SURFACE = pygame.Surface((6, 6), pygame.SRCALPHA)
pygame.draw.circle(TRAIL_SURFACE, (255, 50, 50, 255), (3, 3), 3)
SHIELD_SURFACE = pygame.Surface((80, 80), pygame.SRCALPHA)
pygame.draw.circle(SHIELD_SURFACE, (0, 0, 255, 64), (40, 40), 40)
ARTILLERY_SHELL_SURFACE = pygame.Surface((10, 10), pygame.SRCALPHA)
pygame.draw.circle(ARTILLERY_SHELL_SURFACE, ORANGE, (5, 5), 5)
ARTILLERY_EXPLOSION_SURFACE = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(ARTILLERY_EXPLOSION_SURFACE, (255, 50, 50, 128), (50, 50), 50)
SNIPER_BULLET_SURFACE = pygame.Surface((10, 144), pygame.SRCALPHA)
pygame.draw.rect(SNIPER_BULLET_SURFACE, (255, 50, 50, 120), (0, 0, 10, 144))
pygame.draw.rect(SNIPER_BULLET_SURFACE, RED, (3, 24, 4, 96))
pygame.draw.rect(SNIPER_BULLET_SURFACE, WHITE, (4, 26, 2, 92))

# Load assets
PLAYER_IMGS = [load_image(f"assets/player{i}.png", RED) for i in range(1, 5)]
BULLET_IMG = load_image("assets/bullet.png")
ENEMY_IMGS = [load_image(f"assets/enemy{i}.png", RED) for i in range(1, 8)]
BOSS_IMGS = [load_image(f"assets/boss{i}.png", RED) for i in range(1, 9)]
BACKGROUNDS = [load_image(f"assets/background{i}.png", BLACK, (WIDTH, HEIGHT)) for i in range(1, 11)] or [pygame.Surface((WIDTH, HEIGHT)).fill(BLACK)]
START_SCREEN = load_image("assets/start_screen.png")
MAIN_MENU_IMG = load_image("assets/main_menu.png")
HIGH_SCORES_IMG = load_image("assets/high_scores.png")
CONTROLS_IMG = load_image("assets/controls.png")
ABOUT_IMG = load_image("assets/about.png", BLACK, (WIDTH, HEIGHT))
SELECT_SHIP_IMG = load_image("assets/select_ship.png")
LOADING_SCREEN = load_image("assets/loading_screen.png")
ASTEROID_IMG = load_image("assets/asteroid.png")
HEALTH_PACK_IMG = load_image("assets/health_pack.png")
POWERUP_IMG = load_image("assets/powerup.png")
SHIELD_IMG = load_image("assets/shield_powerup.png")
MISSILE_POWERUP_IMG = load_image("assets/missile_powerup.png")
MISSILE_IMG = load_image("assets/missile.png")
HEART_IMG = load_image("assets/heart.png")
GAME_OVER_IMG = load_image("assets/game_over.png")
GAME_PAUSED_IMG = load_image("assets/game_paused.png")
DOUBLE_ICON = pygame.transform.scale(load_image("assets/powerup.png"), (24, 24))
SHIELD_ICON = pygame.transform.scale(load_image("assets/shield_powerup.png"), (24, 24))
MISSILE_ICON = pygame.transform.scale(load_image("assets/missile_powerup.png"), (24, 24))
SPEED_POWERUP_IMG = load_image("assets/speed_powerup.png")
SPEED_ICON = pygame.transform.scale(load_image("assets/speed_powerup.png"), (24, 24))
BOMB_POWERUP_IMG = load_image("assets/bomb_powerup.png")
BOMB_ICON = pygame.transform.scale(load_image("assets/bomb_powerup.png"), (24, 24))

# Load sounds
SHOOT_SOUND = load_sound("assets/shoot.wav")
ASTEROID_COLLISION_SOUND = load_sound("assets/asteroid_collision.wav")
EXPLOSION_SOUND = load_sound("assets/explosion.wav")
BOMB_EXPLOSION_SOUND = load_sound("assets/bomb_explosion.wav")
PLAYER_EXPLOSION_SOUND = load_sound("assets/player_explosion.wav")
BOSS_EXPLOSION_SOUND = load_sound("assets/boss_explosion.wav")
BOSS_SHOOT_SOUND = load_sound("assets/boss_shoot.wav")
ENEMY_BOMB_SOUND = load_sound("assets/enemy_bomb.wav")
SNIPER_LASER_SOUND = load_sound("assets/sniper_shoot.wav")
FIGHTER_SHOOT_SOUND = load_sound("assets/fighter_shoot.wav")
LEECH_TETHER_SOUND = load_sound("assets/leech_tether.wav")
ARTILLERY_SHOT_SOUND = load_sound("assets/artillery_shot.wav")
MISSILE_SHOT_SOUND = load_sound("assets/missile_shot.wav")
POWERUP_COLLECT_SOUND = load_sound("assets/powerup_collect.wav")
HEALTH_PACK_COLLECT_SOUND = load_sound("assets/health_pack_collect.wav")
GAME_OVER_SOUND = load_sound("assets/game_over.mp3")
PLAYER_COLLISION_SOUND = load_sound("assets/player_collision.wav")

# Precompute sin table for enemy movement
SIN_TABLE = [math.sin(i * 0.05) * 3 for i in range(360)]

# Background scroll
bg_y = 0

# Game variables
missile_hits_tracker = {}
BG = None
score = 0
level = 1
wave = 1
max_waves = 6
enemies_per_wave = 2
base_enemies = 4
enemies_spawned = 0
boss_spawned = False
spawn_timer = 0
SPAWN_DELAY = 30
powerup_timer = 0
missile_timer = 0
game_started = False
DOUBLE_SHOT_DURATION = 900
SHIELD_DURATION = 900
MISSILE_DURATION = 900
level_transition_delay = False
delay_timer = 0
selected_ship = None
debug_mode = False
fps_debug = False
last_score = -1
last_level = -1
score_text = None
level_text = None
last_frame_time = 0
is_menu_music_playing = False
bomb_flash_timer = 0
asteroid_spawn_timer = 0
ASTEROID_SPAWN_DELAY = 90  # Spawn every 1.5 seconds at 60 FPS
max_asteroids = 0  # Will be set based on level

# Utility functions
def fade_screen(color=(0, 0, 0)):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(color)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        GAME_SURFACE.blit(fade_surface, (0, 0))
        render_game()
        pygame.time.delay(10)

def draw_health_bar(surface, x, y, current_health, max_health):
    bar_width = 150
    bar_height = 20
    fill = (current_health / max_health) * bar_width
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, RED, outline_rect, 2)
    pygame.draw.rect(surface, GREEN, fill_rect)

def draw_timer_bar(surface, x, y, timer, max_timer, color):
    bar_width = 100
    bar_height = 10
    fill = (timer / max_timer) * bar_width
    pygame.draw.rect(surface, color, (x, y, fill, bar_height))
    pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)

def draw_debug_info():
    if not debug_mode:
        return
    debug_texts = [
        (f"Player Health: {player.health}", None),
        (f"Player Lives: {player.lives}", None),
        (f"Player Invincible: {player.invincible}", None),
        (f"Player Shield: {player.shield}", None),
        (f"Player Missile Shot: {player.missile_shot}", None),
        (f"Player Speed Boost: {player.speed_boost}", None),
        (f"Player Tethered: {player.is_tethered}", None),
        (f"Player Bomb Count: {player.bomb_count}", None),
        (f"Boss Health: {boss_group.sprites()[0].health if boss_group else 'N/A'}", None),
        (f"Wave: {wave}/{max_waves}, Level: {level}", None),
        (f"Enemies Spawned: {enemies_spawned}/{enemies_per_wave}", None),
        (f"Boss Spawned: {boss_spawned}", None),
        (f"Level Transition Delay: {level_transition_delay}", None),
        (f"Delay Timer: {delay_timer}", None),
        (f"Bullets: {len(bullets)}", None),
        (f"Missiles: {len(missiles)}", None),
        (f"Boss Bullets: {len(boss_bullets)}", None),
        (f"Enemy Bullets: {len(enemy_bullets)}", None),
        (f"Bombs: {len(bombs)}", None),
        (f"Artillery Shells: {len(artillery_shells)}", None),
        (f"Speed Power-ups: {len(speed_powerups)}", None),
        (f"Bomb Power-ups: {len(bomb_powerups)}", None)
    ]
    for i, (text, cached) in enumerate(debug_texts):
        if not cached:
            cached = font.render(text, True, YELLOW)
            debug_texts[i] = (text, cached)
        GAME_SURFACE.blit(cached, (10, 160 + i * 30))

def draw_fps_info():
    if not fps_debug:
        return
    frame_time = pygame.time.get_ticks() - last_frame_time
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {fps:.1f} Frame Time: {frame_time:.1f}ms", True, YELLOW)
    GAME_SURFACE.blit(fps_text, (10, 130))

# Start screen
def start_screen():
    global fullscreen_debounce_timer
    play_menu_music()
    while True:
        clock.tick(FPS)
        GAME_SURFACE.blit(START_SCREEN, ((WIDTH - START_SCREEN.get_width()) // 2, (HEIGHT - START_SCREEN.get_height()) // 2))
        render_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_RETURN: # Changed from any key to Enter for consistency
                    fade_screen()
                    return

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, ship_image):
        super().__init__()
        self.image = ship_image
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 60))
        self.base_speed = 7
        self.speed = self.base_speed
        self.speed_boost = False
        self.speed_timer = 0
        self.SPEED_DURATION = 900
        self.health = 100
        self.double_shot = False
        self.shield = False
        self.missile_shot = False
        self.shield_timer = 0
        self.missile_timer = 0
        self.lives = 3
        self.invincible = False
        self.invincibility_timer = 0
        self.INVINCIBILITY_DURATION = 180
        self.blink_timer = 0
        self.visible = True
        self.shoot_timer = 0
        self.missile_shoot_timer = 0
        self.SHOOT_DELAY = 10
        self.MISSILE_SHOOT_DELAY = 20
        self.is_tethered = False
        self.tether_timer = 0
        self.bomb_count = 0
        self.MAX_BOMBS = 9
        self.bomb_cooldown = 0
        self.BOMB_COOLDOWN_DURATION = 20

    def update(self, keys):
        if self.is_tethered:
            self.tether_timer -= 1
            if self.tether_timer <= 0:
                self.is_tethered = False
        effective_speed = self.speed * 0.5 if self.is_tethered else self.speed

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= effective_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += effective_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= effective_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += effective_speed

        if self.invincible:
            self.invincibility_timer -= 1
            self.blink_timer += 1
            if self.blink_timer >= 20:
                self.visible = not self.visible
                self.blink_timer = 0
            if self.invincibility_timer <= 0:
                self.invincible = False
                self.visible = True

        if keys[pygame.K_SPACE]:
            self.shoot_timer += 1
            if self.shoot_timer >= self.SHOOT_DELAY:
                self.shoot(mash=False)
                self.shoot_timer = 0
        else:
            self.shoot_timer = 0

        if keys[pygame.K_m]:
            if self.missile_shot:
                self.missile_shoot_timer += 1
                if self.missile_shoot_timer >= self.MISSILE_SHOOT_DELAY:
                    self.shoot_missile()
                    self.missile_shoot_timer = 0
        else:
            self.missile_shoot_timer = 0

        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
        if keys[pygame.K_b] and self.bomb_count > 0 and self.bomb_cooldown == 0:
            self.use_bomb()
            self.bomb_cooldown = self.BOMB_COOLDOWN_DURATION

    def shoot(self, mash=False):
        damage = 15 if mash else 10
        if self.double_shot:
            bullets.add(Bullet(self.rect.centerx - 10, self.rect.top, damage))
            bullets.add(Bullet(self.rect.centerx + 10, self.rect.top, damage))
        else:
            bullets.add(Bullet(self.rect.centerx, self.rect.top, damage))
        SHOOT_SOUND.play()

    def shoot_missile(self):
        missiles.add(Missile(self.rect.centerx, self.rect.top))
        MISSILE_SHOT_SOUND.play()

    def use_bomb(self):
        global score, bomb_flash_timer, wave, level_transition_delay, delay_timer
        if self.bomb_count > 0:
            self.bomb_count -= 1
            bomb_flash_timer = 10
            if BOMB_EXPLOSION_SOUND:
                BOMB_EXPLOSION_SOUND.play()
            # Play EXPLOSION_SOUND for each asteroid destroyed
            for asteroid in asteroids:
                if EXPLOSION_SOUND:
                    EXPLOSION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Asteroid destroyed by bomb, playing explosion.wav")
            for enemy in enemies:
                if enemy.health <= 20:
                    score += enemy.score_value
                    enemy.kill()
                    if enemy.is_leech and enemy.tethered_enemy:
                        enemy.tethered_enemy.is_tethered = False
                else:
                    enemy.health -= 50
                    if enemy.health <= 0:
                        score += enemy.score_value
                        enemy.kill()
                        if enemy.is_leech and enemy.tethered_enemy:
                            enemy.tethered_enemy.is_tethered = False
            for boss in boss_group:
                boss.health -= 100
                if boss.health <= 0:
                    score += int(250 * (1.25 ** (level - 1)))
                    boss.kill()
                    if BOSS_EXPLOSION_SOUND:
                        BOSS_EXPLOSION_SOUND.play()
                    wave += 1
                    level_transition_delay = True
                    delay_timer = 180
            enemy_bullets.empty()
            bombs.empty()
            artillery_shells.empty()
            asteroids.empty()

    def reset(self):
        self.rect.center = (WIDTH//2, HEIGHT - 60)
        self.health = 100
        self.double_shot = False
        self.shield = False
        self.missile_shot = False
        self.speed_boost = False
        self.speed = self.base_speed
        self.shield_timer = 0
        self.missile_timer = 0
        self.speed_timer = 0
        self.invincible = True
        self.invincibility_timer = self.INVINCIBILITY_DURATION
        self.visible = True
        self.shoot_timer = 0
        self.missile_shoot_timer = 0
        self.is_tethered = False
        self.tether_timer = 0
        self.bomb_count = 0
        self.bomb_cooldown = 0

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect)
            if self.shield:
                shield_pos = (self.rect.centerx - SHIELD_SURFACE.get_width() // 2,
                              self.rect.centery - SHIELD_SURFACE.get_height() // 2)
                surface.blit(SHIELD_SURFACE, shield_pos)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=10):
        super().__init__()
        self.image = BULLET_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10
        self.damage = damage

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = MISSILE_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.damage = 20  # Used only for bosses
        self.target = None
        # Find initial closest target (enemy, boss, or asteroid)
        targets = list(enemies) + list(boss_group) + list(asteroids)
        if targets:
            self.target = min(targets, key=lambda t: ((self.rect.x - t.rect.x) ** 2 + (self.rect.y - t.rect.y) ** 2) ** 0.5, default=None)

    def update(self):
        if not self.target or not self.target.alive():
            # Find new closest target
            targets = list(enemies) + list(boss_group) + list(asteroids)
            if targets:
                self.target = min(targets, key=lambda t: ((self.rect.x - t.rect.x) ** 2 + (self.rect.y - t.rect.y) ** 2) ** 0.5, default=None)
            else:
                self.target = None

        if self.target:
            # Calculate direction to target
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > 0:
                # Move toward target at constant speed
                self.rect.x += (dx / dist) * self.speed
                self.rect.y += (dy / dist) * self.speed
        else:
            # Move straight up if no target
            self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 7
        self.angle = angle
        self.vx = self.speed * math.sin(math.radians(self.angle))
        self.vy = self.speed * math.cos(math.radians(self.angle))

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.top > HEIGHT or self.rect.bottom < 0 or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color=YELLOW, angle=90, speed=5, width=5, height=10, damage=10):
        super().__init__()
        self.is_sniper_bullet = (color == RED)
        if self.is_sniper_bullet:
            self.image = SNIPER_BULLET_SURFACE
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.angle = angle
        self.damage = damage
        self.vx = self.speed * math.cos(math.radians(self.angle))
        self.vy = self.speed * math.sin(math.radians(self.angle))
        self.trail = []
        self.last_pos = (x, y)

    def update(self):
        if self.rect.top > HEIGHT or self.rect.bottom < 0 or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()
            return
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.is_sniper_bullet:
            dist = ((self.rect.centerx - self.last_pos[0]) ** 2 + (self.rect.centery - self.last_pos[1]) ** 2) ** 0.5
            if dist >= 4:
                self.trail.append((self.rect.centerx, self.rect.centery, 255))
                self.last_pos = (self.rect.centerx, self.rect.centery)
            self.trail = [(x, y, max(0, a - 50)) for x, y, a in self.trail if a > 0]
            if len(self.trail) > 6:
                self.trail.pop(0)

    def draw(self, surface):
        if self.rect.top > HEIGHT or self.rect.bottom < 0 or self.rect.left > WIDTH or self.rect.right < 0:
            return
        surface.blit(self.image, self.rect)
        if self.is_sniper_bullet:
            for x, y, alpha in self.trail:
                TRAIL_SURFACE.set_alpha(alpha)
                surface.blit(TRAIL_SURFACE, (x - 3, y - 3))

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, color=RED):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        angle_rad = math.radians(angle)
        self.vx = self.speed * math.sin(angle_rad)
        self.vy = self.speed * math.cos(angle_rad)
        self.damage = 15

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.top > HEIGHT:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ASTEROID_IMG
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), -40))
        self.health = 3
        self.speed = random.uniform(4, 8)  # Increased speed range
        self.angle = random.uniform(45, 135)  # Narrower angle range (downward)
        self.vx = self.speed * math.cos(math.radians(self.angle))
        self.vy = self.speed * math.sin(math.radians(self.angle))
        self.damage = 15

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.top > HEIGHT + 40 or self.rect.bottom < -40 or self.rect.left > WIDTH + 40 or self.rect.right < -40:
            self.kill()

class ArtilleryShell(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = ARTILLERY_SHELL_SURFACE
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        self.start_pos = (x, y)
        self.max_distance = 400
        self.damage = 20
        self.blast_radius = 50
        self.explosion_timer = 0
        self.exploded = False
        dx = target_x - x
        dy = target_y - y
        distance = max(1, (dx**2 + dy**2)**0.5)
        self.vx = self.speed * dx / distance
        self.vy = self.speed * dy / distance

    def update(self):
        if self.exploded:
            self.explosion_timer -= 1
            if self.explosion_timer > 0:
                blast_rect = pygame.Rect(self.rect.centerx - self.blast_radius, self.rect.centery - self.blast_radius, self.blast_radius * 2, self.blast_radius * 2)
                if blast_rect.collidepoint(player.rect.center) and not player.shield and not player.invincible:
                    distance = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)**0.5
                    if distance <= self.blast_radius:
                        player.health -= 10
            if self.explosion_timer <= 0:
                self.kill()
            return
        self.rect.x += self.vx
        self.rect.y += self.vy
        distance_traveled = ((self.rect.centerx - self.start_pos[0])**2 + (self.rect.centery - self.start_pos[1])**2)**0.5
        if distance_traveled >= self.max_distance or self.rect.top > HEIGHT:
            self.explode()

    def explode(self):
        if not self.exploded:
            self.exploded = True
            self.explosion_timer = 10
            EXPLOSION_SOUND.play()

    def draw(self, surface):
        if self.exploded:
            if self.explosion_timer > 0:
                alpha = int(128 * (self.explosion_timer / 10))
                ARTILLERY_EXPLOSION_SURFACE.set_alpha(alpha)
                surface.blit(ARTILLERY_EXPLOSION_SURFACE, (self.rect.centerx - 50, self.rect.centery - 50))
        else:
            surface.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        enemy_types = [
            (ENEMY_IMGS[0], (4, 7), 10, 1.0, False, False, False, 10, 1),
            (ENEMY_IMGS[1], (2, 5), 20, 1.0, True, False, False, 10, 1),
            (ENEMY_IMGS[2], (1, 3), 30, 1.0, True, True, False, 20, 2),
            (ENEMY_IMGS[3], (1, 3), 40, 1.0, True, False, True, 15, 3),
            (ENEMY_IMGS[4], (2, 4), 20, 1.0, True, False, False, 15, 4),
            (ENEMY_IMGS[5], (3, 6), 20, 1.0, True, False, False, 15, 5),
            (ENEMY_IMGS[6], (0, 0), 50, 1.0, True, False, False, 20, 6)
        ]
        available_types = [t for t in enemy_types if t[8] <= level] or [enemy_types[0], enemy_types[1]]
        weight_map = {1: 0.25, 2: 0.2, 3: 0.15, 4: 0.1, 5: 0.05}
        weights = [weight_map.get(t[8], 0.05) for t in available_types]
        weight_sum = sum(weights)
        weights = [w / weight_sum if weight_sum > 0 else 1.0 / len(weights) for w in weights]
        self.type_data = random.choices(available_types, weights=weights, k=1)[0]
        self.image = self.type_data[0]
        self.original_image = self.image.copy()
        if self.type_data[0] == ENEMY_IMGS[6]:
            self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), 100))
            self.base_speed = 0
        else:
            self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), -40))
            self.base_speed = random.randint(self.type_data[1][0], self.type_data[1][1]) + level // 2
        self.speed = self.base_speed
        self.health = round(self.type_data[2] * (1.0 + (level - self.type_data[8]) * 0.1))
        self.can_shoot = self.type_data[4]
        self.is_tank = self.type_data[5]
        self.is_bomber = self.type_data[6]
        self.is_sniper = self.type_data[0] == ENEMY_IMGS[4]
        self.is_leech = self.type_data[0] == ENEMY_IMGS[5]
        self.is_artillery = self.type_data[0] == ENEMY_IMGS[6]
        self.score_value = self.type_data[7]
        self.is_shooting = False
        self.shooting_pause_timer = 0
        self.timer = 0
        self.muzzle_flash_timer = 0
        if self.is_leech:
            self.tethered_enemy = None
            self.shoot_timer = 0
            self.shoot_delay = 120
            self.pulse_timer = 0
            self.pulse_scale = 1.0
        elif self.is_artillery:
            self.shoot_timer = 0
            self.shoot_delay = 300
        elif self.can_shoot or self.is_sniper:
            self.shoot_timer = 0
            self.shoot_delay = 150 if self.is_sniper else 180 if self.is_bomber else 120
        if self.is_sniper:
            self.aim_timer = 0
            self.recoil_timer = 0
            self.shoot_pause_timer = 0
            self.flash_timer = 0

    def update(self):
        if self.rect.top > HEIGHT + 40 or self.rect.bottom < -40:
            if self.rect.bottom > HEIGHT and not self.is_artillery:
                self.kill()
            return
        self.timer = (self.timer + 1) % 360
        if self.is_leech:
            self.rect.x += SIN_TABLE[self.timer] * 5
            if self.rect.left < 20:
                self.rect.left = 20
            if self.rect.right > WIDTH - 20:
                self.rect.right = WIDTH - 20
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_delay:
                dist = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)**0.5
                if dist <= 200 and not player.is_tethered:
                    player.is_tethered = True
                    player.tether_timer = 180
                    self.tethered_enemy = player
                    self.shoot_timer = 0
                    if self.tethered_enemy is player and not hasattr(self, 'tether_sound_played'):
                        LEECH_TETHER_SOUND.play()
                        self.tether_sound_played = True
            self.pulse_timer += 1
            if self.pulse_timer >= 10:
                self.pulse_timer = 0
            self.pulse_scale = 1.0 + 0.05 * math.sin(self.pulse_timer * 0.628)
            new_size = (int(self.original_image.get_width() * self.pulse_scale), 
                       int(self.original_image.get_height() * self.pulse_scale))
            self.image = pygame.transform.scale(self.original_image, new_size)
            self.rect = self.image.get_rect(center=self.rect.center)
        elif self.is_sniper:
            if self.aim_timer > 0:
                self.speed = 0
                self.aim_timer -= 1
                self.flash_timer += 1
                if self.flash_timer % 5 == 0:
                    alpha = 128 if self.image.get_alpha() == 255 else 255
                    self.image = self.original_image.copy()
                    self.image.set_alpha(alpha)
                if self.aim_timer == 0:
                    self.recoil_timer = 1
                    self.image = self.original_image.copy()
                    self.image.set_alpha(255)
            elif self.recoil_timer > 0:
                self.speed = 0
                if self.rect.top > -80:
                    self.rect.y -= 20
                self.recoil_timer += 1
                if self.recoil_timer > 4:
                    self.recoil_timer = 0
                    self.shoot_pause_timer = 2
            elif self.shoot_pause_timer > 0:
                self.speed = 0
                self.shoot_pause_timer -= 1
                if self.shoot_pause_timer <= 0:
                    bullet_height = max(1, HEIGHT - (self.rect.bottom - 20))
                    enemy_bullets.add(EnemyBullet(
                        self.rect.centerx, self.rect.bottom - 20,
                        color=RED, angle=90, speed=10,
                        width=4, height=96, damage=15
                    ))
                    SNIPER_LASER_SOUND.play()
                    self.is_shooting = True
                    self.shooting_pause_timer = 30
                    self.muzzle_flash_timer = 3
            elif self.is_shooting and self.shooting_pause_timer > 0:
                self.speed = 0
                self.shooting_pause_timer -= 1
                if self.shooting_pause_timer <= 0:
                    self.is_shooting = False
                    self.speed = self.base_speed
            else:
                self.speed = self.base_speed
                self.rect.x += SIN_TABLE[self.timer]
                if self.rect.left < 20:
                    self.rect.left = 20
                if self.rect.right > WIDTH - 20:
                    self.rect.right = WIDTH - 20
        elif self.is_artillery:
            self.speed = 0
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_delay:
                self.shoot()
                self.shoot_timer = 0
        else:
            self.speed = self.base_speed

        if self.can_shoot and not self.is_leech and not self.is_artillery:
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_delay:
                self.shoot()
                self.shoot_timer = 0
                self.shoot_delay = 150 if self.is_sniper else 180 if self.is_bomber else 120
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= 1

        self.rect.y += self.speed

    def draw(self, surface):
        if self.rect.top > HEIGHT or self.rect.bottom < 0:
            return
        surface.blit(self.image, self.rect)
        if self.is_leech and self.tethered_enemy:
            pygame.draw.line(surface, PURPLE, self.rect.center, self.tethered_enemy.rect.center, 2)
        if self.muzzle_flash_timer > 0:
            surface.blit(MUZZLE_FLASH_SURFACE, (self.rect.centerx - 5, self.rect.bottom - 5))

    def shoot(self):
        if self.is_sniper:
            if self.aim_timer == 0 and self.recoil_timer == 0 and self.shoot_pause_timer == 0 and not self.is_shooting:
                self.aim_timer = 30
        elif self.is_bomber:
            angles = [-30, 0, 30]
            for angle in angles:
                bombs.add(Bomb(self.rect.centerx, self.rect.bottom, angle, MAGENTA))
            ENEMY_BOMB_SOUND.play()
            self.muzzle_flash_timer = 3
        elif self.is_tank:
            bombs.add(Bomb(self.rect.centerx, self.rect.bottom, color=ORANGE))
            ENEMY_BOMB_SOUND.play()
        elif self.is_artillery:
            artillery_shells.add(ArtilleryShell(self.rect.centerx, self.rect.bottom, player.rect.centerx, player.rect.centery))
            ARTILLERY_SHOT_SOUND.play()
            self.muzzle_flash_timer = 3
        elif self.type_data[0] == ENEMY_IMGS[1]:
            enemy_bullets.add(EnemyBullet(self.rect.centerx, self.rect.bottom, YELLOW, 90, 5))
            FIGHTER_SHOOT_SOUND.play()
        else:
            enemy_bullets.add(EnemyBullet(self.rect.centerx, self.rect.bottom, YELLOW, 90, 5))
            ENEMY_BOMB_SOUND.play()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(BOSS_IMGS)
        self.rect = self.image.get_rect(center=(WIDTH // 2, -150))
        self.speed_y = 2
        self.health = 300 + level * 75
        self.max_health = 300 + level * 75
        self.direction = 1
        self.speed_x = 5
        self.shoot_timer = 0
        self.shoot_delay = max(30, 60 - level * 5)
        self.phase = 1
        self.bomb_timer = 0
        self.bomb_delay = 120

    def update(self):
        if self.rect.top > HEIGHT:
            self.kill()
            return
        health_ratio = self.health / self.max_health
        if health_ratio > 0.66:
            self.phase = 1
        elif health_ratio > 0.33:
            self.phase = 2
        else:
            self.phase = 3

        if self.phase == 1:
            self.speed_x = 5
            self.shoot_delay = max(30, 60 - level * 5)
        elif self.phase == 2:
            self.speed_x = 7
            self.shoot_delay = max(30, 60 - level * 5)
        else:
            self.speed_x = 10
            self.shoot_delay = max(25, 45 - level * 5)
            if random.random() < 0.05:
                self.direction *= -1

        if self.rect.top < 50:
            self.rect.y += self.speed_y
        else:
            self.rect.x += self.speed_x * self.direction
            if self.rect.right >= WIDTH or self.rect.left <= 0:
                self.direction *= -1

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot()
            self.shoot_timer = 0

        if self.phase == 3:
            self.bomb_timer += 1
            if self.bomb_timer >= self.bomb_delay:
                bombs.add(Bomb(self.rect.centerx, self.rect.bottom))
                BOSS_SHOOT_SOUND.play()
                self.bomb_timer = 0

    def shoot(self):
        if self.phase == 1:
            boss_bullets.add(BossBullet(self.rect.centerx, self.rect.bottom))
        elif self.phase == 2:
            angles = [0, -30, 30]
            for angle in angles:
                boss_bullets.add(BossBullet(self.rect.centerx, self.rect.bottom, angle))
        else:
            angles = [0, -45, -22.5, 22.5, 45]
            for angle in angles:
                boss_bullets.add(BossBullet(self.rect.centerx, self.rect.bottom, angle))
        BOSS_SHOOT_SOUND.play()

    def draw_health_bar(self, surface):
        bar_width = self.rect.width
        bar_height = 10
        health_ratio = self.health / self.max_health
        fill_width = int(bar_width * health_ratio)
        outline_rect = pygame.Rect(self.rect.left, self.rect.top - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.left, self.rect.top - 15, fill_width, bar_height)
        if self.phase == 3:
            pygame.draw.rect(surface, BLACK, outline_rect)
            pygame.draw.rect(surface, RED, fill_rect)
        else:
            color = GREEN if self.phase == 1 else YELLOW
            pygame.draw.rect(surface, RED, outline_rect)
            pygame.draw.rect(surface, color, fill_rect)

class HealthPack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = HEALTH_PACK_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = POWERUP_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class ShieldPowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = SHIELD_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class MissilePowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = MISSILE_POWERUP_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class SpeedPowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = SPEED_POWERUP_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class BombPowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BOMB_POWERUP_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Groups
player = None
player_group = pygame.sprite.GroupSingle()
bullets = pygame.sprite.Group()
missiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
health_packs = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
powerups = pygame.sprite.Group()
shield_powerups = pygame.sprite.Group()
missile_powerups = pygame.sprite.Group()
speed_powerups = pygame.sprite.Group()
bomb_powerups = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
bombs = pygame.sprite.Group()
artillery_shells = pygame.sprite.Group()

# Ship selection menu
def ship_selection_menu():
    global fullscreen_debounce_timer
    fade_screen()
    option_font = pygame.font.SysFont("arial", 28)
    selected_ship = 0
    selected_option = 0
    options = ["Ships", "Back"]
    display_ships = [pygame.transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5))) for img in PLAYER_IMGS]
    back_text = option_font.render("Back", True, WHITE)
    back_text_selected = option_font.render("Back", True, GREEN)

    while True:
        GAME_SURFACE.blit(SELECT_SHIP_IMG, ((WIDTH - SELECT_SHIP_IMG.get_width()) // 2, (HEIGHT - SELECT_SHIP_IMG.get_height()) // 2))

        for i, ship_img in enumerate(display_ships):
            if i < 2:
                x = WIDTH//2 - 100 if i == 0 else WIDTH//2 + 100
                y = HEIGHT//2 - 80 - ship_img.get_height()//2
            else:
                x = WIDTH//2 - 100 if i == 2 else WIDTH//2 + 100
                y = HEIGHT//2 + 80 - ship_img.get_height()//2
            GAME_SURFACE.blit(ship_img, (x - ship_img.get_width()//2, y))
            if selected_option == 0 and i == selected_ship:
                pygame.draw.rect(GAME_SURFACE, GREEN, (x - ship_img.get_width()//2 - 5, y - 5, ship_img.get_width() + 10, ship_img.get_height() + 10), 3)

        GAME_SURFACE.blit(back_text_selected if selected_option == 1 else back_text, (WIDTH//2 - back_text.get_width()//2, 600))

        render_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_UP:
                    if selected_option == 1:
                        selected_option = 0
                    elif selected_ship == 2:
                        selected_ship = 0
                    elif selected_ship == 3:
                        selected_ship = 1
                    else:
                        selected_ship = selected_ship + 2
                if event.key == pygame.K_DOWN:
                    if selected_option == 0:
                        if selected_ship == 0:
                            selected_ship = 2
                        elif selected_ship == 1:
                            selected_ship = 3
                        else:
                            selected_option = 1
                if event.key == pygame.K_LEFT and selected_option == 0:
                    selected_ship = (selected_ship - 1) % len(PLAYER_IMGS)
                if event.key == pygame.K_RIGHT and selected_option == 0:
                    selected_ship = (selected_ship + 1) % len(PLAYER_IMGS)
                if event.key == pygame.K_RETURN:
                    fade_screen()
                    if selected_option == 1:
                        return "main_menu"
                    return PLAYER_IMGS[selected_ship]
                if event.key == pygame.K_ESCAPE:
                    fade_screen()
                    return "main_menu"

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# Controls screen
def controls_screen():
    global fullscreen_debounce_timer
    fade_screen()
    control_font = pygame.font.SysFont("arial", 28)
    option_font = pygame.font.SysFont("arial", 28)
    
    control_texts = [
        control_font.render("Left Arrow: Move Left", True, WHITE),
        control_font.render("Right Arrow: Move Right", True, WHITE),
        control_font.render("Up Arrow: Move Up", True, WHITE),
        control_font.render("Down Arrow: Move Down", True, WHITE),
        control_font.render("Space: Shoot", True, WHITE),
        control_font.render("M: Fire Missile (with powerup)", True, WHITE),
        control_font.render("B: Use Bomb (with powerup)", True, WHITE),
        control_font.render("P or ESC: Pause", True, WHITE),
        control_font.render("F11: Toggle Fullscreen", True, WHITE),
        control_font.render("F1: FPS, F2: Debug", True, WHITE),
        control_font.render("Up/Down Arrows: Navigate Menus", True, WHITE),
        control_font.render("Enter: Select Menu Option", True, WHITE)
    ]
    back_text = option_font.render("Back", True, WHITE)
    back_text_selected = option_font.render("Back", True, GREEN)
    selected = 0

    while True:
        GAME_SURFACE.blit(CONTROLS_IMG, ((WIDTH - CONTROLS_IMG.get_width()) // 2, (HEIGHT - CONTROLS_IMG.get_height()) // 2))

        for i, text in enumerate(control_texts):
            GAME_SURFACE.blit(text, (WIDTH//2 - text.get_width()//2, 140 + i * 35))

        GAME_SURFACE.blit(back_text_selected if selected else back_text, (WIDTH//2 - back_text.get_width()//2, 560))

        render_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected = 1 - selected
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    fade_screen()
                    return

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# About Screen
def about_screen():
    global fullscreen_debounce_timer
    fade_screen()
    instruction_font = pygame.font.SysFont("arial", 24)
    text_font = pygame.font.SysFont("arial", 22)
    instruction_text = instruction_font.render("Press ESC to return to menu", True, WHITE)

    # Define scrolling text content
    scroll_text = [
        ("Game Overview", True),
        ("Star Fighter is a vertical-scrolling space shooter where you,", False),
        ("as Commander Aria Vex, pilot the Aetherion to battle the Xerath", False),
        ("Dominion’s forces in the Nebula Sector. Survive waves of enemies,", False),
        ("defeat powerful bosses, and collect power-ups to strengthen your ship.", False),
        ("Progress through increasingly difficult levels, earn high scores, and", False),
        ("save humanity from annihilation. The game features immersive visuals,", False),
        ("dynamic audio, and a variety of gameplay mechanics to test your skill", False),
        ("and strategy.", False),
        ("", False),
        ("Game Credits", True),
        ("Lead Developer: Rizwan N", False),
        ("Art Designer: Rizwan N", False),
        ("Music and Sound Effects: freesound.org", False),
        ("Game Design: Rizwan N", False),
        ("Thanks: Grok AI, Open AI", False),
        ("", False),
        ("Created with Pygame and Python", False),
        ("Version 1.0 - May 2025", False),
        ("", False),
        ("", False),
        ("Special Thanks", True),
        ("Thank you for playing Star Fighter! As Commander Aria Vex, you hold", False),
        ("humanity’s fate in your hands. Unravel the Dominion’s secrets, destroy", False),
        ("The Oblivion, and save the galaxy. Launch Aetherion and write your", False),
        ("legend among the stars!", False)
    ]

    # Pre-render text surfaces
    text_surfaces = []
    for text, is_heading in scroll_text:
        color = GREEN if is_heading else WHITE
        surface = text_font.render(text, True, color)
        text_surfaces.append((surface, is_heading))

    # Scroll parameters
    scroll_speed = 1  # Pixels per frame
    text_y = HEIGHT - 120  # Start at bottom of display area (y=780)
    total_text_height = sum(surface.get_height() + (20 if is_heading else 10) for surface, is_heading in text_surfaces)
    display_area_height = (HEIGHT - 120) - 170  # 780 - 170 = 610 pixels
    scroll_loop_height = total_text_height + display_area_height  # Total height including gap for looping

    while True:
        GAME_SURFACE.blit(ABOUT_IMG, ((WIDTH - ABOUT_IMG.get_width()) // 2, (HEIGHT - ABOUT_IMG.get_height()) // 2))

        # Draw scrolling text within y=170 to y=780
        y = int(text_y)
        for surface, is_heading in text_surfaces:
            # Only draw if the text is within the display area
            if y > 170 - surface.get_height() and y < HEIGHT - 120:
                x = WIDTH // 2 - surface.get_width() // 2
                GAME_SURFACE.blit(surface, (x, y))
            y += surface.get_height() + (20 if is_heading else 10)

        # Update scroll position
        text_y -= scroll_speed
        if text_y <= 170 - total_text_height:
            text_y += scroll_loop_height  # Loop back to bottom of display area

        # Draw static instruction text
        GAME_SURFACE.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))

        render_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_ESCAPE:
                    fade_screen()
                    return

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# Reset game state
def reset_game(ship_image):
    global score, level, wave, max_waves, enemies_per_wave, base_enemies, enemies_spawned, boss_spawned, powerup_timer, missile_timer, bg_y, game_started, level_transition_delay, delay_timer, player, player_group, last_score, last_level, score_text, level_text, bomb_flash_timer, BG, asteroid_spawn_timer, max_asteroids
    score = 0
    level = 1
    wave = 1
    max_waves = min(10, 6 + level - 1)
    base_enemies = 3 + level
    enemies_per_wave = math.ceil(base_enemies * 0.5)
    enemies_spawned = 0
    boss_spawned = False
    powerup_timer = 0
    missile_timer = 0
    asteroid_spawn_timer = 0
    max_asteroids = max(5, min(8, level - 1)) if level >= 2 else 0
    bg_y = 0
    game_started = False
    level_transition_delay = False
    delay_timer = 0
    bomb_flash_timer = 0
    last_score = -1
    last_level = -1
    score_text = None
    level_text = None
    player = Player(ship_image)
    player_group = pygame.sprite.GroupSingle(player)
    # Random BG initialization
    if BACKGROUNDS:
        BG = random.choice(BACKGROUNDS)
    else:
        BG = pygame.Surface((WIDTH, HEIGHT))
        BG.fill(BLACK)
    bullets.empty()
    missiles.empty()
    enemies.empty()
    boss_group.empty()
    health_packs.empty()
    powerups.empty()
    shield_powerups.empty()
    missile_powerups.empty()
    speed_powerups.empty()
    bomb_powerups.empty()
    boss_bullets.empty()
    enemy_bullets.empty()
    bombs.empty()
    artillery_shells.empty()
    asteroids.empty()
    play_game_music()

# Input initials for high score
def input_initials(score):
    global fullscreen_debounce_timer
    instruction_font = pygame.font.SysFont("arial", 24)
    input_font = pygame.font.SysFont("arial", 36)
    
    instruction_text = instruction_font.render("Enter 3 initials (A-Z), Press ENTER or ESC", True, WHITE)
    score_text = instruction_font.render(f"Score: {score}", True, WHITE)
    NEW_HIGH_SCORE_IMG = pygame.image.load("assets/new_high_score.png")
    
    pygame.mixer.music.stop()
    pygame.mixer.stop()
    global is_menu_music_playing
    is_menu_music_playing = False
    if GAME_OVER_SOUND and not GAME_OVER_CHANNEL.get_busy():
        if DEBUG_PRINT:
            print("Playing game_over.wav in input_initials")
        GAME_OVER_CHANNEL.play(GAME_OVER_SOUND)
    
    initials = ["A", "A", "A"]
    current_pos = 0
    
    while True:
        GAME_SURFACE.blit(NEW_HIGH_SCORE_IMG, ((WIDTH - NEW_HIGH_SCORE_IMG.get_width()) // 2, 0))
        
        GAME_SURFACE.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT//2 + 120))
        GAME_SURFACE.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 40))
        
        for i, letter in enumerate(initials):
            color = GREEN if i == current_pos else WHITE
            letter_text = input_font.render(letter, True, color)
            GAME_SURFACE.blit(letter_text, (WIDTH//2 - 60 + i * 40, HEIGHT//2 - 40))
        
        render_game()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if GAME_OVER_CHANNEL.get_busy():
                    GAME_OVER_CHANNEL.stop()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_LEFT and current_pos > 0:
                    current_pos -= 1
                if event.key == pygame.K_RIGHT and current_pos < 2:
                    current_pos += 1
                if event.key == pygame.K_UP:
                    current_letter = initials[current_pos]
                    next_letter = chr(ord(current_letter) + 1) if ord(current_letter) < ord('Z') else 'A'
                    initials[current_pos] = next_letter
                if event.key == pygame.K_DOWN:
                    current_letter = initials[current_pos]
                    next_letter = chr(ord(current_letter) - 1) if ord(current_letter) > ord('A') else 'Z'
                    initials[current_pos] = next_letter
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    # Do not stop game over sound, let it continue
                    initials_str = "".join(initials)
                    return initials_str

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# Save high score with initials
def save_high_score(initials, score, scores):
    global fullscreen_debounce_timer
    high_score_file = "high_scores.txt"
    scores.append((initials.upper(), score))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[:5]
    
    try:
        with open(high_score_file, "w", encoding="utf-8") as file:
            for init, s in scores:
                file.write(f"{init},{s}\n")
    except Exception:
        pass

# Main Menu
def main():
    global level
    pygame.display.set_caption("Star Fighter")
    clock = pygame.time.Clock()
    play_menu_music()

    start_screen()
    while True:
        choice = main_menu()
        if choice == "quit":
            pygame.quit()
            sys.exit()
        elif choice == "new_game":
            selected_ship = ship_selection_menu()
            if selected_ship == "main_menu":
                continue
            elif selected_ship:
                result = run_game(selected_ship)
                if result == "game_over":
                    result = game_over()
                    if result == "retry":
                        continue
                    elif result == "main_menu":
                        play_menu_music()
                        continue
                    elif result == "quit":
                        pygame.quit()
                        sys.exit()
                elif result == "main_menu":
                    play_menu_music()
                    continue
                elif result == "quit":
                    pygame.quit()
                    sys.exit()

def main_menu():
    global fullscreen_debounce_timer
    play_menu_music()
    fade_screen()
    option_font = pygame.font.SysFont("arial", 28)
    options = ["New Game", "High Scores", "Controls", "About", "Quit"]
    option_texts = [option_font.render(opt, True, WHITE) for opt in options]
    option_texts_selected = [option_font.render(opt, True, GREEN) for opt in options]
    selected = 0

    while True:
        clock.tick(FPS)
        GAME_SURFACE.blit(MAIN_MENU_IMG, ((WIDTH - MAIN_MENU_IMG.get_width()) // 2, (HEIGHT - MAIN_MENU_IMG.get_height()) // 2))

        for i, (text, text_selected) in enumerate(zip(option_texts, option_texts_selected)):
            GAME_SURFACE.blit(text_selected if i == selected else text, (WIDTH//2 - text.get_width()//2, 300 + i * 40))

        render_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if options[selected] == "New Game":
                        return "new_game"
                    elif options[selected] == "High Scores":
                        fade_screen()
                        high_scores_screen()
                    elif options[selected] == "Controls":
                        fade_screen()
                        controls_screen()
                    elif options[selected] == "About":
                        fade_screen()
                        about_screen()
                    elif options[selected] == "Quit":
                        pygame.quit()
                        sys.exit()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# High Scores Screen
def high_scores_screen():
    global fullscreen_debounce_timer
    score_font = pygame.font.SysFont("arial", 28)
    instruction_font = pygame.font.SysFont("arial", 24)
    
    instruction_text = instruction_font.render("Press ENTER or ESC to return to menu", True, WHITE)
    
    high_score_file = "high_scores.txt"
    scores = [("---", 0)] * 5
    try:
        if os.path.exists(high_score_file):
            with open(high_score_file, "r", encoding="utf-8") as file:
                temp_scores = []
                for line in file:
                    if line.strip():
                        try:
                            init, s = line.strip().split(",")
                            if len(init) == 3 and init.isalpha() and s.isdigit():
                                temp_scores.append((init.upper(), int(s)))
                        except ValueError:
                            continue
                scores = temp_scores + [("---", 0)] * (5 - len(temp_scores))
    except Exception:
        pass
    
    score_texts = [score_font.render(f"{i+1}. {init} {score}", True, WHITE) for i, (init, score) in enumerate(scores[:5])]

    while True:
        GAME_SURFACE.blit(HIGH_SCORES_IMG, ((WIDTH - HIGH_SCORES_IMG.get_width()) // 2, (HEIGHT - HIGH_SCORES_IMG.get_height()) // 2))
        
        for i, text in enumerate(score_texts):
            GAME_SURFACE.blit(text, (WIDTH//2 - text.get_width()//2, 250 + i * 40))
        
        GAME_SURFACE.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 500))
        render_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    fade_screen()
                    return

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# Pause Menu
def pause_menu():
    global is_menu_music_playing, fullscreen_debounce_timer
    pygame.mixer.music.pause()
    play_menu_music()
    option_font = pygame.font.SysFont("arial", 28)
    options = ["Resume", "Restart", "Main Menu", "Quit"]
    option_texts = [option_font.render(opt, True, WHITE) for opt in options]
    option_texts_selected = [option_font.render(opt, True, GREEN) for opt in options]
    selected = 0
    
    while True:
        GAME_SURFACE.fill((0, 0, 0))
        GAME_SURFACE.blit(GAME_PAUSED_IMG, ((WIDTH - GAME_PAUSED_IMG.get_width()) // 2, (HEIGHT - GAME_PAUSED_IMG.get_height()) // 2))
        for i, (text, text_selected) in enumerate(zip(option_texts, option_texts_selected)):
            GAME_SURFACE.blit(text_selected if i == selected else text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100 + i * 40))
        render_game()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if options[selected] == "Resume":
                        pygame.mixer.music.stop()
                        play_game_music()
                    elif options[selected] == "Restart":
                        pass
                    elif options[selected] == "Main Menu":
                        pass
                    return options[selected].lower()

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# Game Over
def game_over():
    global score, is_menu_music_playing, fullscreen_debounce_timer
    pygame.mixer.music.stop()
    pygame.mixer.stop()
    is_menu_music_playing = False
    
    high_score_file = "high_scores.txt"
    scores = [("---", 0)] * 5
    try:
        if os.path.exists(high_score_file):
            with open(high_score_file, "r", encoding="utf-8") as file:
                temp_scores = []
                for line in file:
                    if line.strip():
                        try:
                            init, s = line.strip().split(",")
                            if len(init) == 3 and init.isalpha() and s.isdigit():
                                temp_scores.append((init.upper(), int(s)))
                        except ValueError:
                            continue
                scores = temp_scores + [("---", 0)] * (5 - len(temp_scores))
    except Exception as e:
        if DEBUG_PRINT:
            print(f"Error reading high scores: {e}")

    if any(score > s[1] for s in scores) or len([s for s in scores if s[1] > 0]) < 5:
        initials = input_initials(score)
        save_high_score(initials, score, scores)
    else:
        save_high_score("---", score, scores)
    
    fade_screen((0, 0, 0))
    option_font = pygame.font.SysFont("arial", 28)
    options = ["Retry", "Main Menu", "Quit"]
    option_texts = [option_font.render(opt, True, WHITE) for opt in options]
    option_texts_selected = [option_font.render(opt, True, GREEN) for opt in options]
    selected = 0

    if GAME_OVER_SOUND and not GAME_OVER_CHANNEL.get_busy():
        if DEBUG_PRINT:
            print("Playing game_over.wav after fade in game_over")
        GAME_OVER_CHANNEL.play(GAME_OVER_SOUND)

    while True:
        GAME_SURFACE.fill((0, 0, 0))
        GAME_SURFACE.blit(GAME_OVER_IMG, ((WIDTH - GAME_OVER_IMG.get_width()) // 2, (HEIGHT - GAME_OVER_IMG.get_height()) // 2))
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        GAME_SURFACE.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))

        for i, (text, text_selected) in enumerate(zip(option_texts, option_texts_selected)):
            GAME_SURFACE.blit(text_selected if i == selected else text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 60 + i * 40))

        render_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if GAME_OVER_CHANNEL.get_busy():
                    GAME_OVER_CHANNEL.stop()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if GAME_OVER_CHANNEL.get_busy():
                        GAME_OVER_CHANNEL.stop()
                    if options[selected] == "Retry":
                        return "retry"
                    elif options[selected] == "Main Menu":
                        return "main_menu"
                    elif options[selected] == "Quit":
                        pygame.quit()
                        sys.exit()
                if event.key == pygame.K_ESCAPE:
                    if GAME_OVER_CHANNEL.get_busy():
                        GAME_OVER_CHANNEL.stop()
                    return "main_menu"

        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

# Handle waves
def handle_waves():
    global level, wave, max_waves, enemies_per_wave, base_enemies, enemies_spawned, boss_spawned, level_transition_delay, score, spawn_timer, BG, asteroid_spawn_timer, max_asteroids
    if level_transition_delay:
        return
    if game_started and wave < max_waves and enemies_spawned >= enemies_per_wave and not enemies and not boss_group:
        wave += 1
        base_enemies = 3 + level
        if wave == 1:
            enemies_per_wave = math.ceil(base_enemies * 0.5)
        elif wave == 2:
            enemies_per_wave = math.ceil(base_enemies * 0.75)
        elif wave == 3:
            enemies_per_wave = base_enemies
        elif wave == 4:
            enemies_per_wave = math.ceil(base_enemies * 1.25)
        elif wave == 5:
            enemies_per_wave = math.ceil(base_enemies * 1.5)
        elif wave == 6:
            enemies_per_wave = math.ceil(base_enemies * 1.75)
        else:
            enemies_per_wave = math.ceil(base_enemies * 2.0)
        enemies_spawned = 0
        boss_spawned = False
        spawn_timer = 0
    if game_started and wave == max_waves and not boss_spawned and not enemies:
        boss = Boss()
        boss_group.add(boss)
        boss_spawned = True
        enemy_bullets.empty()
        bombs.empty()
        artillery_shells.empty()
    if game_started and wave > max_waves:
        GAME_SURFACE.fill(BLACK)
        level_text = font.render(f"Level {level} Completed!", True, WHITE)
        GAME_SURFACE.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2))
        score += 100
        render_game()
        pygame.time.delay(3000)
        fade_screen()
        level += 1
        wave = 1
        max_waves = min(10, 6 + level - 1)
        base_enemies = 3 + level
        enemies_per_wave = math.ceil(base_enemies * 0.5)
        enemies_spawned = 0
        boss_spawned = False
        boss_group.empty()
        # Set random background for new level
        if BACKGROUNDS:
            available_backgrounds = [bg for bg in BACKGROUNDS if bg != BG]
            BG = random.choice(available_backgrounds if available_backgrounds else BACKGROUNDS)
        else:
            BG = pygame.Surface((WIDTH, HEIGHT))
            BG.fill(BLACK)
        player.rect.center = (WIDTH//2, HEIGHT - 60)
        player.is_tethered = False
        player.tether_timer = 0
        bullets.empty()
        missiles.empty()
        boss_bullets.empty()
        enemy_bullets.empty()
        bombs.empty()
        artillery_shells.empty()
    if game_started and wave < max_waves and enemies_spawned < enemies_per_wave and not boss_spawned:
        spawn_timer += 1
        if spawn_timer >= SPAWN_DELAY:
            enemies.add(Enemy())
            enemies_spawned += 1
            spawn_timer = 0
    if game_started and level >= 2 and len(asteroids) < max_asteroids and not boss_spawned:
        asteroid_spawn_timer += 1
        if asteroid_spawn_timer >= ASTEROID_SPAWN_DELAY:
            asteroids.add(Asteroid())
            asteroid_spawn_timer = 0

# Main game loop
def run_game(selected_ship):
    global game_started, enemies_spawned, enemies_per_wave, base_enemies, powerup_timer, missile_timer, score, bg_y, wave, boss_spawned, level_transition_delay, delay_timer, debug_mode, fps_debug, last_score, last_level, score_text, level_text, last_frame_time, player, player_group, level, max_waves, bomb_flash_timer, BG, asteroid_spawn_timer, max_asteroids, fullscreen_debounce_timer
    reset_game(selected_ship)
    countdown_start = pygame.time.get_ticks()
    countdown_duration = 3000

    while True:
        frame_start = pygame.time.get_ticks()
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_F1]:
            fps_debug = not fps_debug
            
        if keys[pygame.K_F2]:
            debug_mode = not debug_mode

        # Update debounce timer
        if fullscreen_debounce_timer > 0 and (pygame.time.get_ticks() - fullscreen_debounce_timer) >= FULLSCREEN_DEBOUNCE_DELAY:
            fullscreen_debounce_timer = 0

        time_elapsed = pygame.time.get_ticks() - countdown_start
        if time_elapsed < countdown_duration:
            GAME_SURFACE.fill(BLACK)
            GAME_SURFACE.blit(LOADING_SCREEN, ((WIDTH - LOADING_SCREEN.get_width()) // 2, 0))
            render_game()
            continue

        if not game_started:
            game_started = True

        if level_transition_delay:
            delay_timer -= 1
            if delay_timer <= 0:
                level_transition_delay = False
                fade_screen()
                max_asteroids = max(5, min(8, level - 1)) if level >= 2 else 0

        bg_y = (bg_y + 1) % BG.get_height()

        handle_waves()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_SPACE:
                    player.shoot(mash=True)
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    pause_choice = pause_menu()
                    if pause_choice == "resume":
                        continue
                    elif pause_choice == "restart":
                        reset_game(selected_ship)
                        countdown_start = pygame.time.get_ticks()
                        game_started = False
                        continue
                    elif pause_choice == "main menu":
                        return "main_menu"
                    elif pause_choice == "quit":
                        return "quit"

        player_group.update(keys)
        bullets.update()
        missiles.update()
        enemies.update()
        boss_group.update()
        health_packs.update()
        powerups.update()
        shield_powerups.update()
        missile_powerups.update()
        speed_powerups.update()
        bomb_powerups.update()
        asteroids.update()

        if player.double_shot:
            powerup_timer -= 1
            if powerup_timer <= 0:
                player.double_shot = False

        if player.shield:
            player.shield_timer -= 1
            if player.shield_timer <= 0:
                player.shield = False

        if player.missile_shot:
            missile_timer -= 1
            if missile_timer <= 0:
                player.missile_shot = False

        if player.speed_boost:
            player.speed_timer -= 1
            if player.speed_timer <= 0:
                player.speed_boost = False
                player.speed = player.base_speed

        if not player.shield and not player.invincible:
            hits = pygame.sprite.spritecollide(player, enemies, False)
            boss_collision = pygame.sprite.spritecollide(player, boss_group, False)
            boss_bullet_hits = pygame.sprite.spritecollide(player, boss_bullets, True)
            enemy_bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            bomb_hits = pygame.sprite.spritecollide(player, bombs, True)
            artillery_shell_hits = pygame.sprite.spritecollide(player, artillery_shells, False)
            asteroid_hits = pygame.sprite.spritecollide(player, asteroids, True)

            for hit in hits:
                player.health -= 20
                hit.kill()
                if hit.is_leech and hit.tethered_enemy:
                    hit.tethered_enemy.is_tethered = False
                if PLAYER_COLLISION_SOUND:
                    PLAYER_COLLISION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Player hit enemy, playing player_collision.wav")
            if boss_collision:
                player.health -= 1
                if PLAYER_COLLISION_SOUND:
                    PLAYER_COLLISION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Player hit boss, playing player_collision.wav")
            for hit in boss_bullet_hits:
                player.health -= 10
                if PLAYER_COLLISION_SOUND:
                    PLAYER_COLLISION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Player hit boss bullet, playing player_collision.wav")
            for hit in enemy_bullet_hits:
                player.health -= hit.damage
                if PLAYER_COLLISION_SOUND:
                    PLAYER_COLLISION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Player hit enemy bullet, playing player_collision.wav")
            for hit in bomb_hits:
                player.health -= hit.damage
                if PLAYER_COLLISION_SOUND:
                    PLAYER_COLLISION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Player hit bomb, playing player_collision.wav")
            for hit in artillery_shell_hits:
                if not hit.exploded:
                    player.health -= hit.damage
                    hit.explode()
                    if PLAYER_COLLISION_SOUND:
                        PLAYER_COLLISION_SOUND.play()
                        if DEBUG_PRINT:
                            print("Player hit artillery shell, playing player_collision.wav")
            for hit in asteroid_hits:
                player.health -= hit.damage
                if ASTEROID_COLLISION_SOUND:
                    ASTEROID_COLLISION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Asteroid hit player, playing asteroid_collision.wav")

            if player.health <= 0:
                if PLAYER_EXPLOSION_SOUND:
                    PLAYER_EXPLOSION_SOUND.play()
                player.lives -= 1
                if player.lives <= 0:
                    game_over_choice = game_over()
                    if game_over_choice == "retry":
                        reset_game(selected_ship)
                        countdown_start = pygame.time.get_ticks()
                        game_started = False
                        continue
                    elif game_over_choice == "main_menu":
                        return "main_menu"
                    elif game_over_choice == "quit":
                        return "quit"
                else:
                    player.reset()
                    enemies.empty()
                    enemy_bullets.empty()
                    bombs.empty()
                    artillery_shells.empty()
                    asteroids.empty()
                    enemies_spawned = 0

        bullet_hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
        for bullet, hit_enemies in bullet_hits.items():
            for enemy in hit_enemies:
                enemy.health -= bullet.damage
                if enemy.health <= 0:
                    score += enemy.score_value
                    if EXPLOSION_SOUND:
                        EXPLOSION_SOUND.play()
                    enemy.kill()
                    if enemy.is_leech and enemy.tethered_enemy:
                        enemy.tethered_enemy.is_tethered = False
                    if random.random() < 0.05:
                        health_packs.add(HealthPack(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.1:
                        powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.05:
                        shield_powerups.add(ShieldPowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.05:
                        missile_powerups.add(MissilePowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.05:
                        speed_powerups.add(SpeedPowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.03:
                        bomb_powerups.add(BombPowerUp(enemy.rect.centerx, enemy.rect.centery))

        bullet_boss_hits = pygame.sprite.groupcollide(bullets, boss_group, True, False)
        for bullet, bosses in bullet_boss_hits.items():
            for boss in bosses:
                boss.health -= bullet.damage
                if boss.health <= 0:
                    score += int(250 * (1.25 ** (level - 1)))
                    boss.kill()
                    if BOSS_EXPLOSION_SOUND:
                        BOSS_EXPLOSION_SOUND.play()
                    wave += 1
                    level_transition_delay = True
                    delay_timer = 180

        bullet_asteroid_hits = pygame.sprite.groupcollide(bullets, asteroids, True, False)
        for bullet, hit_asteroids in bullet_asteroid_hits.items():
            for asteroid in hit_asteroids:
                asteroid.health -= 1
                if asteroid.health <= 0:
                    if EXPLOSION_SOUND:
                        EXPLOSION_SOUND.play()
                        if DEBUG_PRINT:
                            print("Asteroid destroyed by bullet, playing explosion.wav")
                    asteroid.kill()

        missile_hits = pygame.sprite.groupcollide(missiles, enemies, True, False)
        for missile, hit_enemies in missile_hits.items():
            for enemy in hit_enemies:
                try:
                    enemy_type_id = enemy.type_data[8]
                    if enemy_type_id in [1, 2, 4, 5]:
                        enemy.health = 0
                        score += enemy.score_value
                        if EXPLOSION_SOUND:
                            EXPLOSION_SOUND.play()
                        enemy.kill()
                        if enemy.is_leech and enemy.tethered_enemy:
                            enemy.tethered_enemy.is_tethered = False
                    elif enemy_type_id in [3, 6, 7]:
                        enemy_id = id(enemy)
                        missile_hits_tracker[enemy_id] = missile_hits_tracker.get(enemy_id, 0) + 1
                        if missile_hits_tracker[enemy_id] >= 2:
                            enemy.health = 0
                            score += enemy.score_value
                            if EXPLOSION_SOUND:
                                EXPLOSION_SOUND.play()
                            enemy.kill()
                            if enemy.is_leech and enemy.tethered_enemy:
                                enemy.tethered_enemy.is_tethered = False
                            del missile_hits_tracker[enemy_id]
                except (IndexError, AttributeError):
                    enemy_type_id = -1
                if enemy.health <= 0:
                    if random.random() < 0.05:
                        health_packs.add(HealthPack(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.1:
                        powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.05:
                        shield_powerups.add(ShieldPowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.05:
                        missile_powerups.add(MissilePowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.05:
                        speed_powerups.add(SpeedPowerUp(enemy.rect.centerx, enemy.rect.centery))
                    elif random.random() < 0.03:
                        bomb_powerups.add(BombPowerUp(enemy.rect.centerx, enemy.rect.centery))

        missile_boss_hits = pygame.sprite.groupcollide(missiles, boss_group, True, False)
        for missile, bosses in missile_boss_hits.items():
            for boss in bosses:
                boss.health -= missile.damage
                if boss.health <= 0:
                    score += int(250 * (1.25 ** (level - 1)))
                    boss.kill()
                    if BOSS_EXPLOSION_SOUND:
                        BOSS_EXPLOSION_SOUND.play()
                    wave += 1
                    level_transition_delay = True
                    delay_timer = 180

        missile_asteroid_hits = pygame.sprite.groupcollide(missiles, asteroids, True, False)
        for missile, hit_asteroids in missile_asteroid_hits.items():
            for asteroid in hit_asteroids:
                asteroid.health = 0
                if EXPLOSION_SOUND:
                    EXPLOSION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Asteroid destroyed by missile, playing explosion.wav")
                asteroid.kill()

        asteroid_enemy_hits = pygame.sprite.groupcollide(asteroids, enemies, True, True)
        for asteroid, hit_enemies in asteroid_enemy_hits.items():
            for enemy in hit_enemies:
                score += enemy.score_value
                if ASTEROID_COLLISION_SOUND:
                    ASTEROID_COLLISION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Asteroid hit enemy, playing asteroid_collision.wav")
                if EXPLOSION_SOUND:
                    EXPLOSION_SOUND.play()
                    if DEBUG_PRINT:
                        print("Enemy destroyed by asteroid, playing explosion.wav")
                if enemy.is_leech and enemy.tethered_enemy:
                    enemy.tethered_enemy.is_tethered = False

        health_pack_collisions = pygame.sprite.spritecollide(player, health_packs, True)
        for _ in health_pack_collisions:
            player.health = min(player.health + 25, 100)
            if HEALTH_PACK_COLLECT_SOUND:
                HEALTH_PACK_COLLECT_SOUND.play()

        powerup_collisions = pygame.sprite.spritecollide(player, powerups, True)
        for _ in powerup_collisions:
            player.double_shot = True
            powerup_timer = DOUBLE_SHOT_DURATION
            if POWERUP_COLLECT_SOUND:
                POWERUP_COLLECT_SOUND.play()

        shield_collisions = pygame.sprite.spritecollide(player, shield_powerups, True)
        for _ in shield_collisions:
            player.shield = True
            player.shield_timer = SHIELD_DURATION
            if POWERUP_COLLECT_SOUND:
                POWERUP_COLLECT_SOUND.play()

        missile_powerup_collisions = pygame.sprite.spritecollide(player, missile_powerups, True)
        for _ in missile_powerup_collisions:
            player.missile_shot = True
            missile_timer = MISSILE_DURATION
            if POWERUP_COLLECT_SOUND:
                POWERUP_COLLECT_SOUND.play()

        speed_powerup_collisions = pygame.sprite.spritecollide(player, speed_powerups, True)
        for _ in speed_powerup_collisions:
            player.speed_boost = True
            player.speed_timer = player.SPEED_DURATION
            player.speed = player.base_speed * 1.5
            if POWERUP_COLLECT_SOUND:
                POWERUP_COLLECT_SOUND.play()

        bomb_powerup_collisions = pygame.sprite.spritecollide(player, bomb_powerups, True)
        for _ in bomb_powerup_collisions:
            if player.bomb_count < player.MAX_BOMBS:
                player.bomb_count += 1
            if POWERUP_COLLECT_SOUND:
                POWERUP_COLLECT_SOUND.play()

        boss_bullets.update()
        enemy_bullets.update()
        bombs.update()
        artillery_shells.update()

        bg_y = (bg_y + 1) % BG.get_height()
        GAME_SURFACE.blit(BG, (0, -BG.get_height() + bg_y))
        GAME_SURFACE.blit(BG, (0, bg_y))

        if bomb_flash_timer > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.fill(WHITE)
            flash_surface.set_alpha(int(128 * (bomb_flash_timer / 10)))
            GAME_SURFACE.blit(flash_surface, (0, 0))
            bomb_flash_timer -= 1

        for bullet in bullets:
            GAME_SURFACE.blit(bullet.image, bullet.rect)

        for missile in missiles:
            GAME_SURFACE.blit(missile.image, missile.rect)

        for enemy in enemies:
            enemy.draw(GAME_SURFACE)

        for boss in boss_group:
            boss.draw_health_bar(GAME_SURFACE)
            GAME_SURFACE.blit(boss.image, boss.rect)

        for health_pack in health_packs:
            GAME_SURFACE.blit(health_pack.image, health_pack.rect)

        for powerup in powerups:
            GAME_SURFACE.blit(powerup.image, powerup.rect)

        for shield_powerup in shield_powerups:
            GAME_SURFACE.blit(shield_powerup.image, shield_powerup.rect)

        for missile_powerup in missile_powerups:
            GAME_SURFACE.blit(missile_powerup.image, missile_powerup.rect)

        for speed_powerup in speed_powerups:
            GAME_SURFACE.blit(speed_powerup.image, speed_powerup.rect)

        for bomb_powerup in bomb_powerups:
            GAME_SURFACE.blit(bomb_powerup.image, bomb_powerup.rect)

        for asteroid in asteroids:
            GAME_SURFACE.blit(asteroid.image, asteroid.rect)

        for bullet in boss_bullets:
            GAME_SURFACE.blit(bullet.image, bullet.rect)

        for bullet in enemy_bullets:
            bullet.draw(GAME_SURFACE)

        for bomb in bombs:
            GAME_SURFACE.blit(bomb.image, bomb.rect)

        for shell in artillery_shells:
            shell.draw(GAME_SURFACE)

        player.draw(GAME_SURFACE)

        if score != last_score:
            score_text = font.render(f"Score: {score}", True, WHITE)
            last_score = score
        if level != last_level:
            level_text = font.render(f"Level: {level}", True, WHITE)
            last_level = level

        draw_health_bar(GAME_SURFACE, 10, 10, player.health, 100)
        GAME_SURFACE.blit(score_text, (10, 40))
        GAME_SURFACE.blit(level_text, (10, 70))
        for i in range(player.lives):
            GAME_SURFACE.blit(HEART_IMG, (10 + i * (HEART_IMG.get_width() + 5), 100))
        if player.double_shot:
            GAME_SURFACE.blit(DOUBLE_ICON, (WIDTH - 140, 20))
            draw_timer_bar(GAME_SURFACE, WIDTH - 110, 25, powerup_timer, DOUBLE_SHOT_DURATION, YELLOW)
        if player.shield:
            GAME_SURFACE.blit(SHIELD_ICON, (WIDTH - 140, 50))
            draw_timer_bar(GAME_SURFACE, WIDTH - 110, 55, player.shield_timer, SHIELD_DURATION, BLUE)
        if player.missile_shot:
            GAME_SURFACE.blit(MISSILE_ICON, (WIDTH - 140, 80))
            draw_timer_bar(GAME_SURFACE, WIDTH - 110, 85, missile_timer, MISSILE_DURATION, RED)
        if player.speed_boost:
            GAME_SURFACE.blit(SPEED_ICON, (WIDTH - 140, 110))
            draw_timer_bar(GAME_SURFACE, WIDTH - 110, 115, player.speed_timer, player.SPEED_DURATION, GREEN)
        if player.bomb_count > 0:
            GAME_SURFACE.blit(BOMB_ICON, (WIDTH - 140, 140))
            bomb_count_text = font.render(f"x{player.bomb_count}", True, WHITE)
            GAME_SURFACE.blit(bomb_count_text, (WIDTH - 110, 140))

        draw_debug_info()
        draw_fps_info()

        render_game()
        last_frame_time = frame_start

# Main execution
if __name__ == "__main__":
    start_screen()
    while True:
        choice = main_menu()
        if choice == "new_game":
            selected_ship = ship_selection_menu()
            if selected_ship == "main_menu":
                continue
            elif selected_ship:
                result = run_game(selected_ship)
                if result == "main_menu":
                    continue
                elif result == "quit":
                    pygame.quit()
                    sys.exit()
        elif choice == "quit":
            pygame.quit()
            sys.exit()
