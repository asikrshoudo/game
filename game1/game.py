import pygame
import random
import math
import sys
import time
from enum import Enum

# Pygame initialization
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Defender - Ultimate Space Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
GOLD = (255, 215, 0)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
SILVER = (192, 192, 192)
DARK_GREEN = (0, 100, 0)
BROWN = (165, 42, 42)

# Game states
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    SETTINGS = 2
    ABOUT = 3
    GAME_OVER = 4
    PAUSED = 5
    LEVEL_TRANSITION = 6
    BOSS_FIGHT = 7
    UPGRADE_SHOP = 8

# Enemy types
class EnemyType(Enum):
    BASIC = 1
    FAST = 2
    TANK = 3
    SHOOTER = 4
    BOSS = 5

# Weapon types
class WeaponType(Enum):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    SPREAD = 4
    LASER = 5

# Load fonts
title_font = pygame.font.SysFont('arial', 64, bold=True)
menu_font = pygame.font.SysFont('arial', 36)
game_font = pygame.font.SysFont('arial', 24)
small_font = pygame.font.SysFont('arial', 18)

# Sound Manager
class SoundManager:
    def __init__(self):
        self.sounds_enabled = True
        
    def toggle_sounds(self):
        self.sounds_enabled = not self.sounds_enabled
        return self.sounds_enabled

# Enhanced Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.icon = icon
        self.glow = 0
        self.glow_dir = 1
        
    def draw(self, surface):
        self.glow += 0.1 * self.glow_dir
        if self.glow > 5 or self.glow < 0:
            self.glow_dir *= -1
        
        color = self.hover_color if self.is_hovered else self.color
        
        if self.is_hovered:
            glow_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, 100), glow_surf.get_rect(), border_radius=15)
            surface.blit(glow_surf, (self.rect.x - 5, self.rect.y - 5))
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        
        border_color = WHITE if self.is_hovered else LIGHT_BLUE
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=10)
        
        text_surf = menu_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        if self.icon:
            icon_rect = self.icon.get_rect(midright=(self.rect.centerx - text_surf.get_width()//2 - 10, self.rect.centery))
            surface.blit(self.icon, icon_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Player class
class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 5
        self.color = GREEN
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.lives = 3
        self.shoot_delay = 200
        self.last_shot = 0
        self.weapon_level = 1
        self.weapon_type = WeaponType.SINGLE
        self.power_timer = 0
        self.shield = 0
        self.money = 0
        self.kill_count = 0
        self.upgrades = {
            "speed": 1,
            "health": 1,
            "damage": 1,
            "fire_rate": 1
        }
        self.invincible = 0

    def draw(self):
        pulse = 0
        if self.invincible > 0:
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 10
            
        # Main ship body
        pygame.draw.polygon(screen, self.color, [
            (self.x, self.y - self.height//2 - pulse),
            (self.x - self.width//2, self.y + self.height//2),
            (self.x + self.width//2, self.y + self.height//2)
        ])
        
        # Cockpit
        pygame.draw.circle(screen, LIGHT_BLUE, (self.x, self.y - 5), 8)
        
        # Engine fire effect
        fire_height = random.randint(10, 20)
        pygame.draw.polygon(screen, YELLOW, [
            (self.x - 8, self.y + self.height//2),
            (self.x, self.y + self.height//2 + fire_height),
            (self.x + 8, self.y + self.height//2)
        ])
        
        # Wings
        pygame.draw.polygon(screen, BLUE, [
            (self.x - self.width//2, self.y + self.height//2),
            (self.x - self.width//2 - 10, self.y),
            (self.x - self.width//2, self.y - 5)
        ])
        pygame.draw.polygon(screen, BLUE, [
            (self.x + self.width//2, self.y + self.height//2),
            (self.x + self.width//2 + 10, self.y),
            (self.x + self.width//2, self.y - 5)
        ])
        
        if self.shield > 0:
            shield_radius = 30 + int(5 * math.sin(pygame.time.get_ticks() * 0.01))
            shield_surf = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (0, 100, 255, 100), (shield_radius, shield_radius), shield_radius)
            pygame.draw.circle(shield_surf, (255, 255, 255, 150), (shield_radius, shield_radius), shield_radius, 2)
            screen.blit(shield_surf, (self.x - shield_radius, self.y - shield_radius))

    def move(self, keys):
        speed = self.speed + (self.upgrades["speed"] * 0.5)
        if keys[pygame.K_LEFT] and self.x > self.width//2:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width//2:
            self.x += speed
        if keys[pygame.K_UP] and self.y > self.height//2:
            self.y -= speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height//2:
            self.y += speed
            
        if self.invincible > 0:
            self.invincible -= 1

    def shoot(self, bullets):
        current_time = pygame.time.get_ticks()
        actual_delay = max(50, self.shoot_delay - (self.upgrades["fire_rate"] * 20))
        
        if current_time - self.last_shot > actual_delay:
            damage = 1 + self.upgrades["damage"]
            
            if self.weapon_type == WeaponType.SINGLE:
                bullets.append(Bullet(self.x, self.y - self.height//2, damage))
            elif self.weapon_type == WeaponType.DOUBLE:
                bullets.append(Bullet(self.x - 10, self.y - self.height//2, damage))
                bullets.append(Bullet(self.x + 10, self.y - self.height//2, damage))
            elif self.weapon_type == WeaponType.TRIPLE:
                bullets.append(Bullet(self.x - 15, self.y - self.height//2, damage))
                bullets.append(Bullet(self.x, self.y - self.height//2, damage))
                bullets.append(Bullet(self.x + 15, self.y - self.height//2, damage))
            elif self.weapon_type == WeaponType.SPREAD:
                bullets.append(Bullet(self.x, self.y - self.height//2, damage, angle=-15))
                bullets.append(Bullet(self.x, self.y - self.height//2, damage, angle=0))
                bullets.append(Bullet(self.x, self.y - self.height//2, damage, angle=15))
            elif self.weapon_type == WeaponType.LASER:
                bullets.append(LaserBeam(self.x, self.y - self.height//2, damage))
            
            self.last_shot = current_time
            return True
        return False

    def take_damage(self, amount):
        if self.invincible > 0:
            return
            
        if self.shield > 0:
            self.shield -= amount
            if self.shield < 0:
                self.health += self.shield
                self.shield = 0
        else:
            self.health -= amount
            self.invincible = 60

# ADD THE MISSING BULLET CLASS HERE
class Bullet:
    def __init__(self, x, y, damage=1, angle=0):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 7
        self.damage = damage
        self.angle = angle
        self.color = YELLOW if damage == 1 else ORANGE if damage == 2 else RED
        self.trail = []

    def draw(self):
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = 255 - (i * 30)
            if alpha > 0:
                trail_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*self.color, alpha), (self.radius, self.radius), self.radius)
                screen.blit(trail_surf, (trail_x - self.radius, trail_y - self.radius))
        
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 1)

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        
        rad_angle = math.radians(self.angle)
        self.x += self.speed * math.sin(rad_angle)
        self.y -= self.speed * math.cos(rad_angle)

# ADD THE MISSING LASERBEAM CLASS HERE
class LaserBeam:
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.width = 6
        self.height = 30
        self.damage = damage
        self.speed = 10
        self.active = True
        self.timer = 30

    def draw(self):
        if self.active:
            pygame.draw.rect(screen, CYAN, (self.x - self.width//2, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLUE, (self.x - self.width//4, self.y, self.width//2, self.height))
            pygame.draw.circle(screen, WHITE, (self.x, self.y), self.width//2)

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
        self.y -= self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y, self.width, self.height)

# Enhanced Enemy class with unique visual designs
class Enemy:
    def __init__(self, enemy_type, level=1):
        self.type = enemy_type
        self.level = level
        
        level_multiplier = 1 + (level * 0.2)
        
        if enemy_type == EnemyType.BASIC:
            self.width = 45
            self.height = 35
            self.speed = random.uniform(1.0, 2.0) * level_multiplier
            self.health = 1
            self.max_health = 1
            self.color = (200, 50, 50)  # Reddish
            self.secondary_color = (150, 150, 150)  # Gray
            self.value = int(10 * level_multiplier)
            self.shoot_chance = 0
            
        elif enemy_type == EnemyType.FAST:
            self.width = 35
            self.height = 25
            self.speed = random.uniform(2.0, 3.5) * level_multiplier
            self.health = 1
            self.max_health = 1
            self.color = (180, 70, 200)  # Purple
            self.secondary_color = (220, 180, 220)  # Light purple
            self.value = int(15 * level_multiplier)
            self.shoot_chance = 0.01 * level_multiplier
            
        elif enemy_type == EnemyType.TANK:
            self.width = 65
            self.height = 50
            self.speed = random.uniform(0.5, 1.5) * level_multiplier
            self.health = int((3 + level) * level_multiplier)
            self.max_health = int((3 + level) * level_multiplier)
            self.color = (100, 30, 30)  # Dark red
            self.secondary_color = (150, 100, 100)  # Brownish
            self.value = int(25 * level_multiplier)
            self.shoot_chance = 0.02 * level_multiplier
            
        elif enemy_type == EnemyType.SHOOTER:
            self.width = 40
            self.height = 40
            self.speed = random.uniform(1.0, 1.5) * level_multiplier
            self.health = int(2 * level_multiplier)
            self.max_health = int(2 * level_multiplier)
            self.color = (220, 120, 0)  # Orange
            self.secondary_color = (255, 200, 100)  # Light orange
            self.value = int(20 * level_multiplier)
            self.shoot_chance = 0.05 * level_multiplier
            
        elif enemy_type == EnemyType.BOSS:
            self.width = 160 + (level * 10)
            self.height = 110 + (level * 8)
            self.speed = (0.5 + (level * 0.1)) * level_multiplier
            self.health = int((50 + (level * 30)) * level_multiplier)
            self.max_health = int((50 + (level * 30)) * level_multiplier)
            self.color = (255, 200, 0)  # Gold
            self.secondary_color = (255, 100, 0)  # Orange
            self.value = int(500 * level_multiplier)
            self.shoot_chance = 0.1 * level_multiplier
            self.attack_pattern = 0
            self.attack_timer = 0
            self.movement_timer = 0
        
        self.x = random.randint(self.width, WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.hit_effect = 0
        self.last_shot = 0
        self.engine_pulse = 0

    def draw(self):
        if self.hit_effect > 0:
            pygame.draw.circle(screen, WHITE, (self.x, self.y), self.width + self.hit_effect, 3)
            self.hit_effect -= 1
        
        # Engine pulse effect
        self.engine_pulse = (self.engine_pulse + 0.2) % (2 * math.pi)
        engine_glow = int(10 + 5 * math.sin(self.engine_pulse))
        
        if self.type == EnemyType.BASIC:
            # Saucer shape for basic enemies
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.width//2)
            pygame.draw.circle(screen, self.secondary_color, (self.x, self.y), self.width//3)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.width//6)
            
            # Engine glow
            pygame.draw.circle(screen, YELLOW, (self.x - 15, self.y + 10), 3 + engine_glow//3)
            pygame.draw.circle(screen, YELLOW, (self.x + 15, self.y + 10), 3 + engine_glow//3)
            
        elif self.type == EnemyType.FAST:
            # Arrow shape for fast enemies
            pygame.draw.polygon(screen, self.color, [
                (self.x, self.y - self.height//2),
                (self.x - self.width//2, self.y + self.height//2),
                (self.x + self.width//2, self.y + self.height//2)
            ])
            pygame.draw.polygon(screen, self.secondary_color, [
                (self.x, self.y - self.height//4),
                (self.x - self.width//4, self.y + self.height//4),
                (self.x + self.width//4, self.y + self.height//4)
            ])
            
            # Engine glow
            pygame.draw.circle(screen, CYAN, (self.x, self.y + self.height//2 + 5), 4 + engine_glow//2)
            
        elif self.type == EnemyType.TANK:
            # Heavy armored look for tanks
            pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height), border_radius=8)
            pygame.draw.rect(screen, self.secondary_color, (self.x - self.width//3, self.y - self.height//3, self.width*2//3, self.height*2//3), border_radius=5)
            
            # Armor plates
            pygame.draw.rect(screen, SILVER, (self.x - self.width//2 + 5, self.y - self.height//2 + 5, self.width - 10, 8))
            pygame.draw.rect(screen, SILVER, (self.x - self.width//2 + 5, self.y + self.height//2 - 13, self.width - 10, 8))
            
            # Engine glow
            for i in range(3):
                offset = -10 + i * 10
                pygame.draw.circle(screen, RED, (self.x + offset, self.y + self.height//2 + 5), 3 + engine_glow//3)
            
        elif self.type == EnemyType.SHOOTER:
            # Gun turret design for shooters
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.width//2)
            pygame.draw.rect(screen, self.secondary_color, (self.x - self.width//4, self.y - self.height//4, self.width//2, self.height//2))
            
            # Gun barrels
            pygame.draw.rect(screen, SILVER, (self.x - 15, self.y - 20, 8, 15))
            pygame.draw.rect(screen, SILVER, (self.x + 7, self.y - 20, 8, 15))
            
            # Engine glow
            pygame.draw.circle(screen, ORANGE, (self.x, self.y + self.height//2 + 5), 4 + engine_glow//2)
            
        elif self.type == EnemyType.BOSS:
            # Massive battleship design for boss
            # Main body
            pygame.draw.ellipse(screen, self.color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
            
            # Secondary color details
            pygame.draw.ellipse(screen, self.secondary_color, (self.x - self.width//3, self.y - self.height//3, self.width*2//3, self.height*2//3))
            
            # Bridge/tower
            pygame.draw.rect(screen, DARK_BLUE, (self.x - 20, self.y - self.height//2 - 10, 40, 20))
            
            # Weapon turrets
            pygame.draw.circle(screen, SILVER, (self.x - 40, self.y - 10), 12)
            pygame.draw.circle(screen, SILVER, (self.x + 40, self.y - 10), 12)
            pygame.draw.circle(screen, SILVER, (self.x - 60, self.y + 10), 10)
            pygame.draw.circle(screen, SILVER, (self.x + 60, self.y + 10), 10)
            
            # Engine glow
            for i in range(5):
                offset = -40 + i * 20
                glow_size = 5 + engine_glow//2
                pygame.draw.circle(screen, RED, (self.x + offset, self.y + self.height//2 + 5), glow_size)
            
            # Boss level indicator
            level_text = small_font.render(f"BOSS LVL {self.level}", True, WHITE)
            screen.blit(level_text, (self.x - level_text.get_width()//2, self.y - self.height//2 - 30))
        
        # Health bar for enemies with more than 1 health
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 5
            health_ratio = self.health / self.max_health
            health_color = GREEN if health_ratio > 0.5 else YELLOW if health_ratio > 0.25 else RED
            
            pygame.draw.rect(screen, RED, (self.x - bar_width//2, self.y - self.height//2 - 10, bar_width, bar_height))
            pygame.draw.rect(screen, health_color, (self.x - bar_width//2, self.y - self.height//2 - 10, bar_width * health_ratio, bar_height))

    def update(self):
        if self.type == EnemyType.BOSS:
            self.movement_timer += 1
            self.attack_timer += 1
            
            if self.movement_timer > 180:
                self.attack_pattern = random.randint(0, 2)
                self.movement_timer = 0
                
            if self.attack_pattern == 0:
                self.x += math.sin(pygame.time.get_ticks() * 0.005) * 3
                self.y += 0.5
            elif self.attack_pattern == 1:
                t = pygame.time.get_ticks() * 0.002
                self.x = WIDTH//2 + math.sin(t) * 150
                self.y = 100 + math.sin(2*t) * 50
            elif self.attack_pattern == 2:
                self.y += 1
                if self.y > 150:
                    self.y = 150
        else:
            self.y += self.speed

    def shoot(self, enemy_bullets):
        if random.random() < self.shoot_chance and pygame.time.get_ticks() - self.last_shot > 1000:
            if self.type == EnemyType.BOSS:
                if self.attack_timer > 120:
                    self.attack_pattern = random.randint(0, 2)
                    self.attack_timer = 0
                
                if self.attack_pattern == 0:
                    for angle in range(-45, 46, 15):
                        enemy_bullets.append(EnemyBullet(self.x, self.y + self.height//2, angle))
                elif self.attack_pattern == 1:
                    enemy_bullets.append(EnemyBullet(self.x - 40, self.y + self.height//2))
                    enemy_bullets.append(EnemyBullet(self.x + 40, self.y + self.height//2))
                    enemy_bullets.append(EnemyBullet(self.x, self.y + self.height//2))
                else:
                    for angle in range(0, 360, 30):
                        enemy_bullets.append(EnemyBullet(self.x, self.y + self.height//2, angle))
            else:
                enemy_bullets.append(EnemyBullet(self.x, self.y + self.height//2))
            
            self.last_shot = pygame.time.get_ticks()
            return True
        return False

# Enemy bullets
class EnemyBullet:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.radius = 3
        self.speed = 4
        self.angle = angle
        self.color = RED

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius - 1)

    def update(self):
        rad_angle = math.radians(self.angle)
        self.x += self.speed * math.sin(rad_angle)
        self.y += self.speed * math.cos(rad_angle)

# Power-up class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 2
        self.type = power_type
        self.colors = {1: GREEN, 2: BLUE, 3: YELLOW, 4: CYAN, 5: GOLD}
        self.symbols = {1: "H", 2: "W", 3: "L", 4: "S", 5: "$"}
        self.pulse = 0
        self.pulse_dir = 1

    def draw(self):
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0:
            self.pulse_dir *= -1
        
        pulse_radius = self.radius + int(3 * self.pulse)
        color = self.colors[self.type]
        
        pygame.draw.circle(screen, color, (self.x, self.y), pulse_radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), pulse_radius, 2)
        
        symbol_text = game_font.render(self.symbols[self.type], True, WHITE)
        symbol_rect = symbol_text.get_rect(center=(self.x, self.y))
        screen.blit(symbol_text, symbol_rect)

    def update(self):
        self.y += self.speed

# Particle effect class
class Particle:
    def __init__(self, x, y, color, size=None, life=None):
        self.x = x
        self.y = y
        self.color = color
        self.size = size or random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = life or random.randint(20, 40)
        self.initial_life = self.life

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self):
        if self.life > 0:
            alpha = int(255 * (self.life / self.initial_life))
            particle_surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*self.color, alpha), (self.size, self.size), self.size)
            screen.blit(particle_surf, (self.x - self.size, self.y - self.size))

# Game class
class Game:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.player = Player()
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []
        self.power_ups = []
        self.clock = pygame.time.Clock()
        self.enemy_spawn_timer = 0
        self.level = 1
        self.score = 0
        self.sound_manager = SoundManager()
        self.boss_active = False
        self.level_transition_timer = 0
        self.enemies_killed_this_level = 0
        self.enemies_needed_for_boss = 15 + (self.level * 2)
        self.wave = 1
        self.wave_size = 5 + self.level
        self.wave_enemies_spawned = 0
        self.wave_complete = False
        self.difficulty_timer = 0
        self.difficulty_interval = 10000
        
        # Enhanced background stars
        self.stars = []
        for _ in range(300):
            star_color = random.choice([WHITE, LIGHT_BLUE, YELLOW, CYAN])
            self.stars.append((
                random.randint(0, WIDTH), 
                random.randint(0, HEIGHT), 
                random.randint(1, 3), 
                random.random()*0.3,
                star_color
            ))
        
        # Create icons for buttons
        self.icons = self.create_icons()
        
        # Menu buttons
        button_width, button_height = 300, 60
        center_x = WIDTH // 2 - button_width // 2
        self.menu_buttons = [
            Button(center_x, 220, button_width, button_height, "Start Mission", BLUE, CYAN, self.icons["play"]),
            Button(center_x, 300, button_width, button_height, "Upgrade Hangar", PURPLE, (255, 100, 255), self.icons["upgrade"]),
            Button(center_x, 380, button_width, button_height, "Mission Briefing", ORANGE, YELLOW, self.icons["about"]),
            Button(center_x, 460, button_width, button_height, "Quit Game", RED, (255, 100, 100), self.icons["quit"])
        ]
        
        self.settings_buttons = [
            Button(center_x, 250, button_width, button_height, "Sound: ON", BLUE, CYAN),
            Button(center_x, 330, button_width, button_height, "Back to Menu", PURPLE, (255, 100, 255))
        ]
        
        self.game_over_buttons = [
            Button(center_x, 350, button_width, button_height, "Try Again", GREEN, CYAN),
            Button(center_x, 430, button_width, button_height, "Main Menu", BLUE, PURPLE)
        ]
        
        self.pause_buttons = [
            Button(center_x, 250, button_width, button_height, "Resume Mission", GREEN, CYAN),
            Button(center_x, 330, button_width, button_height, "Main Menu", BLUE, PURPLE)
        ]
        
        self.upgrade_buttons = [
            Button(center_x, 200, button_width, button_height, "Speed Upgrade", BLUE, CYAN),
            Button(center_x, 280, button_width, button_height, "Health Upgrade", GREEN, (100, 255, 100)),
            Button(center_x, 360, button_width, button_height, "Damage Upgrade", RED, (255, 100, 100)),
            Button(center_x, 440, button_width, button_height, "Fire Rate Upgrade", ORANGE, YELLOW),
            Button(center_x, 520, button_width, button_height, "Back to Menu", PURPLE, (255, 100, 255))
        ]

    def create_icons(self):
        icons = {}
        
        # Play icon (triangle)
        play_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(play_icon, WHITE, [(5, 5), (5, 25), (25, 15)])
        icons["play"] = play_icon
        
        # Upgrade icon (wrench)
        upgrade_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(upgrade_icon, WHITE, (10, 5, 5, 20), border_radius=2)
        pygame.draw.rect(upgrade_icon, WHITE, (15, 10, 10, 5), border_radius=2)
        icons["upgrade"] = upgrade_icon
        
        # About icon (info)
        about_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(about_icon, WHITE, (15, 15), 12, 2)
        pygame.draw.rect(about_icon, WHITE, (14, 10, 2, 8))
        pygame.draw.rect(about_icon, WHITE, (14, 20, 2, 2))
        icons["about"] = about_icon
        
        # Quit icon (X)
        quit_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.line(quit_icon, WHITE, (5, 5), (25, 25), 3)
        pygame.draw.line(quit_icon, WHITE, (25, 5), (5, 25), 3)
        icons["quit"] = quit_icon
        
        return icons

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []
        self.power_ups = []
        self.enemy_spawn_timer = 0
        self.level = 1
        self.score = 0
        self.boss_active = False
        self.level_transition_timer = 0
        self.enemies_killed_this_level = 0
        self.enemies_needed_for_boss = 15 + (self.level * 2)
        self.wave = 1
        self.wave_size = 5 + self.level
        self.wave_enemies_spawned = 0
        self.wave_complete = False
        self.difficulty_timer = 0

    def spawn_enemy(self):
        if self.boss_active:
            return
            
        if self.wave_enemies_spawned < self.wave_size:
            enemy_type_roll = random.random()
            enemy_type = EnemyType.BASIC
            
            if self.level >= 8 and enemy_type_roll < 0.15:
                enemy_type = EnemyType.SHOOTER
            elif self.level >= 6 and enemy_type_roll < 0.25:
                enemy_type = EnemyType.TANK
            elif self.level >= 4 and enemy_type_roll < 0.35:
                enemy_type = EnemyType.FAST
            elif enemy_type_roll < 0.5:
                enemy_type = EnemyType.BASIC
            else:
                if self.level >= 10:
                    enemy_type = random.choice([EnemyType.FAST, EnemyType.SHOOTER, EnemyType.TANK])
                elif self.level >= 7:
                    enemy_type = random.choice([EnemyType.FAST, EnemyType.SHOOTER])
                elif self.level >= 5:
                    enemy_type = random.choice([EnemyType.FAST, EnemyType.BASIC])
                else:
                    enemy_type = EnemyType.BASIC
                    
            self.enemies.append(Enemy(enemy_type, self.level))
            self.wave_enemies_spawned += 1

    def spawn_boss(self):
        if not self.boss_active:
            self.boss_active = True
            boss = Enemy(EnemyType.BOSS, self.level)
            boss.x = WIDTH // 2
            boss.y = -100
            self.enemies.append(boss)
            
            for _ in range(100):
                self.particles.append(Particle(WIDTH//2, 0, GOLD, size=random.randint(3, 8), life=random.randint(40, 80)))

    def spawn_power_up(self, x, y):
        power_type_roll = random.random()
        
        if power_type_roll < 0.4:
            power_type = 1
        elif power_type_roll < 0.65:
            power_type = 2
        elif power_type_roll < 0.8:
            power_type = 4
        elif power_type_roll < 0.95:
            power_type = 5
        else:
            power_type = 3
            
        self.power_ups.append(PowerUp(x, y, power_type))

    def check_collisions(self):
        # Bullet-enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if hasattr(bullet, 'active') and not bullet.active:
                    continue
                    
                distance = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                collision_distance = enemy.width//2 + (bullet.radius if hasattr(bullet, 'radius') else bullet.width//2)
                
                if distance < collision_distance:
                    enemy.health -= bullet.damage
                    enemy.hit_effect = 10
                    
                    for _ in range(5):
                        self.particles.append(Particle(enemy.x, enemy.y, enemy.color))
                    
                    if enemy.health <= 0:
                        for _ in range(20):
                            self.particles.append(Particle(enemy.x, enemy.y, RED))
                        for _ in range(10):
                            self.particles.append(Particle(enemy.x, enemy.y, YELLOW))
                        
                        if random.random() < 0.3:
                            self.spawn_power_up(enemy.x, enemy.y)
                        
                        self.score += enemy.value
                        self.player.kill_count += 1
                        self.player.money += enemy.value // 5
                        self.enemies_killed_this_level += 1
                        
                        if enemy.type == EnemyType.BOSS:
                            self.boss_active = False
                            self.level += 1
                            self.state = GameState.LEVEL_TRANSITION
                            self.level_transition_timer = 180
                            self.wave = 1
                            self.wave_size = 5 + self.level
                            self.wave_enemies_spawned = 0
                            self.wave_complete = False
                            self.enemies_killed_this_level = 0
                            self.enemies_needed_for_boss = 15 + (self.level * 2)
                        
                        self.enemies.remove(enemy)
                    
                    if hasattr(bullet, 'active'):
                        bullet.active = False
                    else:
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                    break

        # Player-enemy collisions
        for enemy in self.enemies[:]:
            if self.player.invincible > 0:
                continue
                
            distance = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
            if distance < enemy.width//2 + self.player.width//2:
                for _ in range(30):
                    self.particles.append(Particle(enemy.x, enemy.y, RED))
                
                self.enemies.remove(enemy)
                self.player.take_damage(10 if enemy.type != EnemyType.BOSS else 25)
                
                if self.player.health <= 0:
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = GameState.GAME_OVER
                    else:
                        self.player.health = self.player.max_health

        # Player-enemy bullet collisions
        for bullet in self.enemy_bullets[:]:
            if self.player.invincible > 0:
                continue
                
            distance = math.sqrt((self.player.x - bullet.x)**2 + (self.player.y - bullet.y)**2)
            if distance < self.player.width//2 + bullet.radius:
                self.enemy_bullets.remove(bullet)
                self.player.take_damage(5)
                
                if self.player.health <= 0:
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = GameState.GAME_OVER
                    else:
                        self.player.health = self.player.max_health

        # Player-power-up collisions
        for power_up in self.power_ups[:]:
            distance = math.sqrt((self.player.x - power_up.x)**2 + (self.player.y - power_up.y)**2)
            if distance < power_up.radius + self.player.width//2:
                if power_up.type == 1:
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif power_up.type == 2:
                    weapons = [WeaponType.SINGLE, WeaponType.DOUBLE, WeaponType.TRIPLE, WeaponType.SPREAD, WeaponType.LASER]
                    current_index = list(weapons).index(self.player.weapon_type) if self.player.weapon_type in weapons else 0
                    self.player.weapon_type = weapons[(current_index + 1) % len(weapons)]
                elif power_up.type == 3:
                    self.player.lives += 1
                elif power_up.type == 4:
                    self.player.shield = 50
                elif power_up.type == 5:
                    self.player.money += 25
                
                self.power_ups.remove(power_up)

    def update(self):
        if self.state == GameState.PLAYING:
            # Progressive difficulty
            self.difficulty_timer += self.clock.get_time()
            if self.difficulty_timer > self.difficulty_interval:
                self.difficulty_timer = 0
                for enemy in self.enemies:
                    enemy.speed *= 1.05
                    enemy.shoot_chance = min(0.3, enemy.shoot_chance * 1.1)

            # Player movement
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            
            # Auto-shooting
            if keys[pygame.K_SPACE]:
                self.player.shoot(self.bullets)
            
            if self.player.power_timer > 0:
                self.player.power_timer -= self.clock.get_time()

            # Enemy spawning logic
            if not self.boss_active:
                self.enemy_spawn_timer += 1
                spawn_rate = max(5, 25 - self.level * 2)
                
                if self.enemies_killed_this_level >= self.enemies_needed_for_boss and len(self.enemies) == 0:
                    self.spawn_boss()
                elif self.enemy_spawn_timer >= spawn_rate and self.wave_enemies_spawned < self.wave_size:
                    self.spawn_enemy()
                    self.enemy_spawn_timer = 0
                
                if self.wave_enemies_spawned >= self.wave_size and len(self.enemies) == 0 and not self.boss_active:
                    self.wave_complete = True
                    self.wave += 1
                    self.wave_size = 5 + self.level + (self.wave * 2)
                    self.wave_enemies_spawned = 0
                    self.wave_complete = False

            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                if hasattr(bullet, 'active') and not bullet.active:
                    self.bullets.remove(bullet)
                elif bullet.y < 0 or bullet.y > HEIGHT or bullet.x < 0 or bullet.x > WIDTH:
                    self.bullets.remove(bullet)

            # Update enemy bullets
            for bullet in self.enemy_bullets[:]:
                bullet.update()
                if bullet.y > HEIGHT or bullet.x < 0 or bullet.x > WIDTH:
                    self.enemy_bullets.remove(bullet)

            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update()
                enemy.shoot(self.enemy_bullets)
                
                if enemy.y > HEIGHT + 100:
                    self.enemies.remove(enemy)
                    if not self.boss_active:
                        self.player.health -= 5

            # Update power-ups
            for power_up in self.power_ups[:]:
                power_up.update()
                if power_up.y > HEIGHT + 50:
                    self.power_ups.remove(power_up)

            # Update particles
            for particle in self.particles[:]:
                particle.update()
                if particle.life <= 0:
                    self.particles.remove(particle)

            # Check collisions
            self.check_collisions()

        elif self.state == GameState.LEVEL_TRANSITION:
            self.level_transition_timer -= 1
            if self.level_transition_timer <= 0:
                self.state = GameState.PLAYING

    def draw_beautiful_menu_background(self):
        for y in range(HEIGHT):
            color_value = int(50 * (1 - y/HEIGHT))
            color = (color_value, color_value, color_value + 50)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        
        for i, (x, y, size, speed, color) in enumerate(self.stars):
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            self.stars[i] = (x, (y + speed) % HEIGHT, size, speed, color)
        
        for i in range(5):
            alpha = int(50 + 20 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            radius = 100 + i * 30
            x = WIDTH//2 + math.cos(pygame.time.get_ticks() * 0.0005 + i) * 50
            y = HEIGHT//3 + math.sin(pygame.time.get_ticks() * 0.0007 + i) * 30
            
            nebula_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(nebula_surf, (100, 50, 150, alpha), (radius, radius), radius)
            screen.blit(nebula_surf, (x - radius, y - radius))

    def draw_main_menu(self):
        self.draw_beautiful_menu_background()
        
        glow_size = 5 + 3 * math.sin(pygame.time.get_ticks() * 0.005)
        title_text = title_font.render("GALAXY DEFENDER", True, CYAN)
        
        for i in range(int(glow_size), 0, -1):
            alpha = 100 - i * (100 // int(glow_size))
            glow_text = title_font.render("GALAXY DEFENDER", True, (0, 255, 255, alpha))
            glow_rect = glow_text.get_rect(center=(WIDTH//2, 100))
            screen.blit(glow_text, glow_rect)
        
        title_rect = title_text.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        subtitle_text = menu_font.render("Ultimate Space Shooter", True, YELLOW)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, 160))
        screen.blit(subtitle_text, subtitle_rect)
        
        for button in self.menu_buttons:
            button.draw(screen)
        
        high_score_text = game_font.render(f"High Score: {self.score}", True, YELLOW)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, 550))

    def draw_upgrade_shop(self):
        self.draw_beautiful_menu_background()
        
        title_text = title_font.render("UPGRADE HANGAR", True, GOLD)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        money_text = menu_font.render(f"Space Credits: ${self.player.money}", True, YELLOW)
        screen.blit(money_text, (WIDTH//2 - money_text.get_width()//2, 120))
        
        upgrade_info = [
            ("Speed", self.player.upgrades["speed"], 100 * (2 ** (self.player.upgrades["speed"] - 1))),
            ("Health", self.player.upgrades["health"], 100 * (2 ** (self.player.upgrades["health"] - 1))),
            ("Damage", self.player.upgrades["damage"], 150 * (2 ** (self.player.upgrades["damage"] - 1))),
            ("Fire Rate", self.player.upgrades["fire_rate"], 120 * (2 ** (self.player.upgrades["fire_rate"] - 1))),
        ]
        
        for i, (name, level, price) in enumerate(upgrade_info):
            button = self.upgrade_buttons[i]
            button.text = f"{name} Upgrade (Lvl {level}) - ${price}"
            button.draw(screen)
            
            stat_value = ""
            if name == "Speed":
                stat_value = f"Current: {5 + (level * 0.5):.1f}"
            elif name == "Health":
                stat_value = f"Current: {100 + ((level-1) * 20)}"
            elif name == "Damage":
                stat_value = f"Current: {1 + level}x"
            elif name == "Fire Rate":
                stat_value = f"Current: {200 - (level * 20)}ms"
                
            value_text = small_font.render(stat_value, True, WHITE)
            screen.blit(value_text, (button.rect.right + 10, button.rect.centery - value_text.get_height()//2))
            
            if self.player.money >= price:
                afford_text = small_font.render("CAN AFFORD", True, GREEN)
            else:
                afford_text = small_font.render("INSUFFICIENT FUNDS", True, RED)
            
            screen.blit(afford_text, (button.rect.right + 10, button.rect.centery + 15))
        
        self.upgrade_buttons[4].draw(screen)

    def draw_settings(self):
        self.draw_beautiful_menu_background()
        
        title_text = title_font.render("SETTINGS", True, CYAN)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))
        
        sound_status = "ON" if self.sound_manager.sounds_enabled else "OFF"
        self.settings_buttons[0].text = f"Sound Effects: {sound_status}"
        
        for button in self.settings_buttons:
            button.draw(screen)

    def draw_about(self):
        self.draw_beautiful_menu_background()
        
        title_text = title_font.render("MISSION BRIEFING", True, CYAN)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))
        
        about_lines = [
            "GALAXY DEFENDER - ULTIMATE SPACE SHOOTER",
            "",
            "ENEMY TYPES:",
            "• SAUCERS - Basic enemy units",
            "• INTERCEPTORS - Fast but fragile", 
            "• BATTLESHIPS - Heavy armor, slow moving",
            "• GUNSHIPS - Attacks from distance",
            "• MOTHERSHIPS - Massive capital ships",
            "",
            "CONTROLS:",
            "Arrow Keys - Navigate your ship",
            "Spacebar - Fire weapons (hold for auto-fire)",
            "P - Pause mission",
            "ESC - Return to command center"
        ]
        
        for i, line in enumerate(about_lines):
            color = YELLOW if line.startswith("GALAXY") else CYAN if line.startswith("ENEMY") or line.startswith("CONTROLS") else WHITE
            text = small_font.render(line, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 25))
        
        back_button = Button(WIDTH//2 - 150, 530, 300, 50, "Back to Command Center", BLUE, PURPLE)
        back_button.draw(screen)

    def draw_game(self):
        screen.fill(BLACK)
        
        for i, (x, y, size, speed, color) in enumerate(self.stars):
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            if self.state == GameState.PLAYING:
                self.stars[i] = (x, (y + speed) % HEIGHT, size, speed, color)

        for particle in self.particles:
            particle.draw()
        
        for enemy in self.enemies:
            enemy.draw()
        
        for bullet in self.bullets:
            bullet.draw()
            
        for bullet in self.enemy_bullets:
            bullet.draw()
        
        for power_up in self.power_ups:
            power_up.draw()
        
        self.player.draw()

        # Draw UI
        ui_bg = pygame.Surface((250, 200), pygame.SRCALPHA)
        ui_bg.fill((0, 0, 0, 150))
        screen.blit(ui_bg, (5, 5))
        
        health_ratio = self.player.health / self.player.max_health
        health_width = 200 * health_ratio
        health_color = GREEN if health_ratio > 0.5 else YELLOW if health_ratio > 0.25 else RED
        
        pygame.draw.rect(screen, RED, (15, 15, 200, 20))
        pygame.draw.rect(screen, health_color, (15, 15, health_width, 20))
        pygame.draw.rect(screen, WHITE, (15, 15, 200, 20), 2)
        
        health_text = game_font.render(f"SHIELD: {self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (20, 40))
        
        stats = [
            f"LEVEL: {self.level}",
            f"SCORE: {self.score}",
            f"LIVES: {self.player.lives}",
            f"CREDITS: ${self.player.money}",
            f"KILLS: {self.enemies_killed_this_level}/{self.enemies_needed_for_boss}",
            f"WAVE: {self.wave}"
        ]
        
        for i, stat in enumerate(stats):
            text = game_font.render(stat, True, WHITE)
            screen.blit(text, (15, 70 + i * 25))
        
        weapon_names = {
            WeaponType.SINGLE: "SINGLE LASER",
            WeaponType.DOUBLE: "DUAL CANNONS", 
            WeaponType.TRIPLE: "TRIPLE BLAST",
            WeaponType.SPREAD: "SPREAD SHOT",
            WeaponType.LASER: "BEAM CANNON"
        }
        
        weapon_text = game_font.render(f"WEAPON: {weapon_names[self.player.weapon_type]}", True, CYAN)
        screen.blit(weapon_text, (WIDTH - weapon_text.get_width() - 15, 15))
        
        if self.player.shield > 0:
            shield_text = game_font.render(f"SHIELD: {self.player.shield}", True, BLUE)
            screen.blit(shield_text, (WIDTH - shield_text.get_width() - 15, 45))
        
        if self.boss_active:
            warning_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
            warning_surf = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
            warning_surf.fill((255, 0, 0, warning_alpha))
            screen.blit(warning_surf, (0, HEIGHT//2 - 30))
            
            warning_text = title_font.render("MOTHERSHIP INCOMING!", True, WHITE)
            screen.blit(warning_text, (WIDTH//2 - warning_text.get_width()//2, HEIGHT//2 - 25))

    def draw_level_transition(self):
        self.draw_game()
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        level_text = title_font.render(f"LEVEL {self.level} COMPLETE!", True, YELLOW)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 80))
        
        stats_text = menu_font.render(f"Score: {self.score}  Credits: ${self.player.money}", True, WHITE)
        screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, HEIGHT//2 - 10))
        
        next_level_text = menu_font.render(f"Next Mission: LEVEL {self.level + 1}", True, GREEN)
        screen.blit(next_level_text, (WIDTH//2 - next_level_text.get_width()//2, HEIGHT//2 + 40))
        
        progress = 1.0 - (self.level_transition_timer / 180)
        pygame.draw.rect(screen, DARK_BLUE, (WIDTH//2 - 150, HEIGHT//2 + 80, 300, 20))
        pygame.draw.rect(screen, CYAN, (WIDTH//2 - 150, HEIGHT//2 + 80, 300 * progress, 20))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 150, HEIGHT//2 + 80, 300, 20), 2)

    def draw_game_over(self):
        self.draw_beautiful_menu_background()
        
        title_text = title_font.render("MISSION FAILED", True, RED)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 150))
        
        score_text = menu_font.render(f"Final Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 250))
        
        level_text = menu_font.render(f"Level Reached: {self.level}", True, CYAN)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 300))
        
        for button in self.game_over_buttons:
            button.draw(screen)

    def draw_pause(self):
        self.draw_game()
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = title_font.render("MISSION PAUSED", True, YELLOW)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, 150))
        
        for button in self.pause_buttons:
            button.draw(screen)

    def draw(self):
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.ABOUT:
            self.draw_about()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.PAUSED:
            self.draw_pause()
        elif self.state == GameState.LEVEL_TRANSITION:
            self.draw_level_transition()
        elif self.state == GameState.UPGRADE_SHOP:
            self.draw_upgrade_shop()

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING or self.state == GameState.PAUSED:
                            self.state = GameState.MAIN_MENU
                        elif self.state in [GameState.SETTINGS, GameState.ABOUT, GameState.UPGRADE_SHOP]:
                            self.state = GameState.MAIN_MENU
                    
                    if event.key == pygame.K_p and self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_p and self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
            
            if self.state == GameState.MAIN_MENU:
                for i, button in enumerate(self.menu_buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if i == 0:
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif i == 1:
                            self.state = GameState.UPGRADE_SHOP
                        elif i == 2:
                            self.state = GameState.ABOUT
                        elif i == 3:
                            running = False
            
            elif self.state == GameState.UPGRADE_SHOP:
                for i, button in enumerate(self.upgrade_buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if i == 0:
                            price = 100 * (2 ** (self.player.upgrades["speed"] - 1))
                            if self.player.money >= price:
                                self.player.money -= price
                                self.player.upgrades["speed"] += 1
                        elif i == 1:
                            price = 100 * (2 ** (self.player.upgrades["health"] - 1))
                            if self.player.money >= price:
                                self.player.money -= price
                                self.player.upgrades["health"] += 1
                                self.player.max_health += 20
                                self.player.health = self.player.max_health
                        elif i == 2:
                            price = 150 * (2 ** (self.player.upgrades["damage"] - 1))
                            if self.player.money >= price:
                                self.player.money -= price
                                self.player.upgrades["damage"] += 1
                        elif i == 3:
                            price = 120 * (2 ** (self.player.upgrades["fire_rate"] - 1))
                            if self.player.money >= price:
                                self.player.money -= price
                                self.player.upgrades["fire_rate"] += 1
                        elif i == 4:
                            self.state = GameState.MAIN_MENU
            
            elif self.state == GameState.SETTINGS:
                for i, button in enumerate(self.settings_buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if i == 0:
                            self.sound_manager.toggle_sounds()
                        elif i == 1:
                            self.state = GameState.MAIN_MENU
            
            elif self.state == GameState.ABOUT:
                back_button = Button(WIDTH//2 - 150, 530, 300, 50, "Back to Command Center", BLUE, PURPLE)
                back_button.check_hover(mouse_pos)
                if back_button.is_clicked(mouse_pos, mouse_click):
                    self.state = GameState.MAIN_MENU
            
            elif self.state == GameState.GAME_OVER:
                for i, button in enumerate(self.game_over_buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if i == 0:
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif i == 1:
                            self.state = GameState.MAIN_MENU
            
            elif self.state == GameState.PAUSED:
                for i, button in enumerate(self.pause_buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if i == 0:
                            self.state = GameState.PLAYING
                        elif i == 1:
                            self.state = GameState.MAIN_MENU
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()