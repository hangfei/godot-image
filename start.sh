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
    echo "  python3 automation.py --window \$GAME_WINDOW_ID \"click <x> <y>\"     - Send mouse click at coordinates"
    echo "  python3 automation.py --window \$GAME_WINDOW_ID \"keyboard <key>\"    - Send keyboard event (w, a, s, d, r, etc.)"
    echo "  python3 automation.py --window \$GAME_WINDOW_ID \"screenshot\"        - Take a screenshot"
    echo "  python3 automation.py --window \$GAME_WINDOW_ID \"wait\"              - Wait 1 second"
    echo ""
    echo "Quick examples (using auto-detected window):"
    echo "  python3 automation.py --window \$GAME_WINDOW_ID \"keyboard w\" \"keyboard w\" \"keyboard d\" \"screenshot\""
    echo "  python3 automation.py --window \$GAME_WINDOW_ID \"click 500 400\" \"keyboard w\""
    echo ""
    echo "Alternative (without window targeting):"
    echo "  python3 automation.py \"click 100 100\" \"screenshot\""
    echo ""
    
    # Start the game and keep it running
    python game.py &
    GAME_PID=$!
    
    # Wait a bit for game to start
    sleep 3
    
    # Find the game window ID
    echo "🔍 Finding game window..."
    WINDOW_ID=""
    for i in {1..5}; do
        # Try different window search patterns
        for pattern in "GLB Asset Adventure" "pygame" "python"; do
            FOUND_ID=$(xdotool search --name "$pattern" 2>/dev/null | head -1)
            if [ ! -z "$FOUND_ID" ]; then
                WINDOW_TITLE=$(xdotool getwindowname $FOUND_ID 2>/dev/null)
                echo "Found window: ID=$FOUND_ID, Title='$WINDOW_TITLE'"
                WINDOW_ID=$FOUND_ID
                break 2
            fi
        done
        if [ ! -z "$WINDOW_ID" ]; then
            break
        fi
        sleep 1
    done
    
    # Fallback: if no window found by name, just use any available window
    if [ -z "$WINDOW_ID" ]; then
        echo "🔄 Fallback: Looking for any available window..."
        FOUND_ID=$(xdotool search --name ".*" 2>/dev/null | head -1)
        if [ ! -z "$FOUND_ID" ]; then
            WINDOW_TITLE=$(xdotool getwindowname $FOUND_ID 2>/dev/null)
            echo "Using fallback window: ID=$FOUND_ID, Title='$WINDOW_TITLE'"
            WINDOW_ID=$FOUND_ID
        fi
    fi
    
    # Export window ID for automation scripts
    if [ ! -z "$WINDOW_ID" ]; then
        export GAME_WINDOW_ID=$WINDOW_ID
        echo "✅ Game window found! Window ID: $WINDOW_ID"
        echo "📝 Window ID exported as GAME_WINDOW_ID environment variable"
    else
        echo "⚠️ Could not find game window automatically"
        echo "💡 You can list windows with: python3 automation.py --list-windows"
    fi
    
    # Take initial screenshot
    if [ ! -z "$WINDOW_ID" ]; then
        python automation.py --window $WINDOW_ID "screenshot"
    else
        python automation.py "screenshot"
    fi
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