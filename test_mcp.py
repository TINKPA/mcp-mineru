#!/usr/bin/env python3
"""Simple test script for MCP-MinerU server"""

import asyncio
import json
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent / "MinerU"))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_mineru.server import app, _list_backends, _parse_pdf


async def test_list_backends():
    """Test the list_backends tool"""
    print("🧪 Testing list_backends tool...\n")

    try:
        result = await _list_backends()
        print("✅ Success!\n")
        print("=" * 60)
        print(result[0].text)
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_parse_pdf():
    """Test the parse_pdf tool"""
    print("\n🧪 Testing parse_pdf tool...\n")

    # Use the test PDF from earlier
    test_pdf = "/Volumes/Samsung Portable SSD T5/danieltangX/Downloads/label_pdf_11-3-2025.pdf"

    if not Path(test_pdf).exists():
        print(f"⚠️  Test PDF not found: {test_pdf}")
        print("Skipping parse_pdf test")
        return False

    try:
        print(f"📄 Parsing: {test_pdf}")
        print("⏳ This may take 30-40 seconds...")

        result = await _parse_pdf({
            "file_path": test_pdf,
            "backend": "pipeline",
            "formula_enable": True,
            "table_enable": True,
            "start_page": 0,
            "end_page": 0,  # Only first page
        })

        print("\n✅ Success!\n")
        print("=" * 60)
        print(result[0].text[:500] + "...")  # First 500 chars
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("🚀 MCP-MinerU Test Suite\n")

    # Test 1: list_backends
    test1_passed = await test_list_backends()

    # Test 2: parse_pdf
    test2_passed = await test_parse_pdf()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"  list_backends: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  parse_pdf:     {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
