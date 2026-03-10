# tests/test_workspace.py

"""
Import workspace fuctions
Arrange situation
Call function
Assert expected results 
"""

# tests
# test init creates manifest and workspace is consistent with expected manifest
from pathlib import Path

import agentorchestrator.workspace as ws 
import pytest


def test_init_consistency_manifest(tmp_path: Path) -> None:
    ws_dir = tmp_path 
    w = ws.init_workspace("mymanifest", "mydesc", "1.1.1", directory=ws_dir)

    # Assert Workspace object looks right
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

# test init workspace once, assert ok, init once again assert error
def test_double_init_raise_error(tmp_path: Path) -> None:
    ws_dir = tmp_path 
    ws.init_workspace("mymanifest", directory=ws_dir) # first time should be OK

    # # Second time shuld fail
    # try:
    #     ws.init_workspace("mymanifest", directory=ws_dir)
    #     assert False, "Warning: expected ManifestAlreadyExistsError."
    # except ws.ManifestAlreadyExistsError:
    #     pass

    with pytest.raises(ws.ManifestAlreadyExistsError):
        ws.init_workspace("mymanifest", directory=ws_dir)