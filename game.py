import pygame
import json
import math
import random
import os
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
import glob

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
GRID_SIZE = 12
CELL_SIZE = 48
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - GRID_SIZE * CELL_SIZE) // 2

# Colors (Synthwave palette)
BLACK = (0, 0, 0)
DARK_PURPLE = (20, 10, 30)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
NEON_PINK = (255, 20, 147)
NEON_BLUE = (0, 191, 255)
NEON_GREEN = (57, 255, 20)
GRID_COLOR = (100, 50, 100)
PLAYER_COLOR = (255, 255, 255)

class Direction(Enum):
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

class OpticType(Enum):
    EMPTY = "empty"
    MIRROR = "mirror"
    PRISM = "prism"
    SPLITTER = "splitter"
    CRYSTAL_WELL = "crystal_well"
    BEAM_SOURCE = "beam_source"
    FILTER = "filter"

class BeamColor(Enum):
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)

@dataclass
class Position:
    x: int
    y: int
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

@dataclass
class Optic:
    type: OpticType
    rotation: int = 0  # 0, 90, 180, 270 degrees
    color_filter: Optional[BeamColor] = None

@dataclass
class BeamSource:
    position: Position
    direction: Direction
    color: BeamColor = BeamColor.WHITE

@dataclass
class BeamSegment:
    start: Position
    end: Position
    color: BeamColor

@dataclass
class GameState:
    player_pos: Position
    grid: List[List[Optic]]
    beam_sources: List[BeamSource]
    crystal_wells: List[Position]
    step_count: int = 0
    score: int = 0
    goals_reached: int = 0
    beam_segments: List[BeamSegment] = field(default_factory=list)

class LightBeamGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Neon Light Router - Synthwave Puzzle")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load existing game state or create new one
        self.game_state = self.load_or_create_game_state()
        self.recalculate_beams()
        
        # Visual effects
        self.particle_systems = []
        self.glow_surfaces = {}
        self.create_glow_surfaces()
        
    def create_glow_surfaces(self):
        """Create pre-rendered glow effects for performance"""
        for color_name, color in [(name, color.value) for name, color in BeamColor.__members__.items()]:
            # Create glow surface
            glow_size = 32
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Create gradient glow effect
            center = glow_size // 2
            for radius in range(center, 0, -1):
                alpha = int(255 * (radius / center) * 0.3)
                glow_color = (*color[:3], alpha)
                pygame.draw.circle(glow_surf, glow_color, (center, center), radius)
            
            self.glow_surfaces[color_name.lower()] = glow_surf

    def load_or_create_game_state(self) -> GameState:
        """Load game state from JSON or create random state"""
        json_files = glob.glob("game_state_step_*.json")
        
        if json_files:
            # Load latest step file
            latest_file = max(json_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
            try:
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                return self.deserialize_game_state(data)
            except Exception as e:
                print(f"Error loading {latest_file}: {e}")
        
        # Create random initial state
        return self.create_random_game_state()
    
    def create_random_game_state(self) -> GameState:
        """Create a randomized initial game state"""
        # Initialize empty grid
        grid = [[Optic(OpticType.EMPTY) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Add random mirrors and prisms
        num_optics = random.randint(8, 15)
        for _ in range(num_optics):
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if grid[y][x].type == OpticType.EMPTY:
                optic_type = random.choice([OpticType.MIRROR, OpticType.PRISM, OpticType.SPLITTER])
                rotation = random.randint(0, 3) * 90
                grid[y][x] = Optic(optic_type, rotation)
        
        # Add beam sources
        beam_sources = []
        num_sources = random.randint(1, 3)
        for _ in range(num_sources):
            x = random.choice([0, GRID_SIZE-1])
            y = random.randint(0, GRID_SIZE-1)
            direction = Direction.EAST if x == 0 else Direction.WEST
            color = random.choice(list(BeamColor))
            beam_sources.append(BeamSource(Position(x, y), direction, color))
            grid[y][x] = Optic(OpticType.BEAM_SOURCE)
        
        # Add crystal wells
        crystal_wells = []
        num_wells = random.randint(2, 4)
        for _ in range(num_wells):
            while True:
                x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
                if grid[y][x].type == OpticType.EMPTY:
                    grid[y][x] = Optic(OpticType.CRYSTAL_WELL)
                    crystal_wells.append(Position(x, y))
                    break
        
        # Player starts at random empty position
        while True:
            px, py = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if grid[py][px].type == OpticType.EMPTY:
                break
        
        return GameState(
            player_pos=Position(px, py),
            grid=grid,
            beam_sources=beam_sources,
            crystal_wells=crystal_wells
        )
    
    def serialize_game_state(self) -> Dict[str, Any]:
        """Convert game state to JSON-serializable format"""
        def serialize_position(pos):
            return {"x": pos.x, "y": pos.y}
        
        def serialize_optic(optic):
            return {
                "type": optic.type.value,
                "rotation": optic.rotation,
                "color_filter": optic.color_filter.name if optic.color_filter else None
            }
        
        def serialize_beam_source(source):
            return {
                "position": serialize_position(source.position),
                "direction": source.direction.name,
                "color": source.color.name
            }
        
        def serialize_beam_segment(segment):
            return {
                "start": serialize_position(segment.start),
                "end": serialize_position(segment.end),
                "color": segment.color.name
            }
        
        return {
            "player_pos": serialize_position(self.game_state.player_pos),
            "grid": [[serialize_optic(cell) for cell in row] for row in self.game_state.grid],
            "beam_sources": [serialize_beam_source(source) for source in self.game_state.beam_sources],
            "crystal_wells": [serialize_position(well) for well in self.game_state.crystal_wells],
            "step_count": self.game_state.step_count,
            "score": self.game_state.score,
            "goals_reached": self.game_state.goals_reached,
            "beam_segments": [serialize_beam_segment(segment) for segment in self.game_state.beam_segments]
        }
    
    def deserialize_game_state(self, data: Dict[str, Any]) -> GameState:
        """Convert JSON data back to game state"""
        def deserialize_position(pos_data):
            return Position(pos_data["x"], pos_data["y"])
        
        def deserialize_optic(optic_data):
            return Optic(
                OpticType(optic_data["type"]),
                optic_data["rotation"],
                BeamColor[optic_data["color_filter"]] if optic_data["color_filter"] else None
            )
        
        def deserialize_beam_source(source_data):
            return BeamSource(
                deserialize_position(source_data["position"]),
                Direction[source_data["direction"]],
                BeamColor[source_data["color"]]
            )
        
        def deserialize_beam_segment(segment_data):
            return BeamSegment(
                deserialize_position(segment_data["start"]),
                deserialize_position(segment_data["end"]),
                BeamColor[segment_data["color"]]
            )
        
        return GameState(
            player_pos=deserialize_position(data["player_pos"]),
            grid=[[deserialize_optic(cell) for cell in row] for row in data["grid"]],
            beam_sources=[deserialize_beam_source(source) for source in data["beam_sources"]],
            crystal_wells=[deserialize_position(well) for well in data["crystal_wells"]],
            step_count=data["step_count"],
            score=data["score"],
            goals_reached=data["goals_reached"],
            beam_segments=[deserialize_beam_segment(segment) for segment in data.get("beam_segments", [])]
        )
    
    def save_game_state(self):
        """Save current game state to JSON file"""
        filename = f"game_state_step_{self.game_state.step_count}.json"
        with open(filename, 'w') as f:
            json.dump(self.serialize_game_state(), f, indent=2)
        print(f"Game state saved to {filename}")
    
    def recalculate_beams(self):
        """Recalculate all beam paths"""
        self.game_state.beam_segments = []
        goals_hit = set()
        
        for source in self.game_state.beam_sources:
            self.trace_beam(source.position, source.direction, source.color, goals_hit)
        
        # Update score based on goals reached
        self.game_state.goals_reached = len(goals_hit)
        base_score = self.game_state.goals_reached * 100
        step_penalty = self.game_state.step_count * 2
        self.game_state.score = max(0, base_score - step_penalty)
    
    def trace_beam(self, start_pos: Position, direction: Direction, color: BeamColor, goals_hit: set, visited=None):
        """Trace a beam through the grid"""
        if visited is None:
            visited = set()
        
        current_pos = Position(start_pos.x, start_pos.y)
        beam_start = Position(current_pos.x, current_pos.y)
        
        while True:
            # Move to next position
            dx, dy = direction.value
            next_pos = Position(current_pos.x + dx, current_pos.y + dy)
            
            # Check bounds
            if (next_pos.x < 0 or next_pos.x >= GRID_SIZE or 
                next_pos.y < 0 or next_pos.y >= GRID_SIZE):
                # Add final beam segment to edge
                self.game_state.beam_segments.append(
                    BeamSegment(beam_start, current_pos, color)
                )
                break
            
            current_pos = next_pos
            cell = self.game_state.grid[current_pos.y][current_pos.x]
            
            # Handle different optic types
            if cell.type == OpticType.CRYSTAL_WELL:
                # Add beam segment and mark goal as hit
                self.game_state.beam_segments.append(
                    BeamSegment(beam_start, current_pos, color)
                )
                goals_hit.add((current_pos.x, current_pos.y))
                break
            
            elif cell.type == OpticType.MIRROR:
                # Add beam segment to mirror
                self.game_state.beam_segments.append(
                    BeamSegment(beam_start, current_pos, color)
                )
                
                # Calculate reflection
                new_direction = self.reflect_beam(direction, cell.rotation)
                if new_direction:
                    beam_start = Position(current_pos.x, current_pos.y)
                    direction = new_direction
                else:
                    break
            
            elif cell.type == OpticType.PRISM:
                # Add beam segment to prism
                self.game_state.beam_segments.append(
                    BeamSegment(beam_start, current_pos, color)
                )
                
                # Prism refracts and potentially splits beam
                new_directions = self.refract_beam(direction, cell.rotation, color)
                for new_dir, new_color in new_directions:
                    pos_key = (current_pos.x, current_pos.y, new_dir)
                    if pos_key not in visited:
                        visited.add(pos_key)
                        self.trace_beam(current_pos, new_dir, new_color, goals_hit, visited)
                break
            
            elif cell.type == OpticType.SPLITTER:
                # Add beam segment to splitter
                self.game_state.beam_segments.append(
                    BeamSegment(beam_start, current_pos, color)
                )
                
                # Splitter creates multiple beams
                new_directions = self.split_beam(direction, cell.rotation)
                for new_dir in new_directions:
                    pos_key = (current_pos.x, current_pos.y, new_dir)
                    if pos_key not in visited:
                        visited.add(pos_key)
                        self.trace_beam(current_pos, new_dir, color, goals_hit, visited)
                break
    
    def reflect_beam(self, direction: Direction, mirror_rotation: int) -> Optional[Direction]:
        """Calculate beam reflection off mirror"""
        # Simplified mirror reflection logic
        angle_map = {
            (Direction.NORTH, 0): Direction.EAST,
            (Direction.EAST, 0): Direction.NORTH,
            (Direction.SOUTH, 0): Direction.WEST,
            (Direction.WEST, 0): Direction.SOUTH,
            (Direction.NORTH, 90): Direction.WEST,
            (Direction.WEST, 90): Direction.NORTH,
            (Direction.SOUTH, 90): Direction.EAST,
            (Direction.EAST, 90): Direction.SOUTH,
        }
        
        return angle_map.get((direction, mirror_rotation % 180))
    
    def refract_beam(self, direction: Direction, prism_rotation: int, color: BeamColor) -> List[Tuple[Direction, BeamColor]]:
        """Calculate beam refraction through prism"""
        # Simplified prism logic - splits white light into colors
        if color == BeamColor.WHITE:
            return [
                (self.rotate_direction(direction, 30), BeamColor.RED),
                (direction, BeamColor.GREEN),
                (self.rotate_direction(direction, -30), BeamColor.BLUE)
            ]
        else:
            # Colored light continues straight but may change direction slightly
            return [(self.rotate_direction(direction, 15), color)]
    
    def split_beam(self, direction: Direction, splitter_rotation: int) -> List[Direction]:
        """Calculate beam splitting"""
        # Splitter sends beam in two perpendicular directions
        if direction in [Direction.NORTH, Direction.SOUTH]:
            return [Direction.EAST, Direction.WEST]
        else:
            return [Direction.NORTH, Direction.SOUTH]
    
    def rotate_direction(self, direction: Direction, angle_degrees: int) -> Direction:
        """Rotate direction by given angle (simplified)"""
        directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        current_index = directions.index(direction)
        
        if angle_degrees == 30 or angle_degrees == 90:
            return directions[(current_index + 1) % 4]
        elif angle_degrees == -30 or angle_degrees == -90:
            return directions[(current_index - 1) % 4]
        else:
            return direction
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            old_pos = Position(self.game_state.player_pos.x, self.game_state.player_pos.y)
            moved = False
            
            # WASD movement
            if event.key == pygame.K_w and self.game_state.player_pos.y > 0:
                self.game_state.player_pos.y -= 1
                moved = True
            elif event.key == pygame.K_s and self.game_state.player_pos.y < GRID_SIZE - 1:
                self.game_state.player_pos.y += 1
                moved = True
            elif event.key == pygame.K_a and self.game_state.player_pos.x > 0:
                self.game_state.player_pos.x -= 1
                moved = True
            elif event.key == pygame.K_d and self.game_state.player_pos.x < GRID_SIZE - 1:
                self.game_state.player_pos.x += 1
                moved = True
            
            # Space to rotate/cycle optic
            elif event.key == pygame.K_SPACE:
                x, y = self.game_state.player_pos.x, self.game_state.player_pos.y
                current_optic = self.game_state.grid[y][x]
                
                if current_optic.type == OpticType.EMPTY:
                    self.game_state.grid[y][x] = Optic(OpticType.MIRROR, 0)
                elif current_optic.type == OpticType.MIRROR:
                    if current_optic.rotation < 270:
                        current_optic.rotation += 90
                    else:
                        self.game_state.grid[y][x] = Optic(OpticType.PRISM, 0)
                elif current_optic.type == OpticType.PRISM:
                    if current_optic.rotation < 270:
                        current_optic.rotation += 90
                    else:
                        self.game_state.grid[y][x] = Optic(OpticType.SPLITTER, 0)
                elif current_optic.type == OpticType.SPLITTER:
                    if current_optic.rotation < 270:
                        current_optic.rotation += 90
                    else:
                        self.game_state.grid[y][x] = Optic(OpticType.EMPTY, 0)
                
                moved = True
            
            # Restart with R
            elif event.key == pygame.K_r:
                self.game_state = self.create_random_game_state()
                moved = True
            
            # If any action was taken, update game state
            if moved:
                self.game_state.step_count += 1
                self.recalculate_beams()
                self.save_game_state()
    
    def draw_grid(self):
        """Draw the game grid"""
        for x in range(GRID_SIZE + 1):
            start_x = GRID_OFFSET_X + x * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, 
                           (start_x, GRID_OFFSET_Y), 
                           (start_x, GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE))
        
        for y in range(GRID_SIZE + 1):
            start_y = GRID_OFFSET_Y + y * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, 
                           (GRID_OFFSET_X, start_y), 
                           (GRID_OFFSET_X + GRID_SIZE * CELL_SIZE, start_y))
    
    def draw_optics(self):
        """Draw all optics on the grid"""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                optic = self.game_state.grid[y][x]
                if optic.type != OpticType.EMPTY:
                    screen_x = GRID_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2
                    screen_y = GRID_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2
                    
                    self.draw_optic(screen_x, screen_y, optic)
    
    def draw_optic(self, x: int, y: int, optic: Optic):
        """Draw a single optic"""
        if optic.type == OpticType.MIRROR:
            color = CYAN
            # Draw mirror as a line
            angle = math.radians(optic.rotation)
            length = CELL_SIZE // 3
            dx = length * math.cos(angle)
            dy = length * math.sin(angle)
            pygame.draw.line(self.screen, color, 
                           (x - dx, y - dy), (x + dx, y + dy), 3)
            
        elif optic.type == OpticType.PRISM:
            color = MAGENTA
            # Draw prism as triangle
            size = CELL_SIZE // 4
            points = [
                (x, y - size),
                (x - size, y + size//2),
                (x + size, y + size//2)
            ]
            pygame.draw.polygon(self.screen, color, points)
            
        elif optic.type == OpticType.SPLITTER:
            color = NEON_GREEN
            # Draw splitter as cross
            size = CELL_SIZE // 4
            pygame.draw.line(self.screen, color, 
                           (x - size, y), (x + size, y), 3)
            pygame.draw.line(self.screen, color, 
                           (x, y - size), (x, y + size), 3)
            
        elif optic.type == OpticType.CRYSTAL_WELL:
            color = NEON_PINK
            # Draw crystal well as diamond
            size = CELL_SIZE // 3
            points = [
                (x, y - size),
                (x + size, y),
                (x, y + size),
                (x - size, y)
            ]
            pygame.draw.polygon(self.screen, color, points)
            
        elif optic.type == OpticType.BEAM_SOURCE:
            color = NEON_BLUE
            # Draw beam source as circle
            pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 4)
    
    def draw_beams(self):
        """Draw all beam segments with glow effects"""
        for segment in self.game_state.beam_segments:
            start_x = GRID_OFFSET_X + segment.start.x * CELL_SIZE + CELL_SIZE // 2
            start_y = GRID_OFFSET_Y + segment.start.y * CELL_SIZE + CELL_SIZE // 2
            end_x = GRID_OFFSET_X + segment.end.x * CELL_SIZE + CELL_SIZE // 2
            end_y = GRID_OFFSET_Y + segment.end.y * CELL_SIZE + CELL_SIZE // 2
            
            # Draw beam line
            beam_color = segment.color.value
            pygame.draw.line(self.screen, beam_color, (start_x, start_y), (end_x, end_y), 3)
            
            # Add glow effect
            if segment.color.name.lower() in self.glow_surfaces:
                glow_surf = self.glow_surfaces[segment.color.name.lower()]
                # Draw glow at multiple points along the beam
                steps = max(1, int(math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2) / 20))
                for i in range(steps + 1):
                    t = i / max(1, steps)
                    glow_x = int(start_x + t * (end_x - start_x)) - 16
                    glow_y = int(start_y + t * (end_y - start_y)) - 16
                    self.screen.blit(glow_surf, (glow_x, glow_y), special_flags=pygame.BLEND_ADD)
    
    def draw_player(self):
        """Draw the player"""
        screen_x = GRID_OFFSET_X + self.game_state.player_pos.x * CELL_SIZE + CELL_SIZE // 2
        screen_y = GRID_OFFSET_Y + self.game_state.player_pos.y * CELL_SIZE + CELL_SIZE // 2
        
        # Draw player as white circle with glow
        pygame.draw.circle(self.screen, PLAYER_COLOR, (screen_x, screen_y), 8)
        
        # Add subtle glow
        glow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 255, 50), (16, 16), 16)
        self.screen.blit(glow_surf, (screen_x - 16, screen_y - 16), special_flags=pygame.BLEND_ADD)
    
    def draw_ui(self):
        """Draw UI elements"""
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.game_state.score}", True, CYAN)
        self.screen.blit(score_text, (20, 20))
        
        # Steps
        steps_text = font.render(f"Steps: {self.game_state.step_count}", True, NEON_PINK)
        self.screen.blit(steps_text, (20, 60))
        
        # Goals
        goals_text = font.render(f"Wells Hit: {self.game_state.goals_reached}/{len(self.game_state.crystal_wells)}", True, NEON_GREEN)
        self.screen.blit(goals_text, (20, 100))
        
        # Controls
        controls = [
            "WASD: Move",
            "SPACE: Rotate/Place Optics",
            "R: Restart"
        ]
        
        small_font = pygame.font.Font(None, 24)
        for i, control in enumerate(controls):
            text = small_font.render(control, True, GRID_COLOR)
            self.screen.blit(text, (WINDOW_WIDTH - 200, 20 + i * 25))
    
    def draw(self):
        """Main draw function"""
        self.screen.fill(DARK_PURPLE)
        
        self.draw_grid()
        self.draw_optics()
        self.draw_beams()
        self.draw_player()
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_input(event)
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = LightBeamGame()
    game.run()
