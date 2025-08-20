def generate_game_state():
    """Generate a random game state for Clockwork Crypts with no imports needed"""
    grid_size = 12
    
    # Create empty grid
    grid = [["empty" for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Border walls
    for i in range(grid_size):
        grid[0][i] = "wall"
        grid[grid_size-1][i] = "wall"
        grid[i][0] = "wall"
        grid[i][grid_size-1] = "wall"
    
    # Add some internal walls for complexity
    wall_positions = [(3, 5), (5, 3), (7, 8), (8, 4), (4, 9), (6, 2), (2, 8)]
    for x, y in wall_positions:
        if 1 <= x < grid_size-1 and 1 <= y < grid_size-1:
            grid[y][x] = "wall"
    
    # Create gear system - 4 interconnected gears
    gear_nodes = [
        {"x": 4, "y": 4, "phase": 0, "connections": [1, 2]},
        {"x": 8, "y": 4, "phase": 1, "connections": [0, 2]},
        {"x": 6, "y": 8, "phase": 2, "connections": [0, 1]},
        {"x": 2, "y": 7, "phase": 3, "connections": []}
    ]
    
    for gear in gear_nodes:
        grid[gear["y"]][gear["x"]] = "gear"
    
    # Create doors linked to gears
    doors = [
        {"x": 6, "y": 4, "required_phase": 2, "gear_id": 0, "is_open": False},
        {"x": 8, "y": 6, "required_phase": 0, "gear_id": 1, "is_open": False},
        {"x": 4, "y": 8, "required_phase": 1, "gear_id": 2, "is_open": False}
    ]
    
    for door in doors:
        grid[door["y"]][door["x"]] = "door"
    
    # Create levers to control gears
    levers = [
        {"x": 2, "y": 4, "target_gear_id": 0, "is_activated": False},
        {"x": 9, "y": 7, "target_gear_id": 1, "is_activated": False}
    ]
    
    for lever in levers:
        grid[lever["y"]][lever["x"]] = "lever"
    
    # Create moving platforms
    moving_platforms = [
        {"x": 5, "y": 6, "target_x": 7, "target_y": 6, "gear_id": 2, "move_on_phase": 1}
    ]
    
    # Place treasures
    treasures = [
        {"x": 3, "y": 2, "value": 25, "collected": False},
        {"x": 9, "y": 2, "value": 35, "collected": False},
        {"x": 2, "y": 9, "value": 40, "collected": False},
        {"x": 9, "y": 9, "value": 30, "collected": False},
        {"x": 6, "y": 2, "value": 50, "collected": False}
    ]
    
    for treasure in treasures:
        grid[treasure["y"]][treasure["x"]] = "treasure"
    
    # Place exit
    grid[10][10] = "exit"
    
    # Return complete game state
    return {
        "player_x": 1,
        "player_y": 1,
        "tick_count": 0,
        "action_count": 0,
        "score": 0,
        "key_fragments": 0,
        "level": 1,
        "grid": grid,
        "gear_nodes": gear_nodes,
        "doors": doors,
        "levers": levers,
        "moving_platforms": moving_platforms,
        "treasures": treasures,
        "level_start_time": 0.0,
        "move_streak": 0,
        "max_moves_for_bonus": 35
    }
