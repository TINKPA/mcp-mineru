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
- Python 3.10+
- uv (recommended) or pip

### Step 1: Clone the repository
```bash
git clone <your-repo-url> mcp-mineru
cd mcp-mineru
```

### Step 2: Initialize submodules
```bash
git submodule update --init --recursive
```

### Step 3: Install MinerU dependencies
```bash
# Install MinerU in the submodule
cd MinerU
pip install -e .
cd ..
```

### Step 4: Install MCP server
```bash
pip install -e .
```

## 🔧 Configuration

### Claude Desktop

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

### Using uv (recommended)

```json
{
  "mcpServers": {
    "mineru": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-mineru",
        "run",
        "mcp-mineru"
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

## 🚀 Performance

On Apple Silicon (M4):
- **pipeline backend**: ~32 seconds/page
- **vlm-mlx-engine backend**: ~38 seconds/page (higher quality)
- **vlm-transformers backend**: ~148 seconds/page

*Benchmarked on a Mac mini M4 with 16GB RAM*

## 📝 License

This project uses MinerU as a submodule, which is licensed under the Apache License 2.0.

## 🙏 Acknowledgments

- [MinerU](https://github.com/opendatalab/MinerU) - The powerful PDF parsing engine
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol specification
