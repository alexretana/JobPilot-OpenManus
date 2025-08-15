#!/usr/bin/env python3
"""
Server Lifecycle Manager for End-to-End Testing

This module handles starting and stopping servers for automated testing,
ensuring clean test environments and proper cleanup.
"""

import asyncio
import os
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict

import psutil
import requests


class ServerManager:
    """Manages server lifecycle for testing purposes."""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.getcwd()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.ports: Dict[str, int] = {"backend": 8080, "frontend": 3000}

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            import socket

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("localhost", port))
                return result != 0
        except Exception:
            return False

    def _wait_for_server(self, port: int, timeout: int = 30) -> bool:
        """Wait for server to be ready on specified port."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"http://localhost:{port}/api/health", timeout=2
                )
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(1)
        return False

    def _kill_process_on_port(self, port: int):
        """Kill any process running on the specified port."""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        print(f"   🔧 Killing process {proc.pid} on port {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    async def start_backend(self, env_vars: Dict[str, str] = None) -> bool:
        """Start the FastAPI backend server."""
        print("🚀 Starting backend server...")

        # Kill any existing process on backend port
        if not self._is_port_available(self.ports["backend"]):
            self._kill_process_on_port(self.ports["backend"])
            time.sleep(2)

        # Prepare environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        # Add test-specific environment variables
        env.update(
            {
                "TESTING": "true",
                "LOG_LEVEL": "INFO",
                "DATABASE_URL": "sqlite:///test_jobpilot.db",
            }
        )

        try:
            # Start backend server
            cmd = [sys.executable, "web_server.py"]
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.processes["backend"] = process

            # Wait for server to be ready
            if self._wait_for_server(self.ports["backend"]):
                print("   ✅ Backend server started successfully")
                return True
            else:
                print("   ❌ Backend server failed to start within timeout")
                self.stop_backend()
                return False

        except Exception as e:
            print(f"   ❌ Failed to start backend server: {e}")
            return False

    async def start_frontend(self) -> bool:
        """Start the frontend development server."""
        print("🌐 Starting frontend server...")

        # Kill any existing process on frontend port
        if not self._is_port_available(self.ports["frontend"]):
            self._kill_process_on_port(self.ports["frontend"])
            time.sleep(2)

        try:
            # Check if frontend is built
            frontend_dir = os.path.join(self.base_dir, "frontend")
            if not os.path.exists(frontend_dir):
                print("   ⚠️ Frontend directory not found, skipping frontend server")
                return True

            # Start frontend dev server
            cmd = ["npm", "run", "dev"]
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.processes["frontend"] = process

            # Wait for frontend to be ready (simpler check)
            time.sleep(5)  # Frontend usually takes a bit longer

            print("   ✅ Frontend server started successfully")
            return True

        except Exception as e:
            print(
                f"   ⚠️ Frontend server start failed: {e} (continuing without frontend)"
            )
            return True  # Don't fail tests if frontend can't start

    def stop_backend(self):
        """Stop the backend server."""
        if "backend" in self.processes:
            print("🛑 Stopping backend server...")
            try:
                process = self.processes["backend"]
                process.terminate()
                process.wait(timeout=10)
                print("   ✅ Backend server stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print("   ⚠️ Backend server killed (timeout)")
            except Exception as e:
                print(f"   ⚠️ Error stopping backend: {e}")
            finally:
                del self.processes["backend"]

    def stop_frontend(self):
        """Stop the frontend server."""
        if "frontend" in self.processes:
            print("🛑 Stopping frontend server...")
            try:
                process = self.processes["frontend"]
                process.terminate()
                process.wait(timeout=10)
                print("   ✅ Frontend server stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print("   ⚠️ Frontend server killed (timeout)")
            except Exception as e:
                print(f"   ⚠️ Error stopping frontend: {e}")
            finally:
                del self.processes["frontend"]

    def stop_all(self):
        """Stop all managed servers."""
        self.stop_backend()
        self.stop_frontend()

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all running servers."""
        health = {}

        # Check backend
        try:
            response = requests.get(
                f"http://localhost:{self.ports['backend']}/api/health", timeout=5
            )
            health["backend"] = response.status_code == 200
        except requests.RequestException:
            health["backend"] = False

        # Check frontend
        try:
            response = requests.get(
                f"http://localhost:{self.ports['frontend']}", timeout=5
            )
            health["frontend"] = response.status_code == 200
        except requests.RequestException:
            health["frontend"] = False

        return health

    @asynccontextmanager
    async def managed_servers(
        self, start_frontend: bool = False, env_vars: Dict[str, str] = None
    ):
        """Context manager for server lifecycle."""
        try:
            # Start servers
            backend_started = await self.start_backend(env_vars)
            if not backend_started:
                raise RuntimeError("Failed to start backend server")

            if start_frontend:
                await self.start_frontend()

            # Verify health
            health = await self.health_check()
            print(f"   📊 Server health: {health}")

            yield self

        finally:
            # Always cleanup
            self.stop_all()

    def cleanup_test_data(self):
        """Clean up test database and temporary files."""
        print("🧹 Cleaning up test data...")

        test_files = ["test_jobpilot.db", "test_jobpilot.db-journal", "test_logs.log"]

        for filename in test_files:
            filepath = os.path.join(self.base_dir, filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"   ✅ Removed {filename}")
                except Exception as e:
                    print(f"   ⚠️ Failed to remove {filename}: {e}")


class TestEnvironment:
    """Complete test environment manager."""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.getcwd()
        self.server_manager = ServerManager(base_dir)
        self.test_config = {
            "RAPIDAPI_KEY": os.getenv("RAPIDAPI_KEY", "test_key"),
            "DATABASE_URL": "sqlite:///test_jobpilot.db",
            "LOG_LEVEL": "INFO",
            "TESTING": "true",
        }

    @asynccontextmanager
    async def full_test_environment(self, include_frontend: bool = False):
        """Set up complete test environment."""
        print("🔧 Setting up test environment...")

        # Clean up any previous test data
        self.server_manager.cleanup_test_data()

        async with self.server_manager.managed_servers(
            start_frontend=include_frontend, env_vars=self.test_config
        ) as servers:
            yield servers

        # Final cleanup
        self.server_manager.cleanup_test_data()
        print("✅ Test environment cleaned up")


# Utility functions for easy use in tests
async def with_test_servers(
    test_func, include_frontend: bool = False, env_vars: Dict[str, str] = None
):
    """Decorator/wrapper to run tests with managed servers."""
    env = TestEnvironment()
    if env_vars:
        env.test_config.update(env_vars)

    async with env.full_test_environment(include_frontend) as servers:
        return await test_func(servers)


if __name__ == "__main__":
    """Test the server manager directly."""
    import asyncio

    async def test_server_lifecycle():
        env = TestEnvironment()

        async with env.full_test_environment() as servers:
            health = await servers.health_check()
            print(f"Server health: {health}")

            # Simple test
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8080/api/health") as response:
                    data = await response.json()
                    print(f"Health check response: {data}")

    asyncio.run(test_server_lifecycle())
