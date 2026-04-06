@echo off
echo === Werewolf AI Player Installer ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python first from https://www.python.org/
    pause
    exit /b 1
)

echo Installing required packages...
echo.
python -m pip install openai python-dotenv

if errorlevel 1 (
    echo.
    echo Error: Failed to install packages.
    pause
    exit /b 1
)

echo.
echo Packages installed successfully.
echo.

REM Check if .env already exists
if exist .env (
    echo .env file already exists.
    set /p overwrite="Do you want to overwrite it? (y/n) "
    if /i not "%overwrite%"=="y" (
        echo.
        echo Installation complete.
        pause
        exit /b 0
    )
)

echo.
echo Please enter your OpenAI API key:
set /p API_KEY=

if "%API_KEY%"=="" (
    echo Error: API key cannot be empty.
    pause
    exit /b 1
)

echo.
echo Creating .env file...

(
echo # OpenAI API Configuration
echo # Created by install_ai.bat
echo.
echo OPENAI_API_KEY=%API_KEY%
echo.
echo # Optional: Model to use (default: gpt-3.5-turbo^)
echo # OPENAI_MODEL=gpt-3.5-turbo
echo # OPENAI_MODEL=gpt-4
echo.
echo # Optional: Temperature (0.0 - 1.0, default: 0.7^)
echo # OPENAI_TEMPERATURE=0.7
echo.
echo # Optional: Request timeout in seconds (default: 30^)
echo # OPENAI_TIMEOUT=30
) > .env

echo.
echo Done! .env file created with your API key.
echo.
echo === Installation Complete ===
echo.
echo To run the game with AI players:
echo.
echo   Interactive mode (ask which players are AI):
echo     python Main.py
echo.
echo   Directly specify AI players (example 3 AI players):
echo     python Main.py --ai=1,2,3
echo.
echo   Chinese language with 3 AI players:
echo     python Main.py --lang=cn --ai=1,2,3
echo.
pause
