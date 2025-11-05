# Installation Guide

## Prerequisites

- Python 3.10-3.13
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation Methods

### Option 1: From PyPI (Recommended)

```bash
# Using uv (faster)
uv pip install mcp-mineru

# Or using pip
pip install mcp-mineru
```

### Option 2: From Source

```bash
git clone https://github.com/TINKPA/mcp-mineru.git
cd mcp-mineru
uv pip install -e .  # or: pip install -e .
```

## Configuration

### Claude Code (One-Command Setup)

**For all projects (global)**:
```bash
claude mcp add --transport stdio --scope user mineru -- \
  uvx --from mcp-mineru python -m mcp_mineru.server
```

**For current project only**:
```bash
claude mcp add --transport stdio mineru -- \
  uvx --from mcp-mineru python -m mcp_mineru.server
```

This uses `uvx` to automatically install and run mcp-mineru in an isolated environment.

### Claude Desktop (Manual Configuration)

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**If installed from PyPI**:
```json
{
  "mcpServers": {
    "mineru": {
      "command": "python",
      "args": ["-m", "mcp_mineru.server"]
    }
  }
}
```

**If installed from source**:
```json
{
  "mcpServers": {
    "mineru": {
      "command": "python",
      "args": [
        "/absolute/path/to/mcp-mineru/src/mcp_mineru/server.py"
      ]
    }
  }
}
```

Or using uv:
```json
{
  "mcpServers": {
    "mineru": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-mineru",
        "run",
        "python",
        "src/mcp_mineru/server.py"
      ]
    }
  }
}
```

## What Gets Installed

The `mineru[core]` dependency automatically installs all backends including:

- **PyTorch** for deep learning models
- **Computer Vision** libraries (OpenCV, ultralytics)
- **OCR engines** (PaddleOCR, RapidOCR)
- **MLX** for Apple Silicon acceleration
- **Web interfaces** (Gradio, FastAPI)

Total: ~163 packages, ~2GB disk space
