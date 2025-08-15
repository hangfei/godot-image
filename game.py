import pygame
import json
import random
import math
import os
from typing import List, Tuple, Dict, Optional
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_WIDTH = 8
GRID_HEIGHT = 8
TILE_SIZE = 60
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 100
FPS = 60

# Colors
COLORS = {
    'background': (20, 20, 40),
    'grid_bg': (40, 40, 60),
    'grid_border': (80, 80, 100),
    'cursor': (255, 255, 255),
    'selected': (255, 255, 0),
    'text': (255, 255, 255),
    'score_bg': (60, 60, 80),
    'gem_red': (220, 50, 50),
    'gem_blue': (50, 50, 220),
    'gem_green': (50, 220, 50),
    'gem_yellow': (220, 220, 50),
    'gem_purple': (220, 50, 220),
    'gem_orange': (255, 165, 0),
    'gem_cyan': (50, 220, 220),
    'particle': (255, 255, 255)
}

class GemType(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    PURPLE = 5
    ORANGE = 6
    CYAN = 7

class GameState(Enum):
    PLAYING = 1
    SELECTING = 2
    LINKING = 3
    CLEARING = 4

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.color = color
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.life -= 1
        
    def draw(self, screen: pygame.Surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = max(1, int(4 * (self.life / self.max_life)))
            color = (*self.color, alpha)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Gem:
    def __init__(self, gem_type: GemType, x: int, y: int):
        self.type = gem_type
        self.x = x
        self.y = y
        self.selected = False
        self.linked = False
        self.animation_offset = 0.0
        self.pulse_timer = 0.0
        
    def get_color(self) -> Tuple[int, int, int]:
        color_map = {
            GemType.RED: COLORS['gem_red'],
            GemType.BLUE: COLORS['gem_blue'],
            GemType.GREEN: COLORS['gem_green'],
            GemType.YELLOW: COLORS['gem_yellow'],
            GemType.PURPLE: COLORS['gem_purple'],
            GemType.ORANGE: COLORS['gem_orange'],
            GemType.CYAN: COLORS['gem_cyan']
        }
        return color_map[self.type]
        
    def update(self):
        self.pulse_timer += 0.1
        if self.linked:
            self.animation_offset = math.sin(self.pulse_timer * 3) * 3
            
    def draw(self, screen: pygame.Surface, screen_x: int, screen_y: int):
        color = self.get_color()
        
        # Add glow effect for linked gems
        if self.linked:
            glow_color = tuple(min(255, c + 50) for c in color)
            pygame.draw.circle(screen, glow_color, 
                             (screen_x, screen_y + int(self.animation_offset)), 
                             TILE_SIZE // 2 + 5)
        
        # Draw main gem
        pygame.draw.circle(screen, color, 
                         (screen_x, screen_y + int(self.animation_offset)), 
                         TILE_SIZE // 2 - 5)
        
        # Add highlight
        highlight_color = tuple(min(255, c + 80) for c in color)
        pygame.draw.circle(screen, highlight_color, 
                         (screen_x - 8, screen_y - 8 + int(self.animation_offset)), 
                         TILE_SIZE // 4)
        
        # Draw selection border
        if self.selected:
            pygame.draw.circle(screen, COLORS['selected'], 
                             (screen_x, screen_y + int(self.animation_offset)), 
                             TILE_SIZE // 2 - 2, 3)

class LinkAndMaxGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Link & Max - Gem Puzzle")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.running = True
        self.state = GameState.PLAYING
        self.grid: List[List[Optional[Gem]]] = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.selected_gems: List[Tuple[int, int]] = []
        self.linked_gems: List[Tuple[int, int]] = []
        self.preview_gems: List[Tuple[int, int]] = []  # Gems that would be cleared
        self.selection_mode = False  # Whether we're in selection preview mode
        self.invalid_selection_timer = 0  # Timer for showing invalid selection feedback
        self.score = 0
        self.moves = 0
        self.multiplier = 1
        self.particles: List[Particle] = []
        
        # Input handling
        self.keys_pressed = set()
        
        # Initialize game
        self.load_game_state()
        
    def create_empty_grid(self):
        """Create an empty grid"""
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
    def fill_grid_randomly(self):
        """Fill the grid with random gems"""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                gem_type = random.choice(list(GemType))
                self.grid[y][x] = Gem(gem_type, x, y)
                
    def load_game_state(self):
        """Load game state from ANY JSON file in directory or create new game"""
        # Look for ANY .json file in the current directory
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        
        if json_files:
            print(f"Found {len(json_files)} JSON file(s): {', '.join(json_files)}")
            
            # Try files in order of preference: save files first, then most recent
            save_files = [f for f in json_files if f.startswith('save')]
            if save_files:
                # Prefer save files, pick most recent
                latest_file = max(save_files, key=lambda f: os.path.getmtime(f))
            else:
                # No save files, pick most recent JSON file
                latest_file = max(json_files, key=lambda f: os.path.getmtime(f))
            
            print(f"Attempting to load: {latest_file}")
            
            try:
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    
                    # Validate it's a game state file
                    required_keys = ['grid']
                    if not all(key in data for key in required_keys):
                        print(f"⚠️  {latest_file} doesn't appear to be a game state file (missing required keys)")
                        print(f"   Required: {required_keys}, Found: {list(data.keys())}")
                        raise ValueError("Invalid game state format")
                    
                    # Load game state data
                    self.score = data.get('score', 0)
                    self.moves = data.get('moves', 0)
                    self.cursor_x = data.get('cursor_x', 0)
                    self.cursor_y = data.get('cursor_y', 0)
                    
                    # Validate cursor position
                    self.cursor_x = max(0, min(self.cursor_x, GRID_WIDTH - 1))
                    self.cursor_y = max(0, min(self.cursor_y, GRID_HEIGHT - 1))
                    
                    # Reconstruct grid
                    self.create_empty_grid()
                    grid_data = data.get('grid', [])
                    
                    if not grid_data:
                        print("⚠️  Grid data is empty, creating random grid")
                        self.fill_grid_randomly()
                    else:
                        for y in range(min(len(grid_data), GRID_HEIGHT)):
                            row = grid_data[y]
                            if isinstance(row, list):
                                for x in range(min(len(row), GRID_WIDTH)):
                                    if row[x] is not None:
                                        try:
                                            gem_type = GemType(row[x])
                                            self.grid[y][x] = Gem(gem_type, x, y)
                                        except ValueError:
                                            print(f"⚠️  Invalid gem type {row[x]} at ({x}, {y}), skipping")
                        
                        # Fill any empty spots that might exist
                        for y in range(GRID_HEIGHT):
                            for x in range(GRID_WIDTH):
                                if self.grid[y][x] is None:
                                    gem_type = random.choice(list(GemType))
                                    self.grid[y][x] = Gem(gem_type, x, y)
                    
                print(f"✅ Successfully loaded game from {latest_file}")
                print(f"   Score: {self.score}, Moves: {self.moves}, Cursor: ({self.cursor_x}, {self.cursor_y})")
                return
                
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                print(f"❌ Error loading {latest_file}: {e}")
                print(f"   Trying other JSON files...")
                
                # Try other JSON files if the first one failed
                for file in json_files:
                    if file != latest_file:
                        try:
                            print(f"   Trying {file}...")
                            with open(file, 'r') as f:
                                data = json.load(f)
                                if 'grid' in data:
                                    print(f"   ✅ {file} looks valid, using it instead")
                                    # Recursively call but with this file as the "latest"
                                    os.utime(file)  # Touch file to make it most recent
                                    return self.load_game_state()
                        except Exception:
                            continue
                            
                print("❌ No valid game state files found, creating new game")
        
        # Create new game if no save file or error loading
        self.create_empty_grid()
        self.fill_grid_randomly()
        self.score = 0
        self.moves = 0
        print("Started new game")
        
    def save_game_state(self):
        """Save current game state to JSON"""
        # Convert grid to serializable format
        grid_data = []
        for y in range(GRID_HEIGHT):
            row = []
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    row.append(self.grid[y][x].type.value)
                else:
                    row.append(None)
            grid_data.append(row)
            
        data = {
            'score': self.score,
            'moves': self.moves,
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'grid': grid_data,
            'timestamp': pygame.time.get_ticks()
        }
        
        filename = f"save_game_{self.score}_{self.moves}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Game saved to {filename}")
        
    def auto_save_game_state(self):
        """Auto-save current game state to JSON (silent)"""
        # Convert grid to serializable format
        grid_data = []
        for y in range(GRID_HEIGHT):
            row = []
            for x in range(GRID_WIDTH):
                gem = self.grid[y][x]
                if gem is not None:
                    row.append(gem.type.value)
                else:
                    row.append(None)
            grid_data.append(row)
            
        data = {
            'score': self.score,
            'moves': self.moves,
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'grid': grid_data,
            'timestamp': pygame.time.get_ticks(),
            'auto_saved': True
        }
        
        # Use a consistent auto-save filename that gets overwritten
        filename = "auto_save_current.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
    def get_adjacent_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid adjacent positions"""
        positions = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                positions.append((nx, ny))
        return positions
        
    def find_linked_gems(self, start_x: int, start_y: int) -> List[Tuple[int, int]]:
        """Find all gems of the same type linked to the starting position"""
        if self.grid[start_y][start_x] is None:
            return []
            
        start_gem = self.grid[start_y][start_x]
        if start_gem is None:
            return []
            
        visited = set()
        to_visit = [(start_x, start_y)]
        linked = []
        
        while to_visit:
            x, y = to_visit.pop(0)
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            current_gem = self.grid[y][x]
            
            if current_gem is not None and start_gem is not None and current_gem.type == start_gem.type:
                linked.append((x, y))
                
                # Add adjacent positions to check
                for adj_x, adj_y in self.get_adjacent_positions(x, y):
                    if (adj_x, adj_y) not in visited:
                        to_visit.append((adj_x, adj_y))
                        
        return linked if len(linked) >= 3 else []  # Only return if 3+ gems linked
        
    def clear_linked_gems(self):
        """Remove linked gems and add particles"""
        if not self.linked_gems:
            return
            
        # Calculate score
        base_score = len(self.linked_gems) * 10
        bonus_score = max(0, (len(self.linked_gems) - 3) * 5)  # Bonus for longer chains
        total_score = (base_score + bonus_score) * self.multiplier
        self.score += total_score
        
        # Create particles
        for x, y in self.linked_gems:
            screen_x = GRID_OFFSET_X + x * TILE_SIZE + TILE_SIZE // 2
            screen_y = GRID_OFFSET_Y + y * TILE_SIZE + TILE_SIZE // 2
            gem = self.grid[y][x]
            if gem is not None:
                gem_color = gem.get_color()
                
                for _ in range(8):
                    self.particles.append(Particle(screen_x, screen_y, gem_color))
            
            # Remove gem
            self.grid[y][x] = None
            
        # Apply gravity
        self.apply_gravity()
        
        # Fill empty spaces
        self.fill_empty_spaces()
        
        # Increase multiplier
        self.multiplier = min(5, self.multiplier + 1)
        
        self.linked_gems = []
        
        # Auto-save after clearing gems (major game state change)
        self.auto_save_game_state()
        
    def apply_gravity(self):
        """Make gems fall down"""
        for x in range(GRID_WIDTH):
            # Collect all non-None gems in this column
            gems = []
            for y in range(GRID_HEIGHT - 1, -1, -1):
                if self.grid[y][x] is not None:
                    gems.append(self.grid[y][x])
                    self.grid[y][x] = None
                    
            # Place them at the bottom
            for i, gem in enumerate(gems):
                new_y = GRID_HEIGHT - 1 - i
                self.grid[new_y][x] = gem
                gem.y = new_y
                
    def fill_empty_spaces(self):
        """Fill empty spaces with new random gems"""
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[y][x] is None:
                    gem_type = random.choice(list(GemType))
                    self.grid[y][x] = Gem(gem_type, x, y)
                    
    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            action_taken = False  # Track if we need to auto-save
            
            if event.key == pygame.K_w and self.cursor_y > 0:
                self.cursor_y -= 1
                self.moves += 1
                action_taken = True
            elif event.key == pygame.K_s and self.cursor_y < GRID_HEIGHT - 1:
                self.cursor_y += 1
                self.moves += 1
                action_taken = True
            elif event.key == pygame.K_a and self.cursor_x > 0:
                self.cursor_x -= 1
                self.moves += 1
                action_taken = True
            elif event.key == pygame.K_d and self.cursor_x < GRID_WIDTH - 1:
                self.cursor_x += 1
                self.moves += 1
                action_taken = True
            elif event.key == pygame.K_SPACE:
                self.handle_selection()
                self.moves += 1
                action_taken = True
            elif event.key == pygame.K_r:
                # Reset game
                self.create_empty_grid()
                self.fill_grid_randomly()
                self.score = 0
                self.moves = 0
                self.multiplier = 1
                self.cursor_x = 0
                self.cursor_y = 0
                self.selected_gems = []
                self.linked_gems = []
                self.preview_gems = []
                self.selection_mode = False
                self.clear_all_selections()
                action_taken = True
            elif event.key == pygame.K_F1:
                # Manual save game
                self.save_game_state()
                
            # Clear selection mode when moving cursor
            if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                if self.selection_mode:
                    self.clear_all_selections()
                    self.selection_mode = False
                    self.preview_gems = []
                self.multiplier = 1
            elif event.key == pygame.K_SPACE:
                self.multiplier = 1
                
            # Auto-save after any action that changes game state
            if action_taken:
                self.auto_save_game_state()
                
    def handle_selection(self):
        """Handle gem selection and linking"""
        cursor_pos = (self.cursor_x, self.cursor_y)
        
        if self.grid[self.cursor_y][self.cursor_x] is None:
            return
            
        # If we're already in selection mode, check if we can execute the clear
        if self.selection_mode:
            current_gem = self.grid[self.cursor_y][self.cursor_x]
            # Execute if cursor is on any gem in the preview group OR same type as preview gems
            preview_gem = None
            if len(self.preview_gems) > 0:
                px, py = self.preview_gems[0]
                preview_gem = self.grid[py][px]
            
            if (cursor_pos in self.preview_gems or 
                (current_gem is not None and preview_gem is not None and
                 current_gem.type == preview_gem.type)):
                # Execute the clearing
                self.linked_gems = self.preview_gems[:]
                for x, y in self.linked_gems:
                    gem = self.grid[y][x]
                    if gem is not None:
                        gem.linked = True
                self.clear_linked_gems()
                self.selection_mode = False
                self.preview_gems = []
                self.clear_all_selections()
                return
            
        # Find all linked gems of the same type
        linked = self.find_linked_gems(self.cursor_x, self.cursor_y)
        
        if len(linked) >= 3:
            # Clear previous selections
            self.clear_all_selections()
                        
            # Enter selection mode - show preview
            self.selection_mode = True
            self.preview_gems = linked[:]
            
            # Mark gems for preview (selected state)
            for x, y in linked:
                gem = self.grid[y][x]
                if gem is not None:
                    gem.selected = True
        else:
            # No valid selection - provide feedback
            current_gem = self.grid[self.cursor_y][self.cursor_x]
            if current_gem is not None:
                # Show brief feedback for invalid selection
                current_gem.selected = True
                # Clear it after a moment (handled in update)
                self.invalid_selection_timer = 30  # frames to show feedback
            self.clear_all_selections()
            self.selection_mode = False
            self.preview_gems = []
            
    def clear_all_selections(self):
        """Clear all gem selections and previews"""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                gem = self.grid[y][x]
                if gem is not None:
                    gem.selected = False
                    gem.linked = False
            
    def update(self):
        """Update game state"""
        # Update gems
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                gem = self.grid[y][x]
                if gem is not None:
                    gem.update()
                    
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
            
        # Handle invalid selection feedback timer
        if self.invalid_selection_timer > 0:
            self.invalid_selection_timer -= 1
            if self.invalid_selection_timer == 0:
                self.clear_all_selections()
            
    def draw(self):
        """Draw the game"""
        self.screen.fill(COLORS['background'])
        
        # Draw title
        title_text = self.font.render("Link & Max - Gem Puzzle", True, COLORS['text'])
        self.screen.blit(title_text, (10, 10))
        
        # Draw score and info
        score_text = self.font.render(f"Score: {self.score}", True, COLORS['text'])
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, COLORS['text'])
        multiplier_text = self.small_font.render(f"Multiplier: x{self.multiplier}", True, COLORS['text'])
        
        self.screen.blit(score_text, (10, 50))
        self.screen.blit(moves_text, (200, 55))
        self.screen.blit(multiplier_text, (300, 55))
        
        # Draw controls
        controls = [
            "WASD: Move cursor",
            "SPACE: Select gems, SPACE again: Clear",
            "R: Reset game",
            "F1: Manual save (auto-saves every action)"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, COLORS['text'])
            self.screen.blit(control_text, (WINDOW_WIDTH - 200, 10 + i * 20))
            
        # Draw grid background
        grid_rect = pygame.Rect(GRID_OFFSET_X - 10, GRID_OFFSET_Y - 10, 
                               GRID_WIDTH * TILE_SIZE + 20, GRID_HEIGHT * TILE_SIZE + 20)
        pygame.draw.rect(self.screen, COLORS['grid_bg'], grid_rect)
        pygame.draw.rect(self.screen, COLORS['grid_border'], grid_rect, 2)
        
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            start_x = GRID_OFFSET_X + x * TILE_SIZE
            pygame.draw.line(self.screen, COLORS['grid_border'], 
                           (start_x, GRID_OFFSET_Y), 
                           (start_x, GRID_OFFSET_Y + GRID_HEIGHT * TILE_SIZE))
                           
        for y in range(GRID_HEIGHT + 1):
            start_y = GRID_OFFSET_Y + y * TILE_SIZE
            pygame.draw.line(self.screen, COLORS['grid_border'], 
                           (GRID_OFFSET_X, start_y), 
                           (GRID_OFFSET_X + GRID_WIDTH * TILE_SIZE, start_y))
        
        # Draw gems
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                gem = self.grid[y][x]
                if gem is not None:
                    screen_x = GRID_OFFSET_X + x * TILE_SIZE + TILE_SIZE // 2
                    screen_y = GRID_OFFSET_Y + y * TILE_SIZE + TILE_SIZE // 2
                    gem.draw(self.screen, screen_x, screen_y)
        
        # Draw cursor
        cursor_screen_x = GRID_OFFSET_X + self.cursor_x * TILE_SIZE
        cursor_screen_y = GRID_OFFSET_Y + self.cursor_y * TILE_SIZE
        cursor_rect = pygame.Rect(cursor_screen_x, cursor_screen_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, COLORS['cursor'], cursor_rect, 3)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
            
        # Draw linking hints and status
        if self.selection_mode:
            hint_text = self.small_font.render(f"Press SPACE on any highlighted gem to clear {len(self.preview_gems)} gems!", True, COLORS['selected'])
        elif self.invalid_selection_timer > 0:
            hint_text = self.small_font.render("Need 3+ adjacent gems of the same color!", True, (255, 100, 100))
        else:
            hint_text = self.small_font.render("Link 3+ adjacent gems of the same color!", True, COLORS['text'])
        self.screen.blit(hint_text, (10, WINDOW_HEIGHT - 40))
        
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game_state()
                    self.running = False
                else:
                    self.handle_input(event)
                    
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = LinkAndMaxGame()
    game.run()
