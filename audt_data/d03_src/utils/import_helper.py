"""
Helper module to fix import issues in the project.
Import this at the top of any script to ensure imports work correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

def fix_imports():
    """Add project root to Python path to ensure imports work"""
    try:
        # Try to get git root first
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            project_root = result.stdout.strip()
        else:
            # Fallback: navigate up from the caller's file
            import inspect
            caller_frame = inspect.stack()[1]
            caller_file = Path(caller_frame.filename).resolve()
            # Find the audt-data directory
            parts = caller_file.parts
            if 'audt-data' in parts:
                idx = parts.index('audt-data')
                project_root = str(Path(*parts[:idx+1]))
            else:
                # Last resort: go up from current file
                project_root = str(Path(__file__).resolve().parent.parent.parent)
        
        # Add to path if not already there
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            return project_root
        return None
    except Exception as e:
        print(f"Warning: Failed to set up Python path: {e}")
        return None

# Automatically fix imports when this module is imported
project_root = fix_imports()
if project_root:
    print(f"Added {project_root} to Python path")
