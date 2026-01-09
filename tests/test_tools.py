import pytest
from pathlib import Path
import src.tools

from src.tools import _validate_path


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
