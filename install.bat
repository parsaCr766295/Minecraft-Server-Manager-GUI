@echo off
echo Installing Minecraft Server Manager...

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

:: Install required packages
echo Installing required packages...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

echo Installation completed successfully!
echo You can now run the application using launch.bat

pause