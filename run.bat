@echo off
:: Setup virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment (Windows)
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo Error: Could not activate virtual environment. Exiting...
    exit /b 1
)

:: Install dependencies if not already installed
if not exist venv\Lib\site-packages\installed (
    if exist requirements.txt (
        echo Installing dependencies...
        pip install wheel
        pip install -r requirements.txt || (
            echo Error: Failed to install dependencies. Exiting...
            exit /b 1
        )
        echo. > venv\Lib\site-packages\installed
    ) else (
        echo Warning: requirements.txt not found. Skipping dependency installation.
    )
)

:: Copy .env file if not exists
if not exist .env (
    if exist .env-example (
        echo Copying configuration file...
        copy .env-example .env
    ) else (
        echo Warning: .env-example not found. Skipping configuration file setup.
    )
)

:: Pull latest changes from Git
echo Pulling latest changes from Git...
git pull || echo Warning: Git pull failed.

:: Run the main script in a loop
:loop
python main.py
if %errorlevel% neq 0 (
    echo Error: main.py exited with code %errorlevel%.
)
echo Restarting the program in 2 seconds... Press Ctrl+C to exit.
timeout /t 2 /nobreak >nul
goto :loop
