# Development Environment Setup Guide

## Preventing Pre-commit Conflicts

### Issue: VSCode Environment Conflicts
VSCode might use a different Python environment than your project, causing formatting conflicts with pre-commit hooks.

### Solution: Proper Environment Setup

#### 1. Activate the correct Python environment in terminal
```bash
# For uv (recommended for this project)
.venv\Scripts\activate

# Or if using conda
conda activate your-jobpilot-env

# Or if using venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 2. Install pre-commit in the correct environment
```bash
pip install pre-commit
pre-commit install
```

#### 3. Run pre-commit manually to test
```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files api_research/tests/test_jsearch.py
```

#### 4. Configure VSCode Python Interpreter
1. Open Command Palette (`Ctrl+Shift+P`)
2. Search "Python: Select Interpreter"
3. Choose the interpreter from your project's .venv directory

### Code Formatting Standards

#### isort Configuration
- Profile: black compatibility
- Lines after imports: 1 (single blank line)
- Multi-line imports: use parentheses with line continuation

#### Black Configuration
- Line length: 88 (default)
- Version: 23.1.0 (specified in pre-commit config)

### Troubleshooting

#### If you see import sorting errors:
1. Check your Python interpreter in VSCode
2. Run `isort .` manually in terminal with correct environment
3. Commit changes after manual formatting

#### If you see trailing whitespace errors:
1. Configure your editor to show trailing whitespace
2. Set up auto-trim on save in VSCode:
   ```json
   "files.trimTrailingWhitespace": true,
   "files.insertFinalNewline": true
   ```

### Quick Fix Commands
```bash
# Fix import sorting
isort api_research/tests/test_jsearch.py
isort api_research/implementations/jsearch_client.py
isort scripts/check_db.py
isort scripts/run_mcp_server.py

# Fix formatting
black api_research/ scripts/

# Run all pre-commit checks
pre-commit run --all-files
```

## Environment Validation

Before committing, validate your environment:

```bash
# Check Python version and location
python --version
which python  # Linux/Mac
where python   # Windows

# Check if pre-commit is properly installed
pre-commit --version

# Check if tools are available
black --version
isort --version
```

This ensures consistent formatting across all contributors and prevents CI failures.
