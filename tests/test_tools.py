import sys
import pytest
import subprocess
from pathlib import Path
import src.tools

from unittest.mock import patch, MagicMock


from src.tools import _validate_path, read_file, write_file, run_pylint

def test_validate_path_inside_sandbox(tmp_path, monkeypatch):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    test_file = sandbox / "file.txt"
    test_file.write_text("ok")

    monkeypatch.setattr(src.tools, "SANDBOX_DIR", sandbox)

    result = _validate_path(str(test_file))

    assert result == test_file.resolve()


def test_validate_path_outside_sandbox(tmp_path, monkeypatch):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("nope")

    monkeypatch.setattr(src.tools, "SANDBOX_DIR", sandbox)

    with pytest.raises(ValueError):
        _validate_path(str(outside_file))


def test_validate_path_with_path_traversal(tmp_path, monkeypatch):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    outside = tmp_path / "outside.txt"
    outside.write_text("attack")

    traversal_path = sandbox / ".." / "outside.txt"

    monkeypatch.setattr(src.tools, "SANDBOX_DIR", sandbox)

    with pytest.raises(ValueError):
        _validate_path(str(traversal_path))


@pytest.mark.skipif(not hasattr(Path, "symlink_to"), reason="Symlinks not supported")
def test_validate_path_symlink_escape(tmp_path, monkeypatch):
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    outside = tmp_path / "outside.txt"
    outside.write_text("secret")

    symlink = sandbox / "link.txt"
    symlink.symlink_to(outside)

    monkeypatch.setattr(src.tools, "SANDBOX_DIR", sandbox)

    with pytest.raises(ValueError):
        _validate_path(str(symlink))



def test_read_file_success(tmp_path):
    # create a real file
    file = tmp_path / "test.txt"
    file.write_text("hello world", encoding="utf-8")

    # mock validation to return this file
    with patch("src.tools._validate_path", return_value=file):
        content = read_file("test.txt")

    assert content == "hello world"


def test_read_file_not_found(tmp_path):
    file = tmp_path / "missing.txt"  # not created

    with patch("src.tools._validate_path", return_value=file):
        with pytest.raises(FileNotFoundError) as exc:
            read_file("missing.txt")

    assert "File not found" in str(exc.value)


def test_read_file_not_a_file(tmp_path):
    directory = tmp_path / "dir"
    directory.mkdir()

    with patch("src.tools._validate_path", return_value=directory):
        with pytest.raises(ValueError) as exc:
            read_file("dir")

    assert "Path is not a file" in str(exc.value)



def test_read_file_io_error(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("data", encoding="utf-8")

    with patch("src.tools._validate_path", return_value=file):
        with patch("builtins.open", side_effect=OSError("boom")):
            with pytest.raises(IOError) as exc:
                read_file("test.txt")

    assert "Error reading file" in str(exc.value)
def test_write_file_success(tmp_path):
    # Setup: Define target file in tmp_path
    target_file = tmp_path / "output.txt"
    content = "New Content"

    # Mock validation to return the safe temporary path
    with patch("src.tools._validate_path", return_value=target_file):
        write_file("output.txt", content)

    # Assert file was created and content matches
    assert target_file.exists()
    assert target_file.read_text(encoding="utf-8") == content


def test_write_file_creates_directories(tmp_path):
    # Setup: Define a nested path that doesn't exist yet
    target_file = tmp_path / "folder" / "subfolder" / "file.txt"
    content = "Nested Content"

    # Mock validation to return the nested path
    with patch("src.tools._validate_path", return_value=target_file):
        write_file("folder/subfolder/file.txt", content)

    # Assert directories were created and file exists
    assert target_file.exists()
    assert target_file.parent.exists()
    assert target_file.read_text(encoding="utf-8") == content


def test_write_file_overwrites_existing(tmp_path):
    # Setup: Create an existing file
    target_file = tmp_path / "existing.txt"
    target_file.write_text("Old Content", encoding="utf-8")
    
    new_content = "Overwritten Content"

    with patch("src.tools._validate_path", return_value=target_file):
        write_file("existing.txt", new_content)

    # Assert content was updated
    assert target_file.read_text(encoding="utf-8") == new_content


def test_write_file_validation_error():
    # Setup: Mock validation to raise ValueError (simulating outside sandbox)
    with patch("src.tools._validate_path", side_effect=ValueError("Outside sandbox")):
        with pytest.raises(ValueError) as exc:
            write_file("../forbidden.txt", "data")

    assert "Outside sandbox" in str(exc.value)


def test_write_file_io_error(tmp_path):
    target_file = tmp_path / "test.txt"
    
    # Mock validation to return a valid path
    with patch("src.tools._validate_path", return_value=target_file):
        # Mock open() to simulate a permission error or disk failure
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(IOError) as exc:
                write_file("test.txt", "content")

    # Assert custom error message formatting
    assert "❌ Error writing to file" in str(exc.value)
    assert "Permission denied" in str(exc.value)
def test_run_pylint_success(tmp_path):
    # Setup: Create a dummy python file
    target_file = tmp_path / "script.py"
    target_file.touch()

    # Setup: Mock the subprocess result
    mock_process = MagicMock()
    mock_process.stdout = "Your code has been rated at 10.00/10"
    mock_process.stderr = ""

    # Mock validation to return the real path
    with patch("src.tools._validate_path", return_value=target_file):
        # Mock subprocess to avoid actually running pylint
        with patch("subprocess.run", return_value=mock_process) as mock_run:
            result = run_pylint("script.py")

            # Assert subprocess was called correctly
            # Updated to include check=False
            mock_run.assert_called_once_with(
                [sys.executable, '-m', 'pylint', str(target_file)],
                capture_output=True,
                text=True,
                timeout=60,
                check=False  # <--- This was missing in the previous test
            )

    # Assert output matches stdout
    assert "rated at 10.00/10" in result
def test_run_pylint_file_not_found_check(tmp_path):
    # Setup: Define a path that DOES NOT exist
    missing_file = tmp_path / "ghost.py"

    # Mock validation to return the non-existent path
    with patch("src.tools._validate_path", return_value=missing_file):
        # We don't need to patch subprocess because the function returns early
        result = run_pylint("ghost.py")

    assert "❌ Error: File not found" in result
    assert str(missing_file) in result


def test_run_pylint_with_stderr_output(tmp_path):
    target_file = tmp_path / "script.py"
    target_file.touch()

    mock_process = MagicMock()
    mock_process.stdout = "Standard output"
    mock_process.stderr = "Import error warning"

    with patch("src.tools._validate_path", return_value=target_file):
        with patch("subprocess.run", return_value=mock_process):
            result = run_pylint("script.py")

    # Assert both outputs are combined
    assert "Standard output" in result
    assert "--- STDERR ---" in result
    assert "Import error warning" in result


def test_run_pylint_timeout(tmp_path):
    target_file = tmp_path / "script.py"
    target_file.touch()

    with patch("src.tools._validate_path", return_value=target_file):
        # Simulate a timeout exception
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="pylint", timeout=60)):
            result = run_pylint("script.py")

    assert "❌ Error: Pylint execution timed out" in result


def test_run_pylint_not_installed(tmp_path):
    target_file = tmp_path / "script.py"
    target_file.touch()

    with patch("src.tools._validate_path", return_value=target_file):
        # Simulate the executable not being found
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = run_pylint("script.py")

    assert "❌ Error: pylint is not installed" in result


def test_run_pylint_empty_output(tmp_path):
    target_file = tmp_path / "script.py"
    target_file.touch()

    mock_process = MagicMock()
    mock_process.stdout = ""  # Empty stdout
    mock_process.stderr = ""  # Empty stderr

    with patch("src.tools._validate_path", return_value=target_file):
        with patch("subprocess.run", return_value=mock_process):
            result = run_pylint("script.py")

    # Should return the default success message
    assert "✅ Pylint completed with no output" in result


def test_run_pylint_generic_exception(tmp_path):
    target_file = tmp_path / "script.py"
    target_file.touch()

    with patch("src.tools._validate_path", return_value=target_file):
        with patch("subprocess.run", side_effect=Exception("Unexpected crash")):
            result = run_pylint("script.py")

    assert "❌ Error running pylint" in result
    assert "Unexpected crash" in result


def test_run_pylint_not_a_file(tmp_path):
    """Test that run_pylint handles directories appropriately."""
    # Setup: Create a directory instead of a file
    target_dir = tmp_path / "my_directory"
    target_dir.mkdir()

    # Mock validation to return the directory path
    with patch("src.tools._validate_path", return_value=target_dir):
        # Mock subprocess to simulate pylint's behavior on a directory
        mock_process = MagicMock()
        mock_process.stdout = "pylint output on directory"
        mock_process.stderr = ""
        
        with patch("subprocess.run", return_value=mock_process):
            result = run_pylint("my_directory")

    # Verify that the function still executes (current behavior)
    # Note: This documents current behavior where directories are passed to pylint
    assert "pylint output on directory" in result
