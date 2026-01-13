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
    except ValueError as e:
        raise ValueError(
            f"❌ Security Error: Path '{file_path}' is outside the allowed sandbox directory '{SANDBOX_DIR}'"
        ) from e


def read_file(file_path: str) -> str:
    """
    Safely reads text from a file within the sandbox.
    
    Args:
        file_path (str): Path to the file to read.
    
    Returns:
        str: Content of the file.
    
    Raises:
        ValueError: If the path is outside the sandbox.
        FileNotFoundError: If the file does not exist.
        IOError: If there's an error reading the file.
    """
    validated_path = _validate_path(file_path)
    
    if not validated_path.exists():
        raise FileNotFoundError(f"❌ File not found: {validated_path}")
    
    if not validated_path.is_file():
        raise ValueError(f"❌ Path is not a file: {validated_path}")
    
    try:
        with open(validated_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise IOError(f"❌ Error reading file '{validated_path}': {str(e)}") from e

def write_file(file_path: str, content: str) -> None:
    """
    Writes content to a file in the sandbox, creating it if it doesn't exist or overwriting it if it does.
    Creates parent directories if they don't exist.
    
    Args:
        file_path (str): Path to the file to write.
        content (str): Content to write to the file.
    
    Raises:
        ValueError: If the path is outside the sandbox.
        IOError: If there's an error writing the file.
    """
    validated_path = _validate_path(file_path)
    
    try:
        # Create parent directories if they don't exist
        validated_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(validated_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"❌ Error writing to file '{validated_path}': {str(e)}") from e


def run_pylint(file_path: str) -> str:
    """
    Runs pylint on the specified file and returns the output.
    
    Args:
        file_path (str): Path to the Python file to lint.
    
    Returns:
        str: Pylint output containing score and error messages.
    """
    validated_path = _validate_path(file_path)
    
    if not validated_path.exists():
        return f"❌ Error: File not found: {validated_path}"
    
    try:
        # Use the current virtual environment's Python executable
        # Run pylint as a module to ensure we use the venv's pylint
        result = subprocess.run(
            [sys.executable, '-m', 'pylint', str(validated_path)],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            check=False,
        )
        
        # Combine stdout and stderr for complete output
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
        
        return output if output.strip() else "✅ Pylint completed with no output."
        
    except subprocess.TimeoutExpired:
        return "❌ Error: Pylint execution timed out (60s limit)."
    except FileNotFoundError:
        return "❌ Error: pylint is not installed. Run: pip install pylint"
    except Exception as e:
        return f"❌ Error running pylint: {str(e)}"

def run_pytest(test_path: str) -> str:
    """
    Runs pytest on the specified test file or directory and returns the output.
    
    Args:
        test_path (str): Path to the test file or directory.
    
    Returns:
        str: Pytest output containing test results and failure logs.
    """
    validated_path = _validate_path(test_path)
    
    if not validated_path.exists():
        return f"❌ Error: Test path not found: {validated_path}"
    
    try:
        # Use the current virtual environment's Python executable
        # Run pytest as a module with verbose output
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(validated_path), '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=120  # 120 second timeout for tests
        )
        
        # Combine stdout and stderr for complete output
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
        
        # Add return code information
        if result.returncode == 0:
            output = f"✅ All tests passed!\n\n{output}"
        else:
            output = f"❌ Tests failed (exit code: {result.returncode})\n\n{output}"
        
        return output if output.strip() else "⚠️ Pytest completed with no output."
        
    except subprocess.TimeoutExpired:
        return "❌ Error: Pytest execution timed out (120s limit)."
    except FileNotFoundError:
        return "❌ Error: pytest is not installed. Run: pip install pytest"
    except Exception as e:
        return f"❌ Error running pytest: {str(e)}"
