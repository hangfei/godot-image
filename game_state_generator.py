import json
import random
import time

def generate_random_game_state(filename=None, 
                             grid_width=8, 
                             grid_height=8,
                             score_range=(0, 500),
                             moves_range=(0, 50)):
    """
    Generate a random game state JSON file for Link & Max game
    
    Args:
        filename: Output filename (auto-generated if None)
        grid_width: Width of the gem grid
        grid_height: Height of the gem grid  
        score_range: (min_score, max_score) tuple
        moves_range: (min_moves, max_moves) tuple
    
    Returns:
        dict: The generated game state
    """
    
    # Generate random grid (gem types 1-7, matching the main game)
    grid = []
    for y in range(grid_height):
        row = []
        for x in range(grid_width):
            # Random gem type (1=Red, 2=Blue, 3=Green, 4=Yellow, 5=Purple, 6=Orange, 7=Cyan)
            gem_type = random.randint(1, 7)
            row.append(gem_type)
        grid.append(row)
    
    # Generate random game stats
    score = random.randint(*score_range)
    moves = random.randint(*moves_range)
    cursor_x = random.randint(0, grid_width - 1)
    cursor_y = random.randint(0, grid_height - 1)
    
    # Create game state data
    game_state = {
        'score': score,
        'moves': moves,
        'cursor_x': cursor_x,
        'cursor_y': cursor_y,
        'grid': grid,
        'timestamp': int(time.time() * 1000)
    }
    
    # Generate filename if not provided
    if filename is None:
        timestamp = int(time.time())
        filename = f"save_random_{score}_{moves}_{timestamp}.json"
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(game_state, f, indent=2)
    
    print(f"Generated random game state:")
    print(f"  Score: {score}")
    print(f"  Moves: {moves}")
    print(f"  Cursor: ({cursor_x}, {cursor_y})")
    print(f"  Saved to: {filename}")
    
    return game_state

# Example usage
if __name__ == "__main__":
    # Generate a few different scenarios
    
    print("🎲 Generating random game states...\n")
    
    # Fresh start
    generate_random_game_state("save_fresh_start.json", 
                              score_range=(0, 0), 
                              moves_range=(0, 0))
    
    print()
    
    # Mid-game
    generate_random_game_state("save_mid_game.json",
                              score_range=(100, 300),
                              moves_range=(20, 40))
    
    print()
    
    # High score game
    generate_random_game_state("save_high_score.json",
                              score_range=(500, 1000),
                              moves_range=(50, 80))
    
    print("\n✅ Done! Place any of these .json files in your game directory.") 