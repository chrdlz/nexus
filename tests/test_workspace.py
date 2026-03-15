# tests/test_workspace.py
"""Tests for workspace module: init, load, manifest consistency, and double-init error."""
from pathlib import Path

import nexus.workspace as ws
import pytest


def test_init_consistency_manifest(tmp_path: Path) -> None:
    """Init creates manifest and loaded workspace matches expected name, description, version."""
    ws_dir = tmp_path
    w = ws.init_workspace("mymanifest", "mydesc", "1.1.1", directory=ws_dir)

    # Assert Workspace object matches arguments
    assert w.name == "mymanifest"
    assert w.description == "mydesc"
    assert w.version == "1.1.1"

    # Assert manifest exists in ws_dir
    manifest_path = ws_dir / "manifest.yaml"
    assert manifest_path.exists()

    loaded = ws.load_workspace(ws_dir)

    # Assert manifest.yaml has correct keys/values
    assert loaded.name == "mymanifest"
    assert loaded.description == "mydesc"
    assert loaded.version == "1.1.1"

def test_double_init_raise_error(tmp_path: Path) -> None:
    """Second init in the same directory raises ManifestAlreadyExistsError."""
    ws_dir = tmp_path
    ws.init_workspace("mymanifest", directory=ws_dir)  # first time succeeds

    # Second init must raise
    # try:
    #     ws.init_workspace("mymanifest", directory=ws_dir)
    #     assert False, "Warning: expected ManifestAlreadyExistsError."
    # except ws.ManifestAlreadyExistsError:
    #     pass

    with pytest.raises(ws.ManifestAlreadyExistsError):
        ws.init_workspace("mymanifest", directory=ws_dir)