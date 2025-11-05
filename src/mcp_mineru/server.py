#!/usr/bin/env python3
"""
MCP-MinerU Server
A Model Context Protocol server for PDF parsing using MinerU
"""

import asyncio
import os
import sys
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from loguru import logger

# Import MinerU modules
try:
    from mineru.cli.common import aio_do_parse, read_fn
    from mineru.version import __version__ as mineru_version
except ImportError:
    logger.error("Failed to import MinerU. Make sure the submodule is initialized.")
    mineru_version = "unknown"


# Create MCP server
app = Server("mcp-mineru")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="parse_pdf",
            description=(
                f"Parse PDF and image files (PDF, JPEG, PNG, etc.) to extract text, tables, formulas, and structure using MinerU v{mineru_version}. "
                "Supports multiple backends including MLX-accelerated inference on Apple Silicon. "
                "Works with documents, screenshots, photos, and scanned images."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to parse (supports PDF, JPEG, PNG, and other image formats)",
                    },
                    "backend": {
                        "type": "string",
                        "enum": ["pipeline", "vlm-mlx-engine", "vlm-transformers"],
                        "default": "pipeline",
                        "description": (
                            "Backend to use:\n"
                            "- pipeline: Fast, general-purpose (recommended for most cases)\n"
                            "- vlm-mlx-engine: Fastest on Apple Silicon (M1/M2/M3/M4)\n"
                            "- vlm-transformers: VLM model, slower but more accurate"
                        ),
                    },
                    "formula_enable": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable formula recognition",
                    },
                    "table_enable": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable table recognition",
                    },
                    "start_page": {
                        "type": "integer",
                        "default": 0,
                        "description": "Starting page number (0-indexed)",
                    },
                    "end_page": {
                        "type": "integer",
                        "default": -1,
                        "description": "Ending page number (-1 for all pages)",
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="list_backends",
            description="Check system capabilities and list recommended backends for document and image parsing",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    if name == "parse_pdf":
        return await _parse_pdf(arguments)
    elif name == "list_backends":
        return await _list_backends()
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _parse_pdf(args: dict) -> list[TextContent]:
    """Parse a PDF file"""
    file_path = urllib.parse.unquote(args["file_path"])
    backend = args.get("backend", "pipeline")
    formula_enable = args.get("formula_enable", True)
    table_enable = args.get("table_enable", True)
    start_page = args.get("start_page", 0)
    end_page = args.get("end_page", -1)

    # Validate file exists
    if not os.path.exists(file_path):
        return [TextContent(
            type="text",
            text=f"❌ Error: File not found: {file_path}"
        )]

    try:
        # Read PDF
        logger.info(f"Reading PDF: {file_path}")
        pdf_bytes = read_fn(file_path)
        pdf_name = Path(file_path).stem

        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Parsing with backend: {backend}")

            # Call MinerU parser
            await aio_do_parse(
                output_dir=temp_dir,
                pdf_file_names=[pdf_name],
                pdf_bytes_list=[pdf_bytes],
                p_lang_list=["ch"],
                backend=backend,
                parse_method="auto",
                formula_enable=formula_enable,
                table_enable=table_enable,
                server_url=None,
                f_draw_layout_bbox=False,
                f_draw_span_bbox=False,
                f_dump_md=True,
                f_dump_middle_json=False,
                f_dump_model_output=False,
                f_dump_orig_pdf=False,
                f_dump_content_list=False,
                start_page_id=start_page,
                end_page_id=end_page if end_page >= 0 else 99999,
            )

            # Read Markdown result
            parse_method = "vlm" if backend.startswith("vlm") else "auto"
            md_file = Path(temp_dir) / pdf_name / parse_method / f"{pdf_name}.md"

            if md_file.exists():
                markdown_content = md_file.read_text(encoding="utf-8")

                # Build response
                response = f"""# 📄 PDF Parsing Result

**File:** `{file_path}`
**Backend:** `{backend}`
**Pages:** {start_page} to {end_page if end_page >= 0 else 'end'}
**Formula Recognition:** {'✅ Enabled' if formula_enable else '❌ Disabled'}
**Table Recognition:** {'✅ Enabled' if table_enable else '❌ Disabled'}

---

{markdown_content}
"""
                return [TextContent(type="text", text=response)]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Error: Failed to generate markdown output"
                )]

    except Exception as e:
        logger.exception("Error parsing PDF")
        return [TextContent(
            type="text",
            text=f"❌ Error parsing PDF: {str(e)}"
        )]


async def _list_backends() -> list[TextContent]:
    """List available backends and system info"""
    import platform
    import subprocess

    system_info = {
        "platform": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }

    # Check for Apple Silicon
    is_apple_silicon = system_info["machine"] == "arm64" and system_info["platform"] == "Darwin"

    # Check for CUDA (simplified check)
    has_cuda = False
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=2
        )
        has_cuda = result.returncode == 0
    except:
        pass

    # Build recommendation
    recommendations = []

    if is_apple_silicon:
        recommendations.append(
            "🚀 **Recommended:** `vlm-mlx-engine` - Optimized for Apple Silicon with MLX acceleration"
        )
        recommendations.append(
            "⚡️ **Alternative:** `pipeline` - Fast and general-purpose (CPU)"
        )
    elif has_cuda:
        recommendations.append(
            "🚀 **Recommended:** `vlm-transformers` with CUDA acceleration"
        )
        recommendations.append(
            "⚡️ **Alternative:** `pipeline` - Balanced speed and quality"
        )
    else:
        recommendations.append(
            "⚡️ **Recommended:** `pipeline` - Best choice for CPU-only systems"
        )

    response = f"""# 🖥️  System Information

**Platform:** {system_info['platform']}
**Architecture:** {system_info['machine']}
**Python:** {system_info['python']}
**Apple Silicon:** {'✅ Yes' if is_apple_silicon else '❌ No'}
**CUDA Available:** {'✅ Yes' if has_cuda else '❌ No'}
**MinerU Version:** {mineru_version}

## 📊 Available Backends

### 1. pipeline
- **Speed:** Fast ⚡️
- **Quality:** Good
- **Requirements:** CPU only
- **Best for:** Most use cases

### 2. vlm-mlx-engine
- **Speed:** Very Fast 🚀 (Apple Silicon only)
- **Quality:** Excellent
- **Requirements:** Apple M1/M2/M3/M4 chips
- **Best for:** Apple Silicon with MLX acceleration

### 3. vlm-transformers
- **Speed:** Slower 🐢
- **Quality:** Excellent
- **Requirements:** CPU or CUDA
- **Best for:** High-quality extraction

## 💡 Recommendations

{chr(10).join(recommendations)}
"""

    return [TextContent(type="text", text=response)]


async def main():
    """Run the MCP server"""
    logger.info("Starting MCP-MinerU server...")
    logger.info(f"MinerU version: {mineru_version}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
