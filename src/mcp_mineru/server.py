#!/usr/bin/env python3
"""
MCP-MinerU Server
A Model Context Protocol server for PDF parsing using MinerU
"""

import asyncio
import os
import sys
import tempfile
import unicodedata
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


def resolve_file_path(file_path: str) -> str | None:
    """
    Resolve file path with Unicode normalization to handle macOS screenshot filenames.

    macOS Sonoma screenshots contain U+202F (NARROW NO-BREAK SPACE) before AM/PM,
    which causes file-not-found errors when users copy/paste paths with regular spaces.

    This function replicates Claude Code's Read tool behavior:
    1. Try exact path match
    2. Try NFKC normalization (converts U+202F → regular space)
    3. Try directory listing + normalized filename comparison

    Args:
        file_path: The file path to resolve (may contain Unicode characters)

    Returns:
        Resolved absolute path if file exists, None otherwise
    """
    # Try exact path first
    if os.path.exists(file_path):
        return file_path

    # Try NFKC normalization (converts U+202F to regular space automatically)
    # This is the key technique that makes Claude Code's Read tool work
    normalized_path = unicodedata.normalize('NFKC', file_path)
    if normalized_path != file_path and os.path.exists(normalized_path):
        logger.info(f"Resolved file using NFKC normalization: {repr(normalized_path)}")
        return normalized_path

    # If absolute path failed, try directory listing + fuzzy match
    # This handles cases where normalization alone isn't enough
    if os.path.isabs(file_path):
        dir_part = os.path.dirname(file_path)
        file_part = os.path.basename(file_path)

        if os.path.isdir(dir_part):
            try:
                # List all files in directory
                for actual_filename in os.listdir(dir_part):
                    # Compare using NFKC normalization
                    normalized_actual = unicodedata.normalize('NFKC', actual_filename)
                    normalized_requested = unicodedata.normalize('NFKC', file_part)

                    if normalized_actual == normalized_requested:
                        resolved = os.path.join(dir_part, actual_filename)
                        logger.info(f"Resolved file using directory listing: {repr(resolved)}")
                        return resolved
            except OSError as e:
                logger.warning(f"Error listing directory {dir_part}: {e}")

    # File not found after all attempts
    return None


async def _parse_pdf(args: dict) -> list[TextContent]:
    """Parse a PDF file"""
    file_path = urllib.parse.unquote(args["file_path"])
    backend = args.get("backend", "pipeline")
    formula_enable = args.get("formula_enable", True)
    table_enable = args.get("table_enable", True)
    start_page = args.get("start_page", 0)
    end_page = args.get("end_page", -1)

    # Resolve file path with Unicode normalization
    resolved_path = resolve_file_path(file_path)

    if not resolved_path:
        # Build helpful error message
        error_msg = f"❌ Error: File not found: {file_path}"

        # Check for Unicode characters
        if any(ord(c) > 127 for c in file_path):
            error_msg += f"\n\n💡 This path contains Unicode characters: {repr(file_path)}"

        # Try to suggest similar files
        if os.path.isabs(file_path):
            dir_part = os.path.dirname(file_path)
            if os.path.isdir(dir_part):
                file_part = os.path.basename(file_path)
                base_name = file_part.rsplit('.', 1)[0] if '.' in file_part else file_part

                try:
                    # Look for files with similar names
                    similar_files = [
                        f for f in os.listdir(dir_part)
                        if base_name[:15] in f and os.path.isfile(os.path.join(dir_part, f))
                    ]

                    if similar_files:
                        error_msg += f"\n\n💡 Similar files found in directory:\n"
                        for f in similar_files[:5]:  # Show max 5
                            error_msg += f"   - {f}\n"
                except OSError:
                    pass

        return [TextContent(type="text", text=error_msg)]

    # Use the resolved path for all subsequent operations
    file_path = resolved_path

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
                parse_method="ocr",
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


async def async_main():
    """Run the MCP server (async)"""
    logger.info("Starting MCP-MinerU server...")
    logger.info(f"MinerU version: {mineru_version}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point for the MCP server (sync wrapper)"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
