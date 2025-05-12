"""
Repository root finder utility.

This module provides functionality to reliably find the root directory of the project
regardless of where the code is being executed from.
"""

import os
import sys
import subprocess
from pathlib import Path
import inspect


def get_repo_root():
    """
    Get the root directory of the repository.
    
    Returns:
        str: Path to the repository root, or None if it cannot be determined.
        
    This function uses multiple strategies to find the repository root:
    1. Try using git to get the repo root 
    2. Look for the 'audt-data' directory in the path
    3. Search up the directory tree for common project files
    """
    # Strategy 1: Try using git command
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        repo_root = result.stdout.strip()
        if os.path.isdir(repo_root):
            return repo_root
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git command failed or git is not installed
        pass
    
    # Strategy 2: Look for 'audt-data' in path
    # Get the calling file's path
    caller_frame = inspect.stack()[1]
    caller_path = Path(caller_frame.filename).resolve()
    
    # Check if 'audt-data' is in the path
    parts = caller_path.parts
    if 'audt-data' in parts:
        idx = parts.index('audt-data')
        repo_root = str(Path(*parts[:idx+1]))
        return repo_root
    
    # Strategy 3: Search up directory tree for common project files
    current_dir = caller_path.parent
    max_levels = 10  # Limit how far up we'll go
    
    for _ in range(max_levels):
        # Check for common project files/directories
        if (current_dir / "pyproject.toml").exists() or \
           (current_dir / "setup.py").exists() or \
           (current_dir / ".git").is_dir() or \
           (current_dir / "d01_data").is_dir():
            return str(current_dir)
        
        # Move up one directory
        parent_dir = current_dir.parent
        if parent_dir == current_dir:  # Reached root
            break
        current_dir = parent_dir
    
    # All strategies failed
    print("Warning: Could not determine repository root.")
    return None


if __name__ == "__main__":
    # When run directly, print the repo root
    root = get_repo_root()
    if root:
        print(f"Repository root: {root}")
    else:
        print("Failed to find repository root")
        sys.exit(1)
