#!/bin/bash
echo "=== Werewolf AI Player Installer ==="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python not found. Please install Python first."
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi

echo "Installing required packages..."
echo
$PYTHON -m pip install openai python-dotenv

if [ $? -ne 0 ]; then
    echo "Error: Failed to install packages."
    exit 1
fi

echo
echo "Packages installed successfully."
echo

# Check if .env already exists
if [ -f .env ]; then
    echo ".env file already exists."
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation complete."
        exit 0
    fi
fi

echo "Please enter your OpenAI API key:"
read -r API_KEY

if [ -z "$API_KEY" ]; then
    echo "Error: API key cannot be empty."
    exit 1
fi

echo "Creating .env file..."
cat > .env << EOF
# OpenAI API Configuration
# Created by install_ai.sh

OPENAI_API_KEY=$API_KEY

# Optional: Model to use (default: gpt-3.5-turbo)
# OPENAI_MODEL=gpt-3.5-turbo
# OPENAI_MODEL=gpt-4

# Optional: Temperature (0.0 - 1.0, default: 0.7)
# OPENAI_TEMPERATURE=0.7

# Optional: Request timeout in seconds (default: 30)
# OPENAI_TIMEOUT=30
EOF

echo
echo "Done! .env file created with your API key."
echo
echo "=== Installation Complete ==="
echo
echo "To run the game with AI players:"
echo "  Interactive mode (ask which players are AI):"
echo "    $PYTHON Main.py"
echo
echo "  Directly specify AI players (example 3 AI players):"
echo "    $PYTHON Main.py --ai=1,2,3"
echo
echo "  Chinese language with 3 AI players:"
echo "    $PYTHON Main.py --lang=cn --ai=1,2,3"
echo
