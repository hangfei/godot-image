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

# Grid settings for tile matching game
GRID_WIDTH = 8
GRID_HEIGHT = 6
TILE_SIZE = 80
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH * TILE_SIZE) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - GRID_HEIGHT * TILE_SIZE) // 2

# Colors inspired by our GLB assets
BACKGROUND_GREEN = (34, 139, 34)  # Forest green for terrain
TREE_BROWN = (101, 67, 33)       # Tree trunk color
TREE_GREEN = (0, 100, 0)         # Tree foliage
BUILDING_RED = (180, 100, 80)    # Building brick color
CUBE_BLUE = (0, 100, 255)        # Cube color
SPHERE_PURPLE = (128, 0, 128)    # Sphere object color
CYLINDER_WOOD = (139, 90, 43)    # Cylinder wood color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Asset types (representing our GLB assets)
ASSET_TYPES = {
    'CUBE': {'color': CUBE_BLUE, 'name': 'Cube'},
    'SPHERE': {'color': SPHERE_PURPLE, 'name': 'Sphere'},
    'CYLINDER': {'color': CYLINDER_WOOD, 'name': 'Cylinder'},
    'TREE': {'color': TREE_GREEN, 'name': 'Tree'},
    'BUILDING': {'color': BUILDING_RED, 'name': 'Building'},
    'TERRAIN': {'color': BACKGROUND_GREEN, 'name': 'Terrain'}
}

class TileMatchingGame:
    """GLB Asset Tile Matching Game - Click to match pairs!"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("GLB Asset Matching - Click Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.revealed = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.matched = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Game variables
        self.first_selection = None
        self.second_selection = None
        self.selection_time = 0
        self.score = 0
        self.moves = 0
        self.pairs_found = 0
        self.total_pairs = (GRID_WIDTH * GRID_HEIGHT) // 2
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Generate grid
        self.generate_grid()
    
    def generate_grid(self):
        """Generate a grid of asset tiles with pairs"""
        # Create pairs of each asset type
        assets = list(ASSET_TYPES.keys())
        tiles = []
        
        # Fill the grid with pairs
        pairs_needed = self.total_pairs
        for i in range(pairs_needed):
            asset_type = assets[i % len(assets)]
            tiles.extend([asset_type, asset_type])  # Add pair
        
        # Shuffle the tiles
        random.shuffle(tiles)
        
        # Place tiles in grid
        tile_index = 0
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if tile_index < len(tiles):
                    self.grid[row][col] = tiles[tile_index]
                    tile_index += 1
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game
                    self.__init__()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_click(event.pos)
    
    def handle_click(self, pos):
        """Handle mouse clicks on tiles"""
        x, y = pos
        
        # Convert screen coordinates to grid coordinates
        grid_x = (x - GRID_OFFSET_X) // TILE_SIZE
        grid_y = (y - GRID_OFFSET_Y) // TILE_SIZE
        
        # Check if click is within grid bounds
        if (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            # Check if tile is already matched or revealed
            if not self.matched[grid_y][grid_x] and not self.revealed[grid_y][grid_x]:
                self.reveal_tile(grid_x, grid_y)
    
    def reveal_tile(self, x, y):
        """Reveal a tile and handle game logic"""
        self.revealed[y][x] = True
        
        if self.first_selection is None:
            # First tile selected
            self.first_selection = (x, y)
        elif self.second_selection is None:
            # Second tile selected
            self.second_selection = (x, y)
            self.moves += 1
            self.selection_time = pygame.time.get_ticks()
            self.check_match()
    
    def check_match(self):
        """Check if the two selected tiles match"""
        if self.first_selection and self.second_selection:
            x1, y1 = self.first_selection
            x2, y2 = self.second_selection
            
            if self.grid[y1][x1] == self.grid[y2][x2]:
                # Match found!
                self.matched[y1][x1] = True
                self.matched[y2][x2] = True
                self.pairs_found += 1
                self.score += 100
                self.reset_selection()
            else:
                # No match - tiles will be hidden after delay
                pass
    
    def reset_selection(self):
        """Reset the current selection"""
        self.first_selection = None
        self.second_selection = None
        self.selection_time = 0
    
    def update(self):
        """Update game state"""
        # Hide non-matching tiles after delay
        if (self.first_selection and self.second_selection and 
            self.selection_time > 0 and 
            pygame.time.get_ticks() - self.selection_time > 1000):
            
            x1, y1 = self.first_selection
            x2, y2 = self.second_selection
            
            if not self.matched[y1][x1]:  # If not matched
                self.revealed[y1][x1] = False
                self.revealed[y2][x2] = False
            
            self.reset_selection()
    
    def draw_tile(self, x, y, asset_type):
        """Draw a single tile representing a GLB asset"""
        screen_x = GRID_OFFSET_X + x * TILE_SIZE
        screen_y = GRID_OFFSET_Y + y * TILE_SIZE
        
        # Draw tile background
        if self.matched[y][x]:
            bg_color = GREEN
        elif self.revealed[y][x]:
            bg_color = WHITE
        else:
            bg_color = LIGHT_GRAY
        
        pygame.draw.rect(self.screen, bg_color, 
                        (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.screen, DARK_GRAY, 
                        (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 2)
        
        # Draw asset representation if revealed or matched
        if self.revealed[y][x] or self.matched[y][x]:
            asset_info = ASSET_TYPES[asset_type]
            self.draw_asset(screen_x, screen_y, asset_type, asset_info['color'])
            
            # Draw asset name
            name_text = self.small_font.render(asset_info['name'], True, BLACK)
            text_rect = name_text.get_rect(center=(screen_x + TILE_SIZE//2, screen_y + TILE_SIZE - 10))
            self.screen.blit(name_text, text_rect)
    
    def draw_asset(self, x, y, asset_type, color):
        """Draw the visual representation of each GLB asset type"""
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2 - 10
        
        if asset_type == 'CUBE':
            # Draw cube (representing cube_basic.glb)
            size = 30
            pygame.draw.rect(self.screen, color, 
                           (center_x - size//2, center_y - size//2, size, size))
            pygame.draw.rect(self.screen, WHITE, 
                           (center_x - size//2, center_y - size//2, size, size), 2)
        
        elif asset_type == 'SPHERE':
            # Draw sphere (representing sphere_basic.glb)
            pygame.draw.circle(self.screen, color, (center_x, center_y), 20)
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 20, 2)
            # Add inner glow
            pygame.draw.circle(self.screen, (200, 150, 255), (center_x-5, center_y-5), 8)
        
        elif asset_type == 'CYLINDER':
            # Draw cylinder (representing cylinder_basic.glb)
            pygame.draw.ellipse(self.screen, color, 
                              (center_x - 20, center_y - 15, 40, 30))
            # Add wood grain lines
            for i in range(3):
                y_offset = center_y - 10 + i * 7
                pygame.draw.ellipse(self.screen, (120, 80, 40), 
                                  (center_x - 15, y_offset, 30, 3))
        
        elif asset_type == 'TREE':
            # Draw tree (representing tree_basic.glb)
            # Trunk
            pygame.draw.rect(self.screen, TREE_BROWN, 
                           (center_x - 4, center_y, 8, 20))
            # Foliage
            pygame.draw.circle(self.screen, color, (center_x, center_y - 5), 18)
        
        elif asset_type == 'BUILDING':
            # Draw building (representing building_basic.glb)
            pygame.draw.rect(self.screen, color, 
                           (center_x - 18, center_y - 15, 36, 30))
            # Add windows
            for i in range(2):
                for j in range(2):
                    window_x = center_x - 12 + i * 12
                    window_y = center_y - 10 + j * 10
                    pygame.draw.rect(self.screen, YELLOW, 
                                   (window_x, window_y, 8, 6))
        
        elif asset_type == 'TERRAIN':
            # Draw terrain (representing terrain_hills.glb)
            # Draw hills/terrain pattern
            points = [
                (center_x - 20, center_y + 10),
                (center_x - 10, center_y - 5),
                (center_x, center_y + 5),
                (center_x + 10, center_y - 8),
                (center_x + 20, center_y + 10)
            ]
            pygame.draw.polygon(self.screen, color, points)
    
    def draw(self):
        self.screen.fill(BACKGROUND_GREEN)
        
        # Draw title
        title_text = self.font.render("GLB Asset Matching Game", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 30))
        self.screen.blit(title_text, title_rect)
        
        # Draw grid
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if self.grid[row][col]:
                    self.draw_tile(col, row, self.grid[row][col])
        
        # Draw game info
        self.draw_ui()
        
        # Win condition
        if self.pairs_found == self.total_pairs:
            self.draw_win_screen()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw user interface"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Moves
        moves_text = self.font.render(f"Moves: {self.moves}", True, WHITE)
        self.screen.blit(moves_text, (10, 50))
        
        # Pairs found
        pairs_text = self.font.render(f"Pairs: {self.pairs_found}/{self.total_pairs}", True, WHITE)
        self.screen.blit(pairs_text, (10, 90))
        
        # Controls
        controls = [
            "🖱️ Click tiles to reveal",
            "🎯 Match pairs of GLB assets", 
            "R - Reset game",
            "ESC - Quit"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (WINDOW_WIDTH - 300, 10 + i * 25))
        
        # Asset legend
        legend_y = WINDOW_HEIGHT - 120
        legend_text = self.small_font.render("GLB Assets:", True, WHITE)
        self.screen.blit(legend_text, (10, legend_y))
        
        x_offset = 10
        for i, (asset_type, info) in enumerate(ASSET_TYPES.items()):
            y_pos = legend_y + 25 + (i % 3) * 25
            if i == 3:
                x_offset = 150
            
            # Draw mini asset
            mini_x = x_offset + (i % 3) * 120
            self.draw_asset(mini_x, y_pos - 10, asset_type, info['color'])
            
            # Draw name
            name_text = self.small_font.render(info['name'], True, WHITE)
            self.screen.blit(name_text, (mini_x + 50, y_pos))
    
    def draw_win_screen(self):
        """Draw win screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Win message
        win_text = self.font.render("🎉 ALL PAIRS MATCHED! 🎉", True, GOLD)
        win_rect = win_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(win_text, win_rect)
        
        # Final score
        final_score = self.font.render(f"Final Score: {self.score} (Moves: {self.moves})", True, WHITE)
        score_rect = final_score.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(final_score, score_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to play again", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TileMatchingGame()
    game.run()
