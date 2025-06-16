@echo off
:: ============================================================================
::  CodeDump Builder
::
::  Creates a single-file GUI executable (CodeDump.exe) using PyInstaller.
::
::  What the script does:
::  1. Ask for a version string.
::  2. Activate the existing virtual environment "venv"   (create it once
::     with   python -m venv venv   and pip install -r requirements if needed).
::  3. Ensure PyInstaller is installed/updated in that venv.
::  4. Run PyInstaller with --onefile --windowed, bundling codedump_gui.py.
::  5. Clean up build artefacts (.spec file + build/ dir) on success.
:: ============================================================================

TITLE CodeDump Builder

echo.
set /p "VERSION=Enter version number for this build (e.g., 1.0.0): "
if "%VERSION%"=="" (
    echo No version entered. Exiting.
    pause
    exit /b 1
)

rem ---------------------------------------------------------------------------
rem  Configure names you might want to tweak
rem ---------------------------------------------------------------------------
set "VENV_DIR=venv"
set "OUTPUT_NAME=CodeDump_v%VERSION%"
set "SPEC_FILE=%OUTPUT_NAME%.spec"
set "ENTRY_SCRIPT=codedump_gui.py"
set "ICON_FILE=codedump.ico"    :: optional – comment out if you have no .ico

rem ---------------------------------------------------------------------------
rem  Check / activate venv
rem ---------------------------------------------------------------------------
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo.
    echo ERROR: Virtual environment "%VENV_DIR%" not found.
    echo Create one first:   python -m venv %VENV_DIR%
    echo then activate it and   pip install pyinstaller pyperclip
    pause
    exit /b 1
)

echo.
echo Activating virtual environment "%VENV_DIR%"...
call "%VENV_DIR%\Scripts\activate.bat"

rem ---------------------------------------------------------------------------
rem  Make sure PyInstaller is available in the venv
rem ---------------------------------------------------------------------------
echo Checking / installing PyInstaller...
python -m pip install --upgrade pyinstaller >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to install or upgrade PyInstaller.
    pause
    exit /b 1
)

rem ---------------------------------------------------------------------------
rem  Build command
rem ---------------------------------------------------------------------------
echo.
echo ============================= BUILD START ==============================
echo.

set "PI_CMD=pyinstaller --onefile --windowed --name "%OUTPUT_NAME%" "%ENTRY_SCRIPT%""

rem Add icon if it exists
if exist "%ICON_FILE%" (
    set "PI_CMD=%PI_CMD% --icon "%ICON_FILE%""
)

echo Running: %PI_CMD%
%PI_CMD%
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed – see messages above.
    echo No cleanup performed.
    pause
    exit /b 1
)

rem ---------------------------------------------------------------------------
rem  Cleanup on success
rem ---------------------------------------------------------------------------
echo.
echo Build succeeded. Cleaning up PyInstaller temp files...

if exist "build" (
    rmdir /s /q build
)
if exist "%SPEC_FILE%" (
    del "%SPEC_FILE%"
)

echo.
echo ======================================================================
echo   CLEANUP COMPLETE!
echo ======================================================================
echo.
echo Your executable is ready:
echo    %cd%\dist\%OUTPUT_NAME%.exe
echo.
echo Share this one file – recipients do NOT need Python installed.
echo.

pause
