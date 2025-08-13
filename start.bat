@echo off
setlocal enabledelayedexpansion

echo =============================================
echo      JobPilot-OpenManus Development Starter
echo =============================================

:: Check if we're in the right directory
if not exist "web_server.py" (
    echo [ERROR] web_server.py not found!
    echo Please run this script from the JobPilot-OpenManus root directory.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] frontend directory not found!
    echo Please ensure the frontend has been set up.
    pause
    exit /b 1
)

:: Check if Node.js and npm are available
echo [INFO] Checking Node.js and npm...
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not available!
    echo Please ensure npm is in your PATH.
    pause
    exit /b 1
)

:: Get versions for confirmation
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i

echo [OK] Node.js version: %NODE_VERSION%
echo [OK] npm version: %NPM_VERSION%

:: Check if Python is available
echo [INFO] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python and ensure it's in your PATH.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python version: %PYTHON_VERSION%

:: Check if frontend package.json exists
if not exist "frontend\package.json" (
    echo [ERROR] frontend/package.json not found!
    echo Please ensure the frontend is properly set up.
    pause
    exit /b 1
)

:: Check if frontend is built for production mode
if not exist "frontend\dist" (
    echo [WARN] Frontend dist directory not found.
    echo Building frontend for production...
    
    pushd frontend
    echo [INFO] Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies!
        popd
        pause
        exit /b 1
    )
    
    echo [INFO] Building frontend...
    call npm run build
    if errorlevel 1 (
        echo [ERROR] Failed to build frontend!
        popd
        pause
        exit /b 1
    )
    popd
    
    echo [OK] Frontend built successfully!
) else (
    echo [OK] Frontend dist directory found.
)

:: Check if node_modules exists in frontend
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    pushd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies!
        popd
        pause
        exit /b 1
    )
    popd
    echo [OK] Frontend dependencies installed!
)

echo.
echo [INFO] Starting services...
echo.
echo Frontend Dev Server: http://localhost:3000 (with hot reload)
echo Backend API Server:  http://localhost:8080
echo.
echo Press Ctrl+C in any window to stop both servers.
echo.

:: Start backend server in a new command prompt
echo [INFO] Starting backend server...
start "JobPilot Backend" cmd /k "python web_server.py && pause"

:: Give backend a moment to start
powershell -Command "Start-Sleep -Seconds 2" >nul

:: Start frontend development server in a new command prompt
echo [INFO] Starting frontend development server...
start "JobPilot Frontend" cmd /k "cd frontend && npm run dev && pause"

echo.
echo [SUCCESS] Both servers should be starting in separate windows.
echo.
echo You can now access:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8080/api/health
echo.
echo This window can be closed. Use the individual server windows to stop services.
echo.
pause
