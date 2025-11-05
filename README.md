# MCP-MinerU

[![PyPI version](https://badge.fury.io/py/mcp-mineru.svg)](https://pypi.org/project/mcp-mineru/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

MCP server for document and image parsing via [MinerU](https://github.com/opendatalab/MinerU). Extract text, tables, and formulas from PDFs, screenshots, and scanned documents with MLX acceleration on Apple Silicon.

## Installation

```bash
claude mcp add --transport stdio --scope user mineru -- \
  uvx --from mcp-mineru python -m mcp_mineru.server
```

This command installs and configures the server for all your Claude Code projects using `uvx` (no manual installation required).

**Alternative methods**: See [Installation Guide](docs/INSTALLATION.md) for PyPI, source installation, and Claude Desktop configuration.

## Features

- **Multiple format support**: PDF, JPEG, PNG, and other image formats
- **OCR capabilities**: Built-in text extraction from screenshots and photos
- **Table recognition**: Preserves structure when extracting tables
- **Formula extraction**: Converts mathematical equations to LaTeX
- **MLX acceleration**: Optimized for Apple Silicon (M1/M2/M3/M4)
- **Multiple backends**: Choose speed vs quality tradeoffs

## Quick Start

### Parse a PDF document
```
User: "Analyze the tables in research_paper.pdf"
Claude: [Calls parse_pdf tool] "The paper contains 3 tables..."
```

### Extract text from a screenshot
```
User: "What does this screenshot say? image.png"
Claude: [Calls parse_pdf tool] "The screenshot contains..."
```

### Check system capabilities
```
User: "Which backend should I use?"
Claude: [Calls list_backends tool] "Your system has Apple Silicon M4..."
```

For more examples, see [Usage Examples](docs/EXAMPLES.md).

## Tools

### parse_pdf

Parse PDF and image files to extract structured content as Markdown.

**Parameters:**
- `file_path` (required): Absolute path to file (PDF, JPEG, PNG, etc.)
- `backend` (optional): `pipeline` | `vlm-mlx-engine` | `vlm-transformers`
- `formula_enable` (optional): Enable formula recognition (default: true)
- `table_enable` (optional): Enable table recognition (default: true)
- `start_page` (optional): Starting page for PDFs (default: 0)
- `end_page` (optional): Ending page for PDFs (default: -1)

### list_backends

Check system capabilities and get backend recommendations.

**Returns:** System information, available backends, and performance recommendations.

## Supported Formats

- PDF documents (.pdf)
- JPEG images (.jpg, .jpeg)
- PNG images (.png)
- Other image formats (WebP, GIF, etc.)

## Performance

Benchmarked on Apple Silicon M4 (16GB RAM):

- **pipeline**: ~32s/page, CPU-only, good quality
- **vlm-mlx-engine**: ~38s/page, Apple Silicon optimized, excellent quality
- **vlm-transformers**: ~148s/page, highest quality, slowest

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed installation options
- [Updating Guide](docs/UPDATING.md) - How to update to the latest version
- [Usage Examples](docs/EXAMPLES.md) - More use cases and API reference
- [MinerU Documentation](https://github.com/opendatalab/MinerU) - Underlying parsing engine

## Development

```bash
git clone https://github.com/TINKPA/mcp-mineru.git
cd mcp-mineru
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built on top of [MinerU](https://github.com/opendatalab/MinerU) by OpenDataLab.
