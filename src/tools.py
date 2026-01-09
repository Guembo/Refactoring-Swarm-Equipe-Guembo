"""
Toolsmith Module
Provides utility functions for file operations, linting, and testing.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

# Security: Define the allowed base directory for file operations
SANDBOX_DIR = (Path(__file__).parent.parent /
               "sandbox").resolve()  # Project root


def _validate_path(file_path: str) -> Path:
    """
    Validates that the file path is within the sandbox directory.
    
    Args:
        file_path (str): The file path to validate.
    
    Returns:
        Path: Resolved absolute path.
    
    Raises:
        ValueError: If the path is outside the sandbox directory.
    """
    try:
        # Convert to absolute path and resolve any symlinks/relative components
        abs_path = Path(file_path).resolve()
        
        # Check if the path is within the sandbox
        abs_path.relative_to(SANDBOX_DIR)
        
        return abs_path
    except (ValueError, RuntimeError) as e:
        raise ValueError(
            f"❌ Security Error: Path '{file_path}' is outside the allowed sandbox directory '{SANDBOX_DIR}'"
        ) from e


