"""Configuration and data directory resolution for Oubli.

Data is always stored globally in ~/.oubli/ to share memories across projects.
Configuration files (.mcp.json, .claude/) are installed locally per project.
"""

from pathlib import Path


# Directory names
OUBLI_DIR_NAME = ".oubli"
CLAUDE_DIR_NAME = ".claude"
MCP_CONFIG_NAME = ".mcp.json"


def get_data_dir() -> Path:
    """Get the data directory (~/.oubli/).

    Data is always stored globally to share memories across all projects.
    """
    return Path.home() / OUBLI_DIR_NAME


def get_claude_dir(project_dir: Path | None = None) -> Path:
    """Get the Claude configuration directory (.claude/ in project).

    Args:
        project_dir: Project directory. Defaults to cwd.

    Returns:
        Path to .claude/ directory.
    """
    project_dir = Path(project_dir) if project_dir else Path.cwd()
    return project_dir / CLAUDE_DIR_NAME


def get_mcp_config_path(project_dir: Path | None = None) -> Path:
    """Get the path to .mcp.json for local MCP server registration.

    Args:
        project_dir: Project directory. Defaults to cwd.

    Returns:
        Path to .mcp.json file.
    """
    project_dir = Path(project_dir) if project_dir else Path.cwd()
    return project_dir / MCP_CONFIG_NAME


# Legacy aliases for backwards compatibility during transition
def resolve_data_dir(prefer_local: bool = True) -> Path:
    """Legacy function - always returns global data dir now."""
    return get_data_dir()


def get_global_data_dir() -> Path:
    """Legacy alias for get_data_dir()."""
    return get_data_dir()


def get_local_data_dir(project_dir: Path | None = None) -> Path:
    """Legacy function - returns global data dir (local data dirs no longer used)."""
    return get_data_dir()


def is_local_installation(data_dir: Path | None = None) -> bool:
    """Legacy function - always returns False (no local installations anymore)."""
    return False
