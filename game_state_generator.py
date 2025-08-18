def generate_game_state_json(seed=None, difficulty="medium"):
    """
    Generate a JSON string for a valid game state that can be loaded by the Light Beam Game.
    
    Args:
        seed: Integer seed for reproducible generation (uses simple LCG if provided)
        difficulty: "easy", "medium", or "hard" - affects number of optics and complexity
    
    Returns:
        JSON string representing a complete game state
    """
    
    # Simple Linear Congruential Generator for deterministic randomness
    class SimpleRandom:
        def __init__(self, seed=None):
            self.state = seed if seed is not None else 12345
        
        def randint(self, min_val, max_val):
            self.state = (self.state * 1103515245 + 12345) & 0x7fffffff
            return min_val + (self.state % (max_val - min_val + 1))
        
        def choice(self, items):
            return items[self.randint(0, len(items) - 1)]
        
        def shuffle(self, items):
            for i in range(len(items) - 1, 0, -1):
                j = self.randint(0, i)
                items[i], items[j] = items[j], items[i]
            return items
    
    rng = SimpleRandom(seed)
    
    # Game constants
    GRID_SIZE = 12
    
    # Difficulty settings
    difficulty_settings = {
        "easy": {"optics": (3, 6), "sources": (1, 2), "wells": (2, 3)},
        "medium": {"optics": (6, 10), "sources": (1, 3), "wells": (2, 4)},
        "hard": {"optics": (8, 15), "sources": (2, 4), "wells": (3, 5)}
    }
    
    settings = difficulty_settings.get(difficulty, difficulty_settings["medium"])
    
    # Initialize empty grid
    grid = []
    for y in range(GRID_SIZE):
        row = []
        for x in range(GRID_SIZE):
            row.append({
                "type": "empty",
                "rotation": 0,
                "color_filter": None
            })
        grid.append(row)
    
    # Available positions for placement
    available_positions = []
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            available_positions.append((x, y))
    
    # Add beam sources (place on edges)
    beam_sources = []
    num_sources = rng.randint(settings["sources"][0], settings["sources"][1])
    
    colors = ["WHITE", "RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA"]
    directions = ["NORTH", "EAST", "SOUTH", "WEST"]
    
    for _ in range(num_sources):
        # Choose edge position
        edge = rng.choice(["left", "right", "top", "bottom"])
        
        if edge == "left":
            x, y = 0, rng.randint(0, GRID_SIZE - 1)
            direction = "EAST"
        elif edge == "right":
            x, y = GRID_SIZE - 1, rng.randint(0, GRID_SIZE - 1)
            direction = "WEST"
        elif edge == "top":
            x, y = rng.randint(0, GRID_SIZE - 1), 0
            direction = "SOUTH"
        else:  # bottom
            x, y = rng.randint(0, GRID_SIZE - 1), GRID_SIZE - 1
            direction = "NORTH"
        
        # Make sure position is not already occupied
        if grid[y][x]["type"] == "empty":
            grid[y][x] = {
                "type": "beam_source",
                "rotation": 0,
                "color_filter": None
            }
            
            beam_sources.append({
                "position": {"x": x, "y": y},
                "direction": direction,
                "color": rng.choice(colors)
            })
            
            # Remove from available positions
            if (x, y) in available_positions:
                available_positions.remove((x, y))
    
    # Add crystal wells (avoid edges)
    crystal_wells = []
    num_wells = rng.randint(settings["wells"][0], settings["wells"][1])
    
    inner_positions = [(x, y) for x, y in available_positions 
                      if 1 <= x <= GRID_SIZE - 2 and 1 <= y <= GRID_SIZE - 2]
    
    for _ in range(min(num_wells, len(inner_positions))):
        if inner_positions:
            pos_idx = rng.randint(0, len(inner_positions) - 1)
            x, y = inner_positions.pop(pos_idx)
            
            grid[y][x] = {
                "type": "crystal_well",
                "rotation": 0,
                "color_filter": None
            }
            
            crystal_wells.append({"x": x, "y": y})
            
            if (x, y) in available_positions:
                available_positions.remove((x, y))
    
    # Add random optics (mirrors, prisms, splitters)
    num_optics = rng.randint(settings["optics"][0], settings["optics"][1])
    optic_types = ["mirror", "prism", "splitter"]
    
    for _ in range(min(num_optics, len(available_positions))):
        if available_positions:
            pos_idx = rng.randint(0, len(available_positions) - 1)
            x, y = available_positions.pop(pos_idx)
            
            optic_type = rng.choice(optic_types)
            rotation = rng.randint(0, 3) * 90
            
            grid[y][x] = {
                "type": optic_type,
                "rotation": rotation,
                "color_filter": None
            }
    
    # Find a good starting position for the player (empty cell)
    player_positions = [(x, y) for x, y in available_positions]
    if not player_positions:
        # Fallback: find any empty cell
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x]["type"] == "empty":
                    player_positions.append((x, y))
                    break
            if player_positions:
                break
    
    if player_positions:
        px, py = rng.choice(player_positions)
    else:
        px, py = 0, 0  # Fallback
    
    # Create the complete game state
    game_state = {
        "player_pos": {"x": px, "y": py},
        "grid": grid,
        "beam_sources": beam_sources,
        "crystal_wells": crystal_wells,
        "step_count": 0,
        "score": 0,
        "goals_reached": 0,
        "beam_segments": []
    }
    
    # Convert to JSON string
    def to_json_string(obj, indent=0):
        """Simple JSON encoder without imports"""
        spaces = "  " * indent
        
        if obj is None:
            return "null"
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif isinstance(obj, int):
            return str(obj)
        elif isinstance(obj, str):
            # Simple string escaping
            escaped = obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'"{escaped}"'
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            
            items = []
            for item in obj:
                items.append(to_json_string(item, indent + 1))
            
            if len(items) == 1 and len(items[0]) < 50:
                return f"[{items[0]}]"
            else:
                item_strings = [f"\n{spaces}  {item}" for item in items]
                return f"[{''.join(item_strings)}\n{spaces}]"
        
        elif isinstance(obj, dict):
            if not obj:
                return "{}"
            
            items = []
            for key, value in obj.items():
                key_str = to_json_string(key, indent + 1)
                value_str = to_json_string(value, indent + 1)
                items.append(f"{key_str}: {value_str}")
            
            if len(items) == 1 and len(items[0]) < 50:
                return f"{{{items[0]}}}"
            else:
                item_strings = [f"\n{spaces}  {item}" for item in items]
                return f"{{{''.join(item_strings)}\n{spaces}}}"
        else:
            return f'"{str(obj)}"'
    
    return to_json_string(game_state)


# Example usage and test cases
def generate_example_states():
    """Generate several example game states for testing"""
    
    examples = []
    
    # Easy puzzle
    examples.append(("easy_puzzle_1", generate_game_state_json(42, "easy")))
    
    # Medium puzzle  
    examples.append(("medium_puzzle_1", generate_game_state_json(123, "medium")))
    
    # Hard puzzle
    examples.append(("hard_puzzle_1", generate_game_state_json(456, "hard")))
    
    # Random puzzles
    examples.append(("random_1", generate_game_state_json(789, "medium")))
    examples.append(("random_2", generate_game_state_json(999, "hard")))
    
    return examples


def create_puzzle_with_solution():
    """Create a puzzle with a known solution path"""
    
    # Create a simple solvable puzzle manually
    grid = []
    for y in range(12):
        row = []
        for x in range(12):
            row.append({
                "type": "empty",
                "rotation": 0,
                "color_filter": None
            })
        grid.append(row)
    
    # Add beam source at left edge
    grid[5][0] = {"type": "beam_source", "rotation": 0, "color_filter": None}
    beam_sources = [{
        "position": {"x": 0, "y": 5},
        "direction": "EAST", 
        "color": "WHITE"
    }]
    
    # Add mirror to redirect beam
    grid[5][3] = {"type": "mirror", "rotation": 0, "color_filter": None}
    
    # Add crystal well as target
    grid[2][3] = {"type": "crystal_well", "rotation": 0, "color_filter": None}
    crystal_wells = [{"x": 3, "y": 2}]
    
    # Player starts near the action
    player_pos = {"x": 4, "y": 5}
    
    game_state = {
        "player_pos": player_pos,
        "grid": grid,
        "beam_sources": beam_sources,
        "crystal_wells": crystal_wells,
        "step_count": 0,
        "score": 0,
        "goals_reached": 0,
        "beam_segments": []
    }
    
    # Convert to JSON
    def to_json_string(obj, indent=0):
        spaces = "  " * indent
        
        if obj is None:
            return "null"
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif isinstance(obj, int):
            return str(obj)
        elif isinstance(obj, str):
            escaped = obj.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            items = [to_json_string(item, indent + 1) for item in obj]
            if len(items) == 1 and len(items[0]) < 50:
                return f"[{items[0]}]"
            item_strings = [f"\n{spaces}  {item}" for item in items]
            return f"[{''.join(item_strings)}\n{spaces}]"
        elif isinstance(obj, dict):
            if not obj:
                return "{}"
            items = []
            for key, value in obj.items():
                key_str = to_json_string(key, indent + 1)
                value_str = to_json_string(value, indent + 1)
                items.append(f"{key_str}: {value_str}")
            if len(items) <= 2 and all(len(item) < 30 for item in items):
                return f"{{{', '.join(items)}}}"
            item_strings = [f"\n{spaces}  {item}" for item in items]
            return f"{{{''.join(item_strings)}\n{spaces}}}"
        else:
            return f'"{str(obj)}"'
    
    return to_json_string(game_state)


if __name__ == "__main__":
    # Generate and print example states
    print("=== EASY PUZZLE ===")
    print(generate_game_state_json(42, "easy"))
    print("\n=== MEDIUM PUZZLE ===")
    print(generate_game_state_json(123, "medium"))
    print("\n=== HARD PUZZLE ===")
    print(generate_game_state_json(456, "hard"))
    print("\n=== SIMPLE SOLVABLE PUZZLE ===")
    print(create_puzzle_with_solution())
