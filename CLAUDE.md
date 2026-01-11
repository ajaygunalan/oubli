# CLAUDE.md

## Project: Oubli - Fractal Memory System for Claude Code

A Claude Code plugin that provides persistent, hierarchical memory with fractal synthesis.

## Working Style Preferences

- **Rapid prototyping** - Get working features fast, avoid over-engineering upfront
- **Phase-based development** - Complete one phase, hand back control for testing/commits, then proceed
- **LLM-driven from the start** - All intelligent operations (parsing, synthesis, core memory generation) run inside Claude Code
- **Test early, test often** - Each phase should have manual test steps before moving on
- **Use uv for virtual environments** - Virtual env at `.venv/`

## Architecture Decisions

- **LanceDB from the start** - Embedded vector database, avoids JSON→LanceDB migration pain later
- **MCP tools are simple CRUD** - Claude Code does the intelligent work (parsing, clustering, summarizing)
- **No slash commands needed** - Users just talk naturally ("Save a memory about...")
- **Core Memory is a markdown file** - `~/.oubli/core_memory.md`, human-readable and editable
- **Everything runs locally** - No external services, no API keys needed

## Key Files

- `src/oubli/storage.py` - LanceDB-backed MemoryStore with Memory dataclass
- `src/oubli/core_memory.py` - Core memory file operations
- `src/oubli/mcp_server.py` - MCP tools for Claude Code integration
- `SPEC.md` - Full specification document (source of truth for features)

## MCP Server

Installed via: `claude mcp add oubli -- .venv/bin/python -m oubli.mcp_server`

Tools implemented:
- `memory_save` - Save a new memory
- `memory_search` - Search by keyword
- `memory_get` - Get full memory details
- `memory_list` - List all memories
- `memory_stats` - Get statistics
- `memory_update` - Update a memory
- `core_memory_get` - Get core memory content
- `core_memory_save` - Save core memory content

## Current Status

### Completed (Phase 1-2)
- Storage foundation with LanceDB
- Memory dataclass with all fields
- CRUD operations (add, get, search, update, delete)
- Core memory file operations
- MCP server with 8 tools
- MCP server registered with Claude Code

### Not Yet Implemented (from SPEC.md)
- `memory_import` tool - Parse text blocks into multiple memories
- `memory_synthesize` tool - Trigger clustering and synthesis
- `core_memory_update` tool - Regenerate core memory from insights
- `core_memory_edit` tool - Edit specific sections
- Session hooks (SessionStart to load core memory, Stop to auto-save)
- Embeddings for semantic search (currently keyword-only)
- CLI commands
- Synthesizer subagent
- Memory awareness skill
- Import parser for Claude.ai format

## Development Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
python -c "from oubli.storage import MemoryStore; store = MemoryStore(); print(store.get_stats())"

# Reset data
rm -rf ~/.oubli/

# Check MCP server loads
python -c "from oubli.mcp_server import mcp; print(mcp.name)"
```

## Next Phase

Phase 3: Test full flow in Claude Code
- Restart Claude Code to load MCP server
- Test: "What memories do you have?"
- Test: "Save a memory that I like Python"
- Test: "Search memories for Python"
