#!/bin/bash

# Start virtual display
echo "Starting virtual display..."
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Wait for display to be ready
sleep 2

# Check if commands were passed as arguments
if [ $# -eq 0 ]; then
    echo "Starting game in interactive mode..."
    echo "The game is running in the background. You can now run automation commands:"
    echo ""
    echo "Available commands:"
    echo "  python3 automation.py \"click <x> <y>\"     - Send mouse click at coordinates"
    echo "  python3 automation.py \"keyboard <key>\"    - Send keyboard event (w, a, s, d, r, etc.)"
    echo "  python3 automation.py \"screenshot\"        - Take a screenshot"
    echo "  python3 automation.py \"wait\"              - Wait 1 second"
    echo ""
    echo "Example: python3 automation.py \"click 100 100\" \"click 300 300\" \"screenshot\""
    echo ""
    
    # Start the game and keep it running
    python game.py &
    GAME_PID=$!
    
    # Wait a bit for game to start
    sleep 3
    
    # Take initial screenshot
    python automation.py "screenshot"
    echo "✅ Game started! Initial screenshot taken."
    echo "💡 You can now run automation commands in this terminal."
    echo "💡 Type 'exit' to quit the container."
    
    # Setup cleanup function
    cleanup() {
        echo "Cleaning up..."
        kill $GAME_PID 2>/dev/null
        exit 0
    }
    trap cleanup SIGINT SIGTERM
    
    # Start an interactive shell
    /bin/bash
    
    # Cleanup when bash exits
    cleanup
else
    echo "Starting game with automation commands..."
    
    # Start the game in background
    python game.py &
    GAME_PID=$!
    
    # Wait a bit for game to start
    sleep 3
    
    # Run automation with provided commands
    python automation.py "$@"
    
    # Kill the game
    kill $GAME_PID 2>/dev/null
fi 