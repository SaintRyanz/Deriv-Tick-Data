@echo off
echo Starting Deriv Index Tick Data Fetcher...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated.
)

REM Check if required packages are installed
echo Checking required packages...
pip show websocket-client >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install required packages.
        pause
        exit /b 1
    )
)

REM Run the Python application
echo Starting application...
python main.py

REM If the application exits with an error, pause to see the output
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error. Press any key to close...
    pause
) else (
    echo.
    echo Application closed successfully.
    pause
)
