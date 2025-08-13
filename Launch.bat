::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFAtVXheDH3ntUONOsb3Hy++UqVkSRN4SW5zeyKKLMtAK1kznepg+6nZbjcUPBB5KMBuoYW8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSzk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+IeA==
::cxY6rQJ7JhzQF1fEqQJhZkgYHGQ=
::ZQ05rAF9IBncCkqN+0xwdVsFAlfMbAs=
::ZQ05rAF9IAHYFVzEqQIdIRVRTxaDOn/6NbAO/u3pr8eGrEwaUfBf
::eg0/rx1wNQPfEVWB+kM9LVsJDCiDKWW5Dvse6fyb
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWHiX9UwTOhpSWESmGX3a
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATEphJie1t1XwWMH3m7AKFczM3tjw==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFAtVXheDH3ntUONOsb3Hy+WEt0AYWvYsRKjSzpybItw+40vhdoQs0G4Xq84eGh5KMz+qYA4zrHwPkVGsC+qVvQriWEmP8gsDHndignGQoCoubtBgn9FN1ji7nA==
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
setlocal enabledelayedexpansion
title Minecraft Server Manager Launcher
echo Starting Minecraft Server Manager...

:: Parse command line arguments
set WEB_MODE=
set DIRECT_LAUNCH=

:parse_args
if "%~1"=="" goto end_parse_args
if /i "%~1"=="--web" set WEB_MODE=1
if /i "%~1"=="--php" set WEB_MODE=php
if /i "%~1"=="--python" set WEB_MODE=python
if /i "%~1"=="--gui" set DIRECT_LAUNCH=gui
shift
goto parse_args
:end_parse_args

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

:: Direct launch based on arguments
if "%DIRECT_LAUNCH%"=="gui" (
    echo Launching Desktop GUI directly...
    python mc_server_manager_gui.py
    goto end
)

if "%WEB_MODE%"=="python" (
    echo Launching Python Web Interface directly...
    start "Python Web Server" python web_gui.py
    timeout /t 2 >nul
    start http://localhost:5000
    goto end
)

if "%WEB_MODE%"=="php" (
    echo Launching PHP Web Interface directly...
    php -v >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo PHP is not installed or not in PATH
        echo Please install PHP 7.4 or higher
        pause
        exit /b 1
    )
    start "PHP Web Server" php -S localhost:8000
    timeout /t 2 >nul
    start http://localhost:8000/index.php
    goto end
)

:: Launch the GUI launcher if no specific mode was requested
python gui_launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo Failed to start the application
    pause
    exit /b 1
)

:end
echo Minecraft Server Manager has been closed.
pause