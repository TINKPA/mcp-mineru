# 🚀 MCP-MinerU

[![PyPI version](https://badge.fury.io/py/mcp-mineru.svg)](https://pypi.org/project/mcp-mineru/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

A Model Context Protocol (MCP) server that brings powerful PDF parsing capabilities to Claude using [MinerU](https://github.com/opendatalab/MinerU).

## 🚀 Quick Start

Get started in one command (requires [uv](https://docs.astral.sh/uv/)):

### Option 1: Install for All Projects (Recommended)

```bash
claude mcp add --transport stdio --scope user mineru -- \
  uvx --from mcp-mineru python -m mcp_mineru.server
```

This adds the server to your global config (`~/.claude.json`) and makes it available in all your projects.

### Option 2: Install for Current Project Only

```bash
claude mcp add --transport stdio mineru -- \
  uvx --from mcp-mineru python -m mcp_mineru.server
```

This adds the server only to your current project.

## ✨ Features

- 📄 **Parse PDF files** with high accuracy
- 🧮 **Extract formulas** and mathematical equations
- 📊 **Recognize tables** and preserve structure
- ⚡️ **MLX acceleration** on Apple Silicon (M1/M2/M3/M4)
- 🔄 **Multiple backends** for different use cases
- 🤖 **MCP integration** for seamless use with Claude

## 🎯 Tools

### `parse_pdf`
Parse PDF files and extract structured content as Markdown.

**Parameters:**
- `file_path` (required): Absolute path to the PDF file
- `backend` (optional): `pipeline` | `vlm-mlx-engine` | `vlm-transformers`
- `formula_enable` (optional): Enable formula recognition (default: true)
- `table_enable` (optional): Enable table recognition (default: true)
- `start_page` (optional): Starting page number (default: 0)
- `end_page` (optional): Ending page number (default: -1 for all pages)

### `list_backends`
Check system capabilities and get backend recommendations.

## 🛠️ Installation

### Prerequisites
- Python 3.10-3.13
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Option 1: Install from PyPI (Recommended)

```bash
# Using uv (faster, recommended)
uv pip install mcp-mineru
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/TINKPA/mcp-mineru.git
cd mcp-mineru

# Install in editable mode
uv pip install -e .  # or: pip install -e .
```

The `mineru[core]` dependency will automatically install all backends (pipeline, vlm, mlx) including:
- 🔥 **PyTorch** for deep learning models
- 🖼️ **Computer Vision** libraries (OpenCV, ultralytics)
- 📊 **OCR engines** (PaddleOCR, RapidOCR)
- ⚡️ **MLX** for Apple Silicon acceleration
- 🌐 **Web interfaces** (Gradio, FastAPI)

## 🔧 Advanced Configuration

### Traditional Setup (Manual Install)

<details>
<summary>If you prefer to install first, then configure (click to expand)</summary>

**Step 1: Install**
```bash
uv pip install mcp-mineru
# or: pip install mcp-mineru
```

**Step 2: Configure**
```bash
claude mcp add --transport stdio mineru -- \
  python -m mcp_mineru.server
```

</details>

<details>
<summary>If installed from source (click to expand)</summary>

```bash
# Replace /absolute/path/to/mcp-mineru with your actual installation path
claude mcp add --transport stdio mineru -- \
  python /absolute/path/to/mcp-mineru/src/mcp_mineru/server.py
```

Or using uv:

```bash
claude mcp add --transport stdio mineru -- \
  uv --directory /absolute/path/to/mcp-mineru run python src/mcp_mineru/server.py
```

</details>

### Claude Desktop (Manual Configuration)

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**If installed from PyPI** (simpler):

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

<details>
<summary>If installed from source (click to expand)</summary>

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

</details>

## 📖 Usage Examples

### Example 1: Parse a PDF
```
User: "Please analyze this research paper: /path/to/paper.pdf"

Claude: [Calls parse_pdf tool]
"This research paper discusses... The key findings in Table 3 show..."
```

### Example 2: Check system capabilities
```
User: "What's the best backend for my system?"

Claude: [Calls list_backends tool]
"Your system has Apple Silicon (M4). I recommend using the
'vlm-mlx-engine' backend for fastest performance."
```

### Example 3: Extract specific pages
```
User: "Extract pages 10-15 from this PDF"

Claude: [Calls parse_pdf with start_page=9, end_page=14]
"Here's the content from pages 10-15..."
```

## 🏗️ Development

### Run tests
```bash
pytest
```

### Format code
```bash
black src/
ruff check src/
```

## ❓ Troubleshooting

### ModuleNotFoundError when running tests

If you see errors like `ModuleNotFoundError: No module named 'mineru'` or `'torch'`:

**Solution**: Reinstall the package to ensure all dependencies are installed:
```bash
pip install -e .
```

The `mineru[core]` dependency should automatically install all required backends.

## 🚀 Performance

On Apple Silicon (M4):
- **pipeline backend**: ~32 seconds/page
- **vlm-mlx-engine backend**: ~38 seconds/page (higher quality)
- **vlm-transformers backend**: ~148 seconds/page

*Benchmarked on a Mac mini M4 with 16GB RAM*

## 📝 License

This project uses MinerU as a submodule, which is licensed under the Apache License 2.0.

## 🙏 Dependencies & Acknowledgments

This project is built on top of:

- **[MinerU](https://github.com/opendatalab/MinerU)** (Apache 2.0)
  - Core PDF parsing engine
  - Included as git submodule for development stability
  
- **[MCP](https://modelcontextprotocol.io/)** (MIT)
  - Model Context Protocol specification