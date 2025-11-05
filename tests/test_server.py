#!/usr/bin/env python3
"""
Comprehensive test suite for MCP-MinerU server
Tests all tools, edge cases, and error handling
"""

import asyncio
import os
import sys
import tempfile
import urllib.parse
from pathlib import Path

import pytest

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_mineru.server import _list_backends, _parse_pdf


class TestListBackends:
    """Test the list_backends tool"""

    @pytest.mark.asyncio
    async def test_list_backends_success(self):
        """Test that list_backends returns valid output"""
        result = await _list_backends()

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Backend" in result[0].text or "backend" in result[0].text
        assert "pipeline" in result[0].text

    @pytest.mark.asyncio
    async def test_list_backends_shows_mlx_on_apple_silicon(self):
        """Test that vlm-mlx-engine is shown on Apple Silicon"""
        result = await _list_backends()
        text = result[0].text

        # On Apple Silicon, should show MLX backend
        import platform
        if platform.machine() == "arm64" and platform.system() == "Darwin":
            assert "vlm-mlx-engine" in text


class TestParsePDF:
    """Test the parse_pdf tool"""

    @pytest.fixture
    def test_files_dir(self):
        """Get the test files directory"""
        return Path(__file__).parent / "fixtures"

    @pytest.mark.asyncio
    async def test_parse_pdf_file_not_found(self):
        """Test error handling when file doesn't exist"""
        result = await _parse_pdf({
            "file_path": "/nonexistent/file.pdf"
        })

        assert len(result) == 1
        assert "Error" in result[0].text or "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_parse_pdf_with_spaces_in_filename(self, tmp_path):
        """Test parsing files with spaces in the filename"""
        # Create a simple PDF-like file with spaces in name
        test_file = tmp_path / "test file with spaces.pdf"

        # Create a minimal valid PDF
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF
"""
        test_file.write_bytes(pdf_content)

        # Test with normal path
        result = await _parse_pdf({
            "file_path": str(test_file),
            "backend": "pipeline"
        })

        # Should not error on file not found
        assert "File not found" not in result[0].text

    @pytest.mark.asyncio
    async def test_parse_pdf_with_url_encoded_path(self, tmp_path):
        """Test parsing files with URL-encoded paths (spaces as %20)"""
        # Create a test file with spaces
        test_file = tmp_path / "test document.pdf"

        # Create a minimal valid PDF
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF
"""
        test_file.write_bytes(pdf_content)

        # URL encode the path (spaces become %20)
        encoded_path = urllib.parse.quote(str(test_file), safe='/')

        # Test with URL-encoded path
        result = await _parse_pdf({
            "file_path": encoded_path,
            "backend": "pipeline"
        })

        # Should successfully decode and find the file
        assert "File not found" not in result[0].text

    @pytest.mark.asyncio
    async def test_parse_pdf_with_special_characters(self, tmp_path):
        """Test parsing files with special characters in path"""
        # Create a test file with special chars (parentheses, ampersand)
        test_file = tmp_path / "test (2024) & results.pdf"

        # Create a minimal valid PDF
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF
"""
        test_file.write_bytes(pdf_content)

        # Test with special characters in path
        result = await _parse_pdf({
            "file_path": str(test_file),
            "backend": "pipeline"
        })

        # Should handle special characters correctly
        assert "File not found" not in result[0].text

    @pytest.mark.asyncio
    async def test_parse_image_jpeg(self, tmp_path):
        """Test parsing JPEG images"""
        # Create a minimal JPEG (1x1 pixel red)
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
            0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 0x00, 0x48,
            0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
            0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C,
            0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D,
            0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20,
            0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27,
            0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34,
            0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4,
            0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x03, 0xFF, 0xC4, 0x00, 0x14,
            0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
            0x00, 0x00, 0x3F, 0x00, 0x37, 0xFF, 0xD9
        ])

        test_file = tmp_path / "test.jpeg"
        test_file.write_bytes(jpeg_data)

        # Test parsing JPEG
        result = await _parse_pdf({
            "file_path": str(test_file),
            "backend": "pipeline"
        })

        # Should process the image (MinerU converts to PDF internally)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_parse_pdf_with_different_backends(self, tmp_path):
        """Test parsing with different backends"""
        # Create a minimal PDF
        test_file = tmp_path / "test.pdf"
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF
"""
        test_file.write_bytes(pdf_content)

        backends = ["pipeline"]

        # Add MLX backend if on Apple Silicon
        import platform
        if platform.machine() == "arm64" and platform.system() == "Darwin":
            backends.append("vlm-mlx-engine")

        for backend in backends:
            result = await _parse_pdf({
                "file_path": str(test_file),
                "backend": backend
            })

            assert len(result) > 0
            assert "File not found" not in result[0].text

    @pytest.mark.asyncio
    async def test_parse_pdf_page_range(self, tmp_path):
        """Test parsing specific page ranges"""
        # Create a minimal PDF
        test_file = tmp_path / "test.pdf"
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF
"""
        test_file.write_bytes(pdf_content)

        # Test with page range
        result = await _parse_pdf({
            "file_path": str(test_file),
            "backend": "pipeline",
            "start_page": 0,
            "end_page": 0
        })

        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_parse_pdf_formula_and_table_flags(self, tmp_path):
        """Test formula and table recognition flags"""
        # Create a minimal PDF
        test_file = tmp_path / "test.pdf"
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF
"""
        test_file.write_bytes(pdf_content)

        # Test with formula and table flags
        result = await _parse_pdf({
            "file_path": str(test_file),
            "backend": "pipeline",
            "formula_enable": True,
            "table_enable": True
        })

        assert len(result) > 0
        # Check that flags are mentioned in output
        assert "Formula Recognition" in result[0].text or "formula" in result[0].text.lower()
        assert "Table Recognition" in result[0].text or "table" in result[0].text.lower()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
