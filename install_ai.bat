@echo off
setlocal enabledelayedexpansion
echo === Werewolf AI Player Installer ===
echo.

echo Step 1: Checking Python installation...
echo.

python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do echo Found Python: %%V
    goto python_found
)

echo Python not found on this system.
echo.
set /p install_python="Do you want to automatically install Python 3.11? (y/n) "
if /i not "!install_python!"=="y" (
    echo.
    echo Please install Python manually from https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo.
echo Downloading Python 3.11 installer...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', 'python-installer.exe')"

if not exist python-installer.exe (
    echo.
    echo Error: Failed to download Python installer.
    echo Please install Python manually from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Running Python installer...
echo IMPORTANT: Please check "Add Python to PATH" when prompted!
start /wait python-installer.exe /passive InstallAllUsers=0 PrependPath=1 Include_doc=0 Include_launcher=0

if errorlevel 1 (
    echo.
    echo Warning: Installer exited with error. Checking if Python is now available...
)

del python-installer.exe

rem Check again after install
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Error: Python still not found in PATH.
    echo Please restart this installer after installation completes.
    pause
    exit /b 1
)

:python_found
echo.
echo Python is ready.
echo.

echo Step 2: Select AI API Provider
echo.
echo 1 = OpenAI (default, GPT-3.5/GPT-4)
echo 2 = Anthropic (Claude)
echo.
set /p provider_choice="Enter your choice (1 or 2): "

if "!provider_choice!"=="2" (
    set PROVIDER=anthropic
    set PACKAGE_NAME=anthropic
    set ENV_NAME=ANTHROPIC_API_KEY
    set DEFAULT_MODEL=claude-3-sonnet-20240229
    echo Selected: Anthropic Claude
) else (
    set PROVIDER=openai
    set PACKAGE_NAME=openai
    set ENV_NAME=OPENAI_API_KEY
    set DEFAULT_MODEL=gpt-3.5-turbo
    echo Selected: OpenAI GPT
)

echo.
echo Step 3: Installing required packages...
echo.

python -m pip install --upgrade pip
python -m pip install %PACKAGE_NAME% python-dotenv

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
    if /i not "!overwrite!"=="y" (
        echo.
        echo Installation complete.
        pause
        exit /b 0
    )
)

echo.
echo Please enter your %ENV_NAME%:
set /p API_KEY=

if "!API_KEY!"=="" (
    echo Error: API key cannot be empty.
    pause
    exit /b 1
)

echo.
echo Creating .env file...

(
echo # AI API Configuration
echo # Created by install_ai.bat
echo.
echo # API Provider: %PROVIDER%
echo PROVIDER=%PROVIDER%
echo.
echo %ENV_NAME%=%API_KEY%
echo.
echo # Model selection
echo %PROVIDER%_MODEL=%DEFAULT_MODEL%
echo.
echo # Optional: Temperature (0.0 - 1.0, default: 0.7)
echo TEMPERATURE=0.7
echo.
echo # Optional: Request timeout in seconds (default: 30)
echo TIMEOUT=30
) > .env

echo.
echo Done! .env file created with your configuration.
echo.

echo Step 4: Updating AI code for selected provider...
echo.

if "%PROVIDER%"=="anthropic" (
    echo Configuring for Anthropic Claude...
    echo Support for Anthropic will be added to ai.py
) else (
    echo Configured for OpenAI.
)

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
