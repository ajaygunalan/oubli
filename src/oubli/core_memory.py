"""Core memory file operations for Oubli.

Core memory is a ~2K token markdown file that contains the most important
information about the user, always loaded at session start.
"""

from pathlib import Path
from typing import Optional

from .storage import DEFAULT_DATA_DIR


CORE_MEMORY_FILENAME = "core_memory.md"


def get_core_memory_path(data_dir: Optional[Path] = None) -> Path:
    """Get the path to the core memory file."""
    data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    return data_dir / CORE_MEMORY_FILENAME


def load_core_memory(data_dir: Optional[Path] = None) -> str:
    """Load core memory content from file.

    Returns:
        The core memory content, or empty string if file doesn't exist.
    """
    path = get_core_memory_path(data_dir)
    if not path.exists():
        return ""
    return path.read_text()


def save_core_memory(content: str, data_dir: Optional[Path] = None) -> None:
    """Save core memory content to file.

    Args:
        content: The markdown content to save.
        data_dir: Optional custom data directory.
    """
    data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)

    path = get_core_memory_path(data_dir)
    path.write_text(content)


def core_memory_exists(data_dir: Optional[Path] = None) -> bool:
    """Check if core memory file exists."""
    return get_core_memory_path(data_dir).exists()
