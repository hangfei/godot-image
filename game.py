#!/usr/bin/env python3
import pygame
import sys
import random
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Colors inspired by our GLB assets
BACKGROUND_GREEN = (34, 139, 34)  # Forest green for terrain
TREE_BROWN = (101, 67, 33)       # Tree trunk color
TREE_GREEN = (0, 100, 0)         # Tree foliage
BUILDING_RED = (180, 100, 80)    # Building brick color
PLAYER_BLUE = (0, 100, 255)      # Player (cube) color
SPHERE_PURPLE = (128, 0, 128)    # Sphere object color
CYLINDER_WOOD = (139, 90, 43)    # Cylinder wood color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

class AssetWorld:
    """A 2D representation of our 3D GLB asset world"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("GLB Asset Adventure - WASD Controls")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Camera offset for world scrolling
        self.camera_x = 0
        self.camera_y = 0
        
        # Player (represents our cube asset)
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # World objects (representing our GLB assets)
        self.trees = []        # Tree assets
        self.buildings = []    # Building assets  
        self.spheres = []      # Sphere assets (collectibles)
        self.cylinders = []    # Cylinder assets (obstacles)
        self.terrain_tiles = [] # Terrain representation
        
        # Game state
        self.score = 0
        self.collected_spheres = 0
        self.total_spheres = 0
        
        # Generate world based on our asset types
        self.generate_world()
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def generate_world(self):
        """Generate a world using representations of our GLB assets"""
        
        # Create terrain tiles (representing terrain_hills.glb)
        for x in range(-2000, 2000, 100):
            for y in range(-1500, 1500, 100):
                # Add some variation to terrain height
                height_variation = random.randint(-20, 20)
                self.terrain_tiles.append(TerrainTile(x, y, height_variation))
        
        # Place trees (representing tree_basic.glb)
        for _ in range(150):
            x = random.randint(-1800, 1800)
            y = random.randint(-1300, 1300)
            # Don't place trees too close to spawn point
            if abs(x) > 200 or abs(y) > 200:
                self.trees.append(Tree(x, y))
        
        # Place buildings (representing building_basic.glb)
        for _ in range(30):
            x = random.randint(-1600, 1600)
            y = random.randint(-1100, 1100)
            if abs(x) > 300 or abs(y) > 300:
                self.buildings.append(Building(x, y))
        
        # Place spheres as collectibles (representing sphere_basic.glb)
        for _ in range(25):
            x = random.randint(-1500, 1500)
            y = random.randint(-1000, 1000)
            self.spheres.append(Sphere(x, y))
            self.total_spheres += 1
        
        # Place cylinders as obstacles (representing cylinder_basic.glb)
        for _ in range(40):
            x = random.randint(-1700, 1700)
            y = random.randint(-1200, 1200)
            if abs(x) > 250 or abs(y) > 250:
                self.cylinders.append(Cylinder(x, y))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset world
                    self.__init__()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        # Update player
        self.player.update()
        
        # Update camera to follow player
        self.camera_x = self.player.x - WINDOW_WIDTH // 2
        self.camera_y = self.player.y - WINDOW_HEIGHT // 2
        
        # Check collisions with cylinders (obstacles)
        for cylinder in self.cylinders:
            if self.player.collides_with(cylinder):
                self.player.handle_collision(cylinder)
        
        # Check collisions with buildings (obstacles)
        for building in self.buildings:
            if self.player.collides_with(building):
                self.player.handle_collision(building)
        
        # Check collisions with spheres (collectibles)
        for sphere in self.spheres[:]:
            if self.player.collides_with(sphere):
                self.spheres.remove(sphere)
                self.collected_spheres += 1
                self.score += 100
        
        # Update animated objects
        for sphere in self.spheres:
            sphere.update()
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x - self.camera_x
        screen_y = world_y - self.camera_y
        return screen_x, screen_y
    
    def is_on_screen(self, world_x, world_y, margin=100):
        """Check if object is visible on screen (with margin)"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        return (-margin < screen_x < WINDOW_WIDTH + margin and 
                -margin < screen_y < WINDOW_HEIGHT + margin)
    
    def draw(self):
        self.screen.fill(BACKGROUND_GREEN)
        
        # Draw terrain tiles
        for tile in self.terrain_tiles:
            if self.is_on_screen(tile.x, tile.y, 200):
                tile.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw trees
        for tree in self.trees:
            if self.is_on_screen(tree.x, tree.y, 100):
                tree.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw buildings  
        for building in self.buildings:
            if self.is_on_screen(building.x, building.y, 100):
                building.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw cylinders
        for cylinder in self.cylinders:
            if self.is_on_screen(cylinder.x, cylinder.y, 100):
                cylinder.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw spheres
        for sphere in self.spheres:
            if self.is_on_screen(sphere.x, sphere.y, 100):
                sphere.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw player
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw user interface"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Collectibles progress
        progress_text = self.font.render(f"Spheres: {self.collected_spheres}/{self.total_spheres}", True, WHITE)
        self.screen.blit(progress_text, (10, 50))
        
        # Position
        pos_text = self.small_font.render(f"Position: ({int(self.player.x)}, {int(self.player.y)})", True, WHITE)
        self.screen.blit(pos_text, (10, 90))
        
        # Controls
        controls = [
            "WASD - Move around the world",
            "SPACE - Sprint (faster movement)", 
            "R - Reset world",
            "ESC - Quit"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (WINDOW_WIDTH - 300, 10 + i * 25))
        
        # Win condition
        if self.collected_spheres == self.total_spheres:
            win_text = self.font.render("ALL SPHERES COLLECTED! Press R to restart", True, GOLD)
            text_rect = win_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            # Draw background for text
            pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
            self.screen.blit(win_text, text_rect)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

class Player:
    """Player character (represents cube_basic.glb)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 25
        self.speed = 4
        self.sprint_speed = 7
        
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Determine speed
        current_speed = self.sprint_speed if keys[pygame.K_SPACE] else self.speed
        
        # Movement with WASD
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += current_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += current_speed
    
    def collides_with(self, other):
        """Check collision with another object"""
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return distance < (self.size + other.size) / 2
    
    def handle_collision(self, obstacle):
        """Handle collision with an obstacle by pushing player back"""
        # Calculate push-back direction
        dx = self.x - obstacle.x
        dy = self.y - obstacle.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize and push back
            push_distance = (self.size + obstacle.size) / 2 + 2
            self.x = obstacle.x + (dx / distance) * push_distance
            self.y = obstacle.y + (dy / distance) * push_distance
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw as a blue cube (representing cube_basic.glb)
        pygame.draw.rect(screen, PLAYER_BLUE, 
                        (screen_x - self.size//2, screen_y - self.size//2, self.size, self.size))
        # Add a slight highlight
        pygame.draw.rect(screen, WHITE, 
                        (screen_x - self.size//2, screen_y - self.size//2, self.size, self.size), 2)

class Tree:
    """Tree object (represents tree_basic.glb)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20  # Collision size
        self.height = random.randint(40, 70)
        self.width = random.randint(25, 40)
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw trunk
        trunk_width = 8
        trunk_height = self.height // 2
        pygame.draw.rect(screen, TREE_BROWN, 
                        (screen_x - trunk_width//2, screen_y - trunk_height//2, trunk_width, trunk_height))
        
        # Draw foliage
        pygame.draw.circle(screen, TREE_GREEN, (int(screen_x), int(screen_y - trunk_height//2)), self.width//2)

class Building:
    """Building object (represents building_basic.glb)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 35
        self.width = random.randint(50, 80)
        self.height = random.randint(40, 90)
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw building as rectangle
        pygame.draw.rect(screen, BUILDING_RED, 
                        (screen_x - self.width//2, screen_y - self.height//2, self.width, self.height))
        
        # Add window details
        for i in range(2, self.width-5, 15):
            for j in range(5, self.height-5, 20):
                pygame.draw.rect(screen, YELLOW, 
                               (screen_x - self.width//2 + i, screen_y - self.height//2 + j, 8, 12))

class Sphere:
    """Sphere collectible (represents sphere_basic.glb)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 15
        self.bob_offset = random.uniform(0, 2 * math.pi)
        self.rotation = 0
    
    def update(self):
        self.bob_offset += 0.05
        self.rotation += 0.1
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + math.sin(self.bob_offset) * 5
        
        # Draw as a glowing sphere
        pygame.draw.circle(screen, SPHERE_PURPLE, (int(screen_x), int(screen_y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), self.size, 2)
        # Add inner glow
        pygame.draw.circle(screen, (200, 150, 255), (int(screen_x-3), int(screen_y-3)), self.size//3)

class Cylinder:
    """Cylinder obstacle (represents cylinder_basic.glb)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 25
        self.height = random.randint(30, 50)
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw as cylinder (ellipse with rectangle)
        pygame.draw.ellipse(screen, CYLINDER_WOOD, 
                           (screen_x - self.size, screen_y - self.size//2, self.size*2, self.size))
        # Add wood grain lines
        for i in range(3):
            y_offset = -self.size//2 + i * (self.size//3)
            pygame.draw.ellipse(screen, (120, 80, 40), 
                               (screen_x - self.size + 5, screen_y + y_offset, self.size*2 - 10, 3))

class TerrainTile:
    """Terrain tile (represents terrain_hills.glb)"""
    
    def __init__(self, x, y, height_variation):
        self.x = x
        self.y = y
        self.height_variation = height_variation
        self.size = 100
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Vary terrain color based on height
        color_offset = self.height_variation
        r = max(0, min(255, 34 + color_offset))
        g = max(0, min(255, 139 + color_offset//2))
        b = max(0, min(255, 34 + color_offset//3))
        
        # Draw terrain patch
        pygame.draw.rect(screen, (r, g, b), 
                        (screen_x, screen_y, self.size, self.size))

if __name__ == "__main__":
    game = AssetWorld()
    game.run()
