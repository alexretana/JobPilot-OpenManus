@echo off
echo Starting JobPilot Development Environment...
echo.

echo Starting Frontend Development Server...
start "Frontend" cmd /c "cd frontend && npm run dev"

echo Waiting for frontend to start...
timeout /t 3 /nobreak > nul

echo.
echo Both services are starting...
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop all services...
pause > nul

echo Stopping services...
taskkill /f /im node.exe > nul 2>&1
echo Development environment stopped.
