# Updating MCP-MinerU

## Check Your Current Version

To see which version you're currently using, check the MCP server logs or use:

```bash
uvx --from mcp-mineru python -c "import mineru; print(mineru.__version__)"
```

## Update Methods

### If You Used uvx (Recommended Installation)

The `uvx` command caches packages. To force an update:

**Option 1: Reinstall the MCP Server**

This is the simplest and most reliable method:

```bash
# Remove the existing server
claude mcp remove --scope user mineru

# Add it again (gets the latest version)
claude mcp add --transport stdio --scope user mineru -- \
  uvx --from mcp-mineru python -m mcp_mineru.server
```

**Option 2: Clear uvx Cache**

```bash
# Run with --force flag to bypass cache
uvx --force --from mcp-mineru python -m mcp_mineru.server --help

# Or clear all uvx cache
rm -rf ~/.local/share/uv/cache
```

**Note**: uvx automatically checks for updates periodically, so you may get the new version automatically after some time.

### If You Used pip Install

```bash
# Using uv (recommended)
uv pip install --upgrade mcp-mineru

# Or using pip
pip install --upgrade mcp-mineru
```

Then restart Claude Code or your MCP client.

### If You Installed from Source

```bash
cd /path/to/mcp-mineru
git pull origin main
uv pip install -e .
```

## Verify the Update

After updating, verify you have the new version:

1. Restart Claude Code
2. Run `/mcp` to check server status
3. Use the `list_backends` tool to see the MinerU version

You should see "MinerU Version: 2.6.4" in the output.

## What's New in Each Version

### v0.1.1 (Latest)
- Added support for image parsing (JPEG, PNG, etc.)
- Updated tool descriptions for better LLM understanding
- Restructured documentation for clarity
- 114-line README (down from 240+ lines)

### v0.1.0 (Initial Release)
- Initial MCP server implementation
- PDF parsing with MinerU
- MLX acceleration support
- Three backends: pipeline, vlm-mlx-engine, vlm-transformers

## Troubleshooting

### MCP Server Won't Update

If you're still seeing the old version after updating:

1. **Restart Claude Code completely** (not just reload)
2. **Check which installation method you used**:
   ```bash
   claude mcp list
   ```
3. **Verify the command**: Make sure it includes `uvx --from mcp-mineru`
4. **Clear all caches**:
   ```bash
   rm -rf ~/.local/share/uv/cache
   rm -rf ~/.cache/uv
   ```

### Permission Errors

If you get permission errors during update:

```bash
# For pip installations
pip install --upgrade --user mcp-mineru

# For source installations
sudo chown -R $USER /path/to/mcp-mineru
```

## Staying Updated

To get notifications about new releases:

- **Watch the GitHub repository**: https://github.com/TINKPA/mcp-mineru
- **Check PyPI**: https://pypi.org/project/mcp-mineru/
- Subscribe to release notifications on GitHub
