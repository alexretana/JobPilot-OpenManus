"""
Server lifecycle management for E2E testing.

This module provides utilities to automatically start and stop backend and frontend
servers for end-to-end testing with proper cleanup and health checking.
"""

import asyncio
import subprocess
import time
import socket
import psutil
import threading
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)


class ServerManager:
    """Manages backend and frontend server lifecycle for testing."""
    
    def __init__(
        self,
        backend_port: int = 8001,
        frontend_port: int = 3001,
        backend_timeout: int = 30,
        frontend_timeout: int = 60
    ):
        self.backend_port = backend_port
        self.frontend_port = frontend_port
        self.backend_timeout = backend_timeout
        self.frontend_timeout = frontend_timeout
        
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        
        # Track if ports were already in use
        self.backend_was_running = False
        self.frontend_was_running = False
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            return result == 0
    
    def find_available_port(self, start_port: int, max_attempts: int = 100) -> int:
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            if not self.is_port_in_use(port):
                return port
        raise RuntimeError(f"Could not find available port starting from {start_port}")
    
    def wait_for_server(self, port: int, timeout: int = 30, endpoint: str = "/") -> bool:
        """Wait for server to be ready on specified port."""
        url = f"http://localhost:{port}{endpoint}"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 404]:  # 404 is fine, means server is responding
                    logger.info(f"Server ready on port {port}")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        logger.error(f"Server on port {port} not ready after {timeout} seconds")
        return False
    
    def start_backend_server(self) -> bool:
        """Start the backend server."""
        if self.is_port_in_use(self.backend_port):
            logger.info(f"Backend server already running on port {self.backend_port}")
            self.backend_was_running = True
            return True
        
        # Find available port if default is taken
        if self.backend_port != 8001 and self.is_port_in_use(self.backend_port):
            self.backend_port = self.find_available_port(8001)
            logger.info(f"Using alternative backend port: {self.backend_port}")
        
        logger.info(f"Starting backend server on port {self.backend_port}")
        
        try:
            # Start backend server
            env = {'PORT': str(self.backend_port)}
            self.backend_process = subprocess.Popen(
                ['python', 'web_server.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            # Wait for server to be ready
            if self.wait_for_server(self.backend_port, self.backend_timeout, "/api/health"):
                logger.info(f"Backend server started successfully on port {self.backend_port}")
                return True
            else:
                self.stop_backend_server()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start backend server: {e}")
            return False
    
    def start_frontend_server(self) -> bool:
        """Start the frontend development server."""
        if self.is_port_in_use(self.frontend_port):
            logger.info(f"Frontend server already running on port {self.frontend_port}")
            self.frontend_was_running = True
            return True
        
        # Find available port if default is taken
        if self.frontend_port != 3001 and self.is_port_in_use(self.frontend_port):
            self.frontend_port = self.find_available_port(3001)
            logger.info(f"Using alternative frontend port: {self.frontend_port}")
        
        logger.info(f"Starting frontend server on port {self.frontend_port}")
        
        try:
            # Check if frontend directory exists
            frontend_path = Path.cwd() / 'frontend'
            if not frontend_path.exists():
                logger.warning("Frontend directory not found, skipping frontend server")
                return True
            
            # Start frontend development server
            env = {'PORT': str(self.frontend_port)}
            self.frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=frontend_path
            )
            
            # Wait for server to be ready
            if self.wait_for_server(self.frontend_port, self.frontend_timeout):
                logger.info(f"Frontend server started successfully on port {self.frontend_port}")
                return True
            else:
                self.stop_frontend_server()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start frontend server: {e}")
            return False
    
    def stop_backend_server(self):
        """Stop the backend server."""
        if self.backend_was_running:
            logger.info("Backend server was already running, not stopping")
            return
        
        if self.backend_process:
            logger.info("Stopping backend server")
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Backend server did not terminate gracefully, killing")
                self.backend_process.kill()
            except Exception as e:
                logger.error(f"Error stopping backend server: {e}")
            
            self.backend_process = None
    
    def stop_frontend_server(self):
        """Stop the frontend server."""
        if self.frontend_was_running:
            logger.info("Frontend server was already running, not stopping")
            return
        
        if self.frontend_process:
            logger.info("Stopping frontend server")
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Frontend server did not terminate gracefully, killing")
                self.frontend_process.kill()
            except Exception as e:
                logger.error(f"Error stopping frontend server: {e}")
            
            self.frontend_process = None
    
    def start_all_servers(self) -> Dict[str, Any]:
        """Start both backend and frontend servers."""
        results = {
            'backend': self.start_backend_server(),
            'frontend': self.start_frontend_server(),
            'backend_port': self.backend_port,
            'frontend_port': self.frontend_port,
            'backend_url': f"http://localhost:{self.backend_port}",
            'frontend_url': f"http://localhost:{self.frontend_port}"
        }
        
        logger.info(f"Server startup results: {results}")
        return results
    
    def stop_all_servers(self):
        """Stop both backend and frontend servers."""
        logger.info("Stopping all servers")
        self.stop_backend_server()
        self.stop_frontend_server()
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get information about running servers."""
        return {
            'backend_port': self.backend_port,
            'frontend_port': self.frontend_port,
            'backend_url': f"http://localhost:{self.backend_port}",
            'frontend_url': f"http://localhost:{self.frontend_port}",
            'backend_running': self.is_port_in_use(self.backend_port),
            'frontend_running': self.is_port_in_use(self.frontend_port)
        }
    
    def health_check(self) -> Dict[str, bool]:
        """Perform health checks on running servers."""
        backend_healthy = False
        frontend_healthy = False
        
        # Check backend health
        try:
            response = requests.get(f"http://localhost:{self.backend_port}/api/health", timeout=5)
            backend_healthy = response.status_code == 200
        except requests.exceptions.RequestException:
            pass
        
        # Check frontend health
        try:
            response = requests.get(f"http://localhost:{self.frontend_port}", timeout=5)
            frontend_healthy = response.status_code in [200, 404]
        except requests.exceptions.RequestException:
            pass
        
        return {
            'backend': backend_healthy,
            'frontend': frontend_healthy
        }


@contextmanager
def test_servers(backend_port: int = 8001, frontend_port: int = 3001, start_frontend: bool = True):
    """Context manager for managing test servers."""
    manager = ServerManager(backend_port, frontend_port)
    
    try:
        # Start servers
        logger.info("Starting test servers")
        backend_started = manager.start_backend_server()
        frontend_started = True
        
        if start_frontend:
            frontend_started = manager.start_frontend_server()
        
        if not backend_started:
            raise RuntimeError("Failed to start backend server")
        
        if start_frontend and not frontend_started:
            logger.warning("Frontend server failed to start, continuing with backend only")
        
        yield manager
        
    finally:
        # Always cleanup
        logger.info("Cleaning up test servers")
        manager.stop_all_servers()


def cleanup_test_processes():
    """Clean up any leftover test processes."""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if any('web_server.py' in str(cmd) for cmd in cmdline):
                    logger.info(f"Killing leftover backend process: {proc.info['pid']}")
                    proc.terminate()
                elif any('npm run dev' in ' '.join(str(cmd) for cmd in cmdline) for cmd in [cmdline]):
                    logger.info(f"Killing leftover frontend process: {proc.info['pid']}")
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Helper functions for common testing patterns

def wait_for_element_visible(page, selector: str, timeout: int = 30000):
    """Wait for an element to be visible on the page."""
    return page.wait_for_selector(selector, state="visible", timeout=timeout)


def wait_for_api_response(page, url_pattern: str, timeout: int = 30000):
    """Wait for a specific API response."""
    return page.wait_for_response(lambda response: url_pattern in response.url, timeout=timeout)


def take_screenshot_on_failure(page, test_name: str):
    """Take a screenshot if a test fails."""
    try:
        screenshot_path = Path("screenshots") / f"{test_name}_failure.png"
        screenshot_path.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshot_path))
        logger.info(f"Screenshot saved: {screenshot_path}")
    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")


if __name__ == "__main__":
    # Test the server manager
    logging.basicConfig(level=logging.INFO)
    
    with test_servers() as servers:
        print("Servers started:")
        print(f"Backend: {servers.get_server_info()['backend_url']}")
        print(f"Frontend: {servers.get_server_info()['frontend_url']}")
        print(f"Health check: {servers.health_check()}")
        
        input("Press Enter to stop servers...")
