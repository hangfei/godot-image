# Pygame GUI Automation with Docker

This project provides a Docker-based solution for automating interactions with pygame GUI applications and capturing screenshots. It's specifically designed to work with the Tic-Tac-Toe game but can be adapted for other pygame applications.

## Features

- 🖥️ **Virtual Display**: Runs pygame applications in a headless Docker environment using Xvfb
- 🎮 **Input Automation**: Supports keyboard events and mouse clicks
- 📸 **Screenshot Capture**: Automatically takes screenshots after each action
- 🐳 **Containerized**: Fully contained Docker environment with all dependencies
- 🔧 **Easy to Use**: Simple command-line interface for automation

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t pygame-automation .
```

### 2. Basic Usage

Run with automation commands:

```bash
# Create a screenshots directory
mkdir screenshots

# Run automation with commands
docker run --rm -v $(pwd)/screenshots:/app/screenshots pygame-automation \
  "click 100 100" \
  "click 300 300" \
  "keyboard r" \
  "screenshot"
```

### 3. Run Example Scripts

```bash
# Make the example script executable and run it
chmod +x example_usage.py
python example_usage.py
```

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `click <x> <y>` | Click at coordinates (x, y) | `click 200 300` |
| `keyboard <key>` | Send keyboard event | `keyboard w` |
| `screenshot` | Take a manual screenshot | `screenshot` |
| `wait` | Wait for 1 second | `wait` |

### Supported Keys

- **Game controls**: `w`, `a`, `s`, `d`
- **Game actions**: `r` (restart)
- **Special keys**: `space`, `enter`, `esc`
- Any other single character key

## Game Coordinates

For the Tic-Tac-Toe game (600x600 pixels), the grid squares are approximately:

```
(100,100)  (300,100)  (500,100)
(100,300)  (300,300)  (500,300)  
(100,500)  (300,500)  (500,500)
```

## File Structure

```
godot-image/
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
├── game.py                 # Your pygame application
├── automation.py          # Automation and screenshot logic
├── start.sh               # Container startup script
├── example_usage.py       # Example automation scripts
└── README.md              # This file
```

## Usage Examples

### Example 1: Simple Game Play

```bash
docker run --rm -v $(pwd)/screenshots:/app/screenshots pygame-automation \
  "click 100 100" \
  "click 300 300" \
  "click 500 500"
```

### Example 2: Complete Game Sequence

```bash
docker run --rm -v $(pwd)/screenshots:/app/screenshots pygame-automation \
  "click 300 300" \
  "click 100 100" \
  "click 500 500" \
  "click 100 500" \
  "click 300 100" \
  "keyboard r" \
  "screenshot"
```

### Example 3: Interactive Mode

```bash
# Run without commands to see available options
docker run --rm -v $(pwd)/screenshots:/app/screenshots pygame-automation
```

## Screenshots

Screenshots are automatically saved after each action with descriptive names:

- `screenshot_001_initial.png` - Initial game state
- `screenshot_002_click_100_100.png` - After clicking at (100,100)
- `screenshot_003_keyboard_r.png` - After pressing 'r' key
- `screenshot_004_manual.png` - Manual screenshot

## Development

### Modifying the Game

To use with a different pygame application:

1. Replace `game.py` with your pygame application
2. Update the window detection in `automation.py` (search for window name)
3. Adjust coordinates and commands as needed

### Adding New Commands

Edit `automation.py` and add new command handlers in the `execute_command` method:

```python
elif command.startswith("my_command "):
    # Your custom command logic here
    pass
```

### Debugging

To see what's happening inside the container:

```bash
# Run interactively
docker run -it --rm -v $(pwd)/screenshots:/app/screenshots pygame-automation bash

# Inside container, start display and run components manually
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
python game.py &
python automation.py "screenshot"
```

## Troubleshooting

### Common Issues

1. **No screenshots generated**: Check that the screenshots directory is mounted correctly
2. **Commands not working**: Ensure the virtual display is ready (the system waits automatically)
3. **Game not responding**: Check that the game window is properly detected

### Logs

Container logs will show:
- Virtual display startup
- Game initialization  
- Command execution status
- Screenshot save confirmations

## Requirements

- Docker
- At least 1GB RAM for the container
- Write permissions for screenshot directory

## License

This project is provided as-is for educational and development purposes. 