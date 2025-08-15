# Dual Stdout Handling in Development Mode

## Overview

When running JobPilot-OpenManus in development mode (`python web_server.py --dev`), we have two separate processes:

1. **Backend FastAPI Server** (Python) - Port 8080
2. **Frontend Vite Dev Server** (Node.js) - Port 3000

Each has its own stdout/stderr streams, but we want all output in a single terminal for the best development experience.

## How It Works

### 1. **Stream Separation**

```python
self.process = subprocess.Popen(
    ["npm", "run", "dev"],
    stdout=subprocess.PIPE,    # Capture frontend stdout
    stderr=subprocess.PIPE,    # Capture frontend stderr (separate)
    text=True,
    bufsize=1,
    universal_newlines=True
)
```

### 2. **Cross-Platform Stream Reading**

#### **Windows (Threading Approach)**

Since Windows doesn't support `select()` on pipes, we use separate threads:

```python
def stream_output(stream, prefix, is_error=False):
    for line in iter(stream.readline, ''):
        if line.strip():
            # Filter verbose output + add emoji prefixes
            if is_error:
                logger.error(f"🔴 {prefix}: {line}")
            else:
                if 'ready' in line.lower():
                    logger.info(f"✅ {prefix}: {line}")
                elif 'error' in line.lower():
                    logger.error(f"🔴 {prefix}: {line}")
                else:
                    logger.info(f"🌐 {prefix}: {line}")

# Two threads: one for stdout, one for stderr
stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, "Frontend", False))
stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, "Frontend", True))
```

#### **Unix/Linux (Select Approach)**

On Unix systems, we can use `select()` for better performance:

```python
while True:
    reads = [process.stdout.fileno(), process.stderr.fileno()]
    ret = select.select(reads, [], [])

    for fd in ret[0]:
        if fd == process.stdout.fileno():
            line = process.stdout.readline().strip()
            logger.info(f"🌐 Frontend: {line}")
        elif fd == process.stderr.fileno():
            line = process.stderr.readline().strip()
            logger.error(f"🔴 Frontend: {line}")
```

### 3. **Log Formatting & Prefixes**

All output is formatted with clear prefixes using emojis:

| Stream Source | Prefix | Example |
|---------------|--------|---------|
| Backend Info | `🔌 Backend:` | `🔌 Backend: Starting server...` |
| Frontend Info | `🌐 Frontend:` | `🌐 Frontend: Building for development...` |
| Frontend Ready | `✅ Frontend:` | `✅ Frontend: Local server ready at http://localhost:3000` |
| Frontend Error | `🔴 Frontend:` | `🔴 Frontend: Failed to compile` |
| Frontend Warning | `⚠️ Frontend:` | `⚠️ Frontend: Deprecated API usage` |

### 4. **Custom Log Formatter**

In development mode, we add a custom log formatter that automatically prefixes backend messages:

```python
class DevModeFormatter(logging.Formatter):
    def format(self, record):
        if not any(prefix in record.getMessage() for prefix in ['Frontend:', '🌐 Frontend:', ...]):
            record.msg = f"🔌 Backend: {record.msg}"
        return super().format(record)
```

### 5. **Noise Filtering**

We filter out verbose Vite output to keep logs clean:

```python
# Skip these common but not useful messages
if any(skip in line.lower() for skip in ['[hmr]', 'page reload', '➜']):
    continue
```

## Visual Example

When you run `python web_server.py --dev`, you'll see output like:

```
14:23:15 - 🔥 Backend: Starting in DEVELOPMENT mode
14:23:15 - 🔌 Backend: Frontend dependencies not installed. Installing...
14:23:20 - 🔌 Backend: Frontend dependencies installed successfully
14:23:20 - 🎯 Backend: Starting frontend development server...
14:23:21 - 🌐 Frontend: VITE v6.0.5 ready in 432 ms
14:23:21 - ✅ Frontend: Local:   http://localhost:3000/
14:23:21 - 🌐 Frontend: Network: use --host to expose
14:23:21 - ✅ Backend: Frontend dev server should be starting at http://localhost:3000
14:23:21 - 🔌 Backend: Starting JobPilot-OpenManus Web Server on localhost:8080...
14:23:22 - 🔌 Backend: Started server process [12345]
14:23:22 - 🔌 Backend: Waiting for application startup.
14:23:22 - 🔌 Backend: Application startup complete.
14:23:22 - 🔌 Backend: Uvicorn running on http://localhost:8080 (Press CTRL+C to quit)
```

## Benefits

1. **Single Terminal** - All output in one place
2. **Clear Identification** - Easy to tell frontend vs backend messages
3. **Error Separation** - Frontend errors clearly marked with 🔴
4. **Noise Reduction** - Verbose messages filtered out
5. **Cross-Platform** - Works on Windows, macOS, and Linux
6. **Proper Cleanup** - Both servers shut down cleanly with Ctrl+C

## Technical Challenges Solved

- **Blocking I/O** - Using threads/select to avoid blocking
- **Platform Differences** - Different approaches for Windows vs Unix
- **Stream Buffering** - Using `bufsize=1` and `universal_newlines=True`
- **Process Management** - Proper cleanup and termination
- **Log Interleaving** - Maintaining chronological order of mixed logs

This approach gives developers a seamless experience where they can see both frontend and backend activity in real-time, with clear visual distinction between the two systems.
