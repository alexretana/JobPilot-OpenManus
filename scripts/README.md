# Development Scripts

This directory contains development and startup scripts for running JobPilot-OpenManus.

## Scripts

### `start.sh` (Linux/macOS)

Main startup script that:

- Validates dependencies (Node.js, npm, Python)
- Installs frontend dependencies if needed
- Builds the frontend for production
- Starts the backend server on port 8080
- Starts the frontend dev server on port 3000
- Opens both services in separate terminals

### `start.bat` (Windows)

Windows version of the main startup script with the same functionality as `start.sh`.

### `start-dev.bat` (Windows Development)

Development-specific startup script for Windows with additional development tools and debugging enabled.

## Usage

### Linux/macOS:

```bash
./scripts/start.sh
```

### Windows:

```cmd
scripts\start.bat
```

### Windows Development:

```cmd
scripts\start-dev.bat
```

## Requirements

All scripts expect to be run from the project root directory and require:

- Python 3.12+
- Node.js 18+
- npm package manager

## What the Scripts Do

1. **Dependency Check**: Verify all required tools are installed
2. **Frontend Setup**: Install npm dependencies and build the production frontend
3. **Server Startup**: Launch the FastAPI backend server
4. **Development Server**: Start the Vite development server with hot reload
5. **Browser Opening**: Automatically open the application in your default browser

## Output

- **Backend API**: `http://localhost:8080`
- **Frontend Development**: `http://localhost:3000` (with hot reload)
- **Production Build**: Served at `http://localhost:8080` (backend serves static files)

## Troubleshooting

If scripts fail:

1. Ensure you're running from the project root directory
2. Check that Python 3.12+ and Node.js 18+ are installed
3. Verify npm is available in your PATH
4. Check port 8080 and 3000 are not in use by other applications
