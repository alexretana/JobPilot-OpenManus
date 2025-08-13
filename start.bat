@echo off
setlocal enabledelayedexpansion

:: Parse command line arguments
set "MODE=both"
if "%~1"=="attached-backend" set "MODE=attached-backend"
if "%~1"=="attached-frontend" set "MODE=attached-frontend"
if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help
if not "%~1"=="" if not "%~1"=="attached-backend" if not "%~1"=="attached-frontend" (
    echo [ERROR] Invalid argument: %~1
    echo.
    goto :show_help
)

echo =============================================
echo      JobPilot-OpenManus Development Starter
if "%MODE%"=="attached-backend" echo              (Attached Backend Mode)
if "%MODE%"=="attached-frontend" echo              (Attached Frontend Mode)
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

if "%MODE%"=="attached-backend" (
    echo [INFO] Starting frontend in new window, backend will run attached...
    echo Press Ctrl+C to stop the backend server.
    echo.
    
    :: Start frontend in new window
    start "JobPilot Frontend" cmd /k "cd frontend && npm run dev && pause"
    
    :: Give frontend a moment to start
    powershell -Command "Start-Sleep -Seconds 2" >nul
    
    echo [INFO] Starting backend server in this window...
    echo You can now access:
    echo - Frontend: http://localhost:3000
    echo - Backend API: http://localhost:8080/api/health
    echo.
    
    :: Run backend in current shell
    python web_server.py
    
) else if "%MODE%"=="attached-frontend" (
    echo [INFO] Starting backend in new window, frontend will run attached...
    echo Press Ctrl+C to stop the frontend server.
    echo.
    
    :: Start backend in new window
    start "JobPilot Backend" cmd /k "python web_server.py && pause"
    
    :: Give backend a moment to start
    powershell -Command "Start-Sleep -Seconds 2" >nul
    
    echo [INFO] Starting frontend development server in this window...
    echo You can now access:
    echo - Frontend: http://localhost:3000
    echo - Backend API: http://localhost:8080/api/health
    echo.
    
    :: Run frontend in current shell
    cd frontend
    npm run dev
    cd ..
    
) else (
    :: Default mode - both in separate windows
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
)

exit /b 0

:show_help
echo Usage: start.bat [MODE]
echo.
echo Modes:
echo   (none)              - Start both servers in separate windows (default)
echo   attached-backend    - Start frontend in new window, backend attached to current shell
echo   attached-frontend   - Start backend in new window, frontend attached to current shell
echo   --help, -h          - Show this help message
echo.
echo Examples:
echo   start.bat                    # Both servers in separate windows
echo   start.bat attached-backend   # Frontend in new window, backend in current shell
echo   start.bat attached-frontend  # Backend in new window, frontend in current shell
echo.
echo Attached modes are useful for debugging or when you want to see live output
echo from one of the servers while the other runs in the background.
echo.
pause
exit /b 0
