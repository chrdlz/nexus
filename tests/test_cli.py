"""Tests for CLI: init and status via subprocess, checking exit code and stdout."""
import os
from pathlib import Path
import subprocess
from nexus.cli import MSG_WS_INIT_SUCCESS, MSG_MANIFEST_NOT_FOUND

# Project root (parent of tests/) for PYTHONPATH and cwd when running CLI
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    """Run nexus CLI with -C tmp_path and given args; return CompletedProcess.

    Parameters
    ----------
    tmp_path : Path
        Workspace directory passed as -C.
    *args : str
        Additional CLI arguments (e.g. "init", "myworkspace", "-d", "mydesc").

    Returns
    -------
    subprocess.CompletedProcess
        Result of subprocess.run with capture_output=True, text=True.
    """
    cmd = [
        "python3",
        "-m",
        "nexus.cli",
        "-C",
        str(tmp_path),
        *args,
    ]
    results = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        env={
            **os.environ,
            "PYTHONPATH": "src",
        },
        capture_output=True,
        text=True,
    )
    return results


def test_manifest_init(tmp_path: Path) -> None:
    """CLI init with name and options succeeds and creates manifest.yaml."""
    cli_output = run_cli(
        tmp_path, "init", "myworkspace", "-d", "mydesc", "-v", "myvers"
    )
    assert cli_output.returncode == 0
    assert MSG_WS_INIT_SUCCESS in cli_output.stdout
    manifest_path = tmp_path / "manifest.yaml"
    assert manifest_path.exists()


def test_manifest_not_found(tmp_path: Path) -> None:
    """CLI status in a directory without manifest exits 1 and prints error message."""
    cli_output = run_cli(tmp_path, "status")
    assert cli_output.returncode == 1
    assert MSG_MANIFEST_NOT_FOUND in cli_output.stdout
