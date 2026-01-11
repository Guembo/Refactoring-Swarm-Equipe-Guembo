import pytest
from pathlib import Path
import src.tools

from unittest.mock import patch

from src.tools import _validate_path
from src.tools import read_file
from src.tools import write_file

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
