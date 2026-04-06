#!/bin/bash
echo "=== Werewolf AI Player Installer ==="
echo

# Auto-detect Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Python not found. Attempting to install..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if ! command -v brew &> /dev/null; then
                echo "Homebrew not found. Please install Python manually."
                exit 1
            fi
            brew install python
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux - try common package managers
            if command -v apt &> /dev/null; then
                sudo apt update && sudo apt install -y python3 python3-pip
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y python3 python3-pip
            elif command -v yum &> /dev/null; then
                sudo yum install -y python3 python3-pip
            else
                echo "Could not detect package manager. Please install Python manually."
                exit 1
            fi
        else
            echo "Unsupported OS. Please install Python manually."
            exit 1
        fi
    fi
fi

if ! command -v python3 &> /dev/null; then
    PYTHON=python
else
    PYTHON=python3
fi

echo "Step 2: Select AI API Provider"
echo
echo "1 = OpenAI (default, GPT-3.5/GPT-4)"
echo "2 = Anthropic (Claude)"
echo
read -p "Enter your choice (1 or 2): " provider_choice

if [[ "$provider_choice" == "2" ]]; then
    PROVIDER="anthropic"
    PACKAGE_NAME="anthropic"
    ENV_NAME="ANTHROPIC_API_KEY"
    DEFAULT_MODEL="claude-3-sonnet-20240229"
    echo "Selected: Anthropic Claude"
else
    PROVIDER="openai"
    PACKAGE_NAME="openai"
    ENV_NAME="OPENAI_API_KEY"
    DEFAULT_MODEL="gpt-3.5-turbo"
    echo "Selected: OpenAI GPT"
fi

echo
echo "Installing required packages..."
echo
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install $PACKAGE_NAME python-dotenv

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

echo
echo "Please enter your $ENV_NAME:"
read -r API_KEY

if [ -z "$API_KEY" ]; then
    echo "Error: API key cannot be empty."
    exit 1
fi

echo "Creating .env file..."
cat > .env << EOF
# AI API Configuration
# Created by install_ai.sh

# API Provider: $PROVIDER
PROVIDER=$PROVIDER

$ENV_NAME=$API_KEY

# Model selection
${PROVIDER}_MODEL=$DEFAULT_MODEL

# Optional: Temperature (0.0 - 1.0, default: 0.7)
TEMPERATURE=0.7

# Optional: Request timeout in seconds (default: 30)
TIMEOUT=30
EOF

echo
echo "Done! .env file created with your configuration."
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
