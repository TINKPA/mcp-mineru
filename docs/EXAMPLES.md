# Usage Examples

## Basic Usage

### Parse a PDF Document

```python
# Claude will automatically call parse_pdf tool
User: "Analyze this research paper: /path/to/paper.pdf"

# Result: Extracted text, tables, formulas in Markdown format
```

### Parse a Screenshot

```python
User: "Extract text from this screenshot: /path/to/screenshot.png"

# MCP-MinerU will OCR the image and return structured content
```

### Parse a Photo

```python
User: "Read the receipt in this photo: /path/to/receipt.jpg"

# Returns text extracted from the photo
```

## Advanced Usage

### Extract Specific PDF Pages

```python
User: "Extract pages 10-15 from document.pdf"

# Claude calls parse_pdf with start_page=9, end_page=14
# (page numbers are 0-indexed)
```

### Check System Capabilities

```python
User: "What's the best backend for my system?"

# Claude calls list_backends tool
# Returns system info and backend recommendations
```

### Choose a Specific Backend

```python
User: "Parse this PDF using the MLX backend for faster processing"

# Claude can specify backend parameter:
# backend="vlm-mlx-engine" (Apple Silicon)
# backend="pipeline" (CPU, fastest)
# backend="vlm-transformers" (highest quality, slowest)
```

## Tool Parameters

### parse_pdf

- `file_path` (required): Path to PDF or image file
- `backend` (optional): `pipeline` | `vlm-mlx-engine` | `vlm-transformers`
- `formula_enable` (optional): Enable formula recognition (default: true)
- `table_enable` (optional): Enable table recognition (default: true)
- `start_page` (optional): Starting page for PDFs (default: 0)
- `end_page` (optional): Ending page for PDFs (default: -1 for all)

### list_backends

No parameters required. Returns system information and backend recommendations.

## Supported File Formats

- **PDF documents** (.pdf)
- **JPEG images** (.jpg, .jpeg)
- **PNG images** (.png)
- **Other formats**: WebP, GIF, and most image formats supported by PIL

## Performance Benchmarks

On Apple Silicon M4 (16GB RAM):

| Backend | Speed (per page) | Quality | Best For |
|---------|-----------------|---------|----------|
| pipeline | ~32 seconds | Good | Most use cases |
| vlm-mlx-engine | ~38 seconds | Excellent | Apple Silicon with MLX |
| vlm-transformers | ~148 seconds | Excellent | High-quality extraction |

## Common Use Cases

1. **Research paper analysis**: Extract text, tables, and formulas from academic papers
2. **Receipt scanning**: OCR receipts and invoices from photos
3. **Screenshot text extraction**: Get text from UI screenshots
4. **Document digitization**: Convert scanned documents to searchable text
5. **Form processing**: Extract structured data from forms and applications
