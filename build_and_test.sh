#!/bin/bash

set -e  # Exit on any error

echo "🐳 Building pygame automation Docker image..."
docker build -t pygame-automation .

echo "✨ Docker image built successfully!"

echo "📂 Creating screenshots directory..."
mkdir -p screenshots

echo "🎮 Testing automation with a simple sequence..."
docker run --rm -v $(pwd)/screenshots:/app/screenshots pygame-automation \
  ./start.sh "click 300 300" "click 100 100" "click 500 500" "keyboard r" "screenshot"

echo "✅ Test completed!"
echo "📸 Check the 'screenshots' directory for captured images."

# List generated screenshots
if [ -d "screenshots" ] && [ "$(ls -A screenshots)" ]; then
    echo ""
    echo "Generated screenshots:"
    ls -la screenshots/
else
    echo "❌ No screenshots were generated. Check the Docker logs above for errors."
fi

echo ""
echo "🚀 Ready to use! Try these commands:"
echo ""
echo "For interactive mode:"
echo "  docker run -it --rm -v \$(pwd)/screenshots:/app/screenshots pygame-automation"
echo "  Then inside the container:"
echo "    python3 automation.py \"click 100 100\" \"click 300 300\" \"screenshot\""
echo ""
echo "For batch mode:"
echo "  docker run --rm -v \$(pwd)/screenshots:/app/screenshots pygame-automation ./start.sh \"click 100 100\" \"click 300 300\""
echo ""
echo "Or run locally:"
echo "  python example_usage.py" 