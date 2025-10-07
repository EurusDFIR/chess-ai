# Project Cleanup Guide

## Files/Folders to DELETE (Development artifacts):

### Root Level:

- `benchmark_engines.py` - Testing only
- `demo_*.py` (all demo files) - Examples only
- `quick_test.py` - Testing only
- `test_*.py` (all test files) - Development only
- `img*.png` (screenshots) - Move to docs/images
- `CMakeLists.txt` - C++ build (optional if using Python only)
- `build/` - Build artifacts
- `.idea/` - IDE settings (keep in .gitignore)
- `README_V2.md` - Duplicate
- `COMPLETION_SUMMARY.md` - Development log

### Docs folder (keep only essentials):

**KEEP:**

- `QUICK_START.md` - User guide
- `GAME_CONTROLS_GUIDE.md` - How to play
- `ANALYSIS_MODE_GUIDE.md` - Features
- `TODO.md` - Roadmap

**DELETE (Development docs):**

- All BUILD\_\*.md files
- All IMPLEMENTATION\_\*.md files
- All FIX\_\*.md files
- All GUI\_\*.md files
- ARCHITECTURE_DIAGRAM.md
- CPP_IMPLEMENTATION_GUIDE.md
- DETAILED_ANALYSIS.md
- DEVELOPER_GUIDE.md
- FINAL_REPORT.md
- HYBRID_ARCHITECTURE.md
- OPTIMIZATION_REPORT.md
- REFACTORING_SUMMARY.md
- TEST_RESULTS.md
- VS_INSTALL_GUIDE.md

## Best Practice Distribution Structure:

```
chess-ai/
├── README.md                 # Main documentation
├── LICENSE                   # Add license
├── requirements.txt          # Python dependencies
├── setup.py                  # Installation script
├── .gitignore               # Git ignore rules
│
├── src/                     # Source code
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── ai/                  # AI engine
│   ├── game/                # Game logic
│   ├── gui/                 # GUI components
│   └── utils/               # Utilities
│
├── assets/                  # Game assets (if any)
│   ├── pieces/
│   ├── sounds/
│   └── themes/
│
├── opening_bin/             # Opening books
├── syzygy/                  # Endgame tablebases
│
├── docs/                    # User documentation only
│   ├── QUICK_START.md
│   ├── CONTROLS.md
│   ├── FEATURES.md
│   └── images/              # Screenshots
│
└── examples/                # Optional: usage examples
    └── demo_analysis.py
```

## Recommended .gitignore:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build artifacts
build/
*.pyd
*.dll

# Testing
.pytest_cache/
.coverage
htmlcov/
```

## Distribution Methods:

### 1. **GitHub Release (Recommended)**

```bash
# Tag version
git tag -a v2.1.0 -m "Release v2.1.0 - Lichess-style UI"
git push origin v2.1.0

# Create release on GitHub with:
- Source code (zip/tar.gz)
- Compiled executables (optional)
- Installation instructions
```

### 2. **PyPI Package**

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

### 3. **Executable Distribution**

```bash
# Using PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed src/gui/main_window_v2.py

# Creates standalone .exe in dist/
```

### 4. **Docker Container**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "-m", "src.gui.main_window_v2"]
```

## Installation Instructions (for users):

````markdown
# Quick Install

## Prerequisites

- Python 3.10+
- pip

## Installation

### Method 1: From Source

```bash
git clone https://github.com/Eurus-Infosec/chess-ai.git
cd chess-ai
pip install -r requirements.txt
python -m src.gui.main_window_v2
```
````

### Method 2: Using setup.py

```bash
git clone https://github.com/Eurus-Infosec/chess-ai.git
cd chess-ai
pip install .
chess-ai
```

### Method 3: Download Executable (Windows)

1. Download `ChessAI-v2.1.0-windows.exe` from [Releases]
2. Run the executable
3. No installation needed!

```

```
