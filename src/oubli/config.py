"""Configuration and data directory resolution for Oubli.

Data is stored in .oubli/ under the current working directory (per-project).
OUBLI_DATA_DIR env var overrides this if set.
Configuration files (.mcp.json, .claude/) are installed locally per project.
"""

import os
from pathlib import Path


# Directory names
OUBLI_DIR_NAME = ".oubli"
CLAUDE_DIR_NAME = ".claude"
MCP_CONFIG_NAME = ".mcp.json"


def get_data_dir() -> Path:
    """Get the data directory.

    Returns OUBLI_DATA_DIR if set, otherwise .oubli/ in the current working directory.
    """
    env_dir = os.environ.get("OUBLI_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.cwd() / OUBLI_DIR_NAME


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
