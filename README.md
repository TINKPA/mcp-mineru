# 🚀 MCP-MinerU

A Model Context Protocol (MCP) server that brings powerful PDF parsing capabilities to Claude using [MinerU](https://github.com/opendatalab/MinerU).

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
- uv (recommended) or pip

### Quick Install

```bash
# Clone the repository
git clone https://github.com/TINKPA/mcp-mineru.git
cd mcp-mineru

# Install with all dependencies (one command!)
pip install -e .
```

That's it! The `mineru[core]` dependency will automatically install all backends (pipeline, vlm, mlx).

## 🔧 Configuration

### Claude Code (Recommended)

Use the Claude Code CLI to add the server directly:

```bash
# Replace /absolute/path/to/mcp-mineru with your actual path
# Using --scope user makes it available across all your projects
claude mcp add --transport stdio --scope user mineru -- \
  python /absolute/path/to/mcp-mineru/src/mcp_mineru/server.py
```

Or using uv:

```bash
claude mcp add --transport stdio --scope user mineru -- \
  uv --directory /absolute/path/to/mcp-mineru run python src/mcp_mineru/server.py
```

**Configuration Scope Options**:
- `--scope user` (recommended): Available across all your projects
- `--scope local`: Available only in the current project (default)
- `--scope project`: Shared with everyone via `.mcp.json` file

**Note**: The `--` (double dash) separates Claude's CLI flags from the command that runs the MCP server. Everything after `--` is the actual command to execute.

### Claude Desktop (Manual Configuration)

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

Or using uv (recommended):

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