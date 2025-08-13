#!/bin/bash

# Enable strict mode
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================="
echo "     JobPilot-OpenManus Development Starter"
echo "============================================="

# Check if we're in the right directory
if [[ ! -f "web_server.py" ]]; then
    log_error "web_server.py not found!"
    log_error "Please run this script from the JobPilot-OpenManus root directory."
    exit 1
fi

if [[ ! -d "frontend" ]]; then
    log_error "frontend directory not found!"
    log_error "Please ensure the frontend has been set up."
    exit 1
fi

# Check if Node.js and npm are available
log_info "Checking Node.js and npm..."

if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed or not in PATH!"
    log_error "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    log_error "npm is not available!"
    log_error "Please ensure npm is in your PATH."
    exit 1
fi

# Get versions for confirmation
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)

log_success "Node.js version: $NODE_VERSION"
log_success "npm version: $NPM_VERSION"

# Check if Python is available
log_info "Checking Python..."

if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    log_error "Python is not installed or not in PATH!"
    log_error "Please install Python and ensure it's in your PATH."
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
log_success "Python version: $PYTHON_VERSION"

# Check if frontend package.json exists
if [[ ! -f "frontend/package.json" ]]; then
    log_error "frontend/package.json not found!"
    log_error "Please ensure the frontend is properly set up."
    exit 1
fi

# Check if frontend is built for production mode
if [[ ! -d "frontend/dist" ]]; then
    log_warn "Frontend dist directory not found."
    log_info "Building frontend for production..."
    
    cd frontend
    log_info "Installing frontend dependencies..."
    npm install
    if [[ $? -ne 0 ]]; then
        log_error "Failed to install frontend dependencies!"
        exit 1
    fi
    
    log_info "Building frontend..."
    npm run build
    if [[ $? -ne 0 ]]; then
        log_error "Failed to build frontend!"
        exit 1
    fi
    cd ..
    
    log_success "Frontend built successfully!"
else
    log_success "Frontend dist directory found."
fi

# Check if node_modules exists in frontend
if [[ ! -d "frontend/node_modules" ]]; then
    log_info "Installing frontend dependencies..."
    cd frontend
    npm install
    if [[ $? -ne 0 ]]; then
        log_error "Failed to install frontend dependencies!"
        exit 1
    fi
    cd ..
    log_success "Frontend dependencies installed!"
fi

echo
log_info "Starting services..."
echo
echo "Frontend Dev Server: http://localhost:3000 (with hot reload)"
echo "Backend API Server:  http://localhost:8080"
echo
echo "Press Ctrl+C to stop both servers."
echo

# Function to cleanup background processes
cleanup() {
    echo
    log_info "Shutting down services..."
    if [[ ! -z "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
    fi
    if [[ ! -z "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
    fi
    log_success "Services stopped."
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Function to check if a port is available
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tulpn | grep ":$port " >/dev/null 2>&1; then
            return 1
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tulpn | grep ":$port " >/dev/null 2>&1; then
            return 1
        fi
    fi
    return 0
}

# Check if ports are available
if ! check_port 8080; then
    log_warn "Port 8080 is already in use. Backend may not start properly."
fi

if ! check_port 3000; then
    log_warn "Port 3000 is already in use. Frontend may not start properly."
fi

# Start backend server in background
log_info "Starting backend server..."
$PYTHON_CMD web_server.py &
BACKEND_PID=$!

# Give backend a moment to start
sleep 3

# Start frontend development server in background
log_info "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
log_success "Both servers are starting!"
echo
echo "You can now access:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8080/api/health"
echo
echo "Press Ctrl+C to stop both servers."

# Wait for background processes
wait
