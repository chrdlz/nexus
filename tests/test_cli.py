"""Tests for CLI: init and status via subprocess, checking exit code and stdout."""
import os
from pathlib import Path
import subprocess
import yaml
from nexus.cli import MSG_WS_INIT_SUCCESS, MSG_MANIFEST_NOT_FOUND
import nexus.run as r
from nexus.workspace import init_workspace

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


def test_runs_list_and_show_commands(tmp_path: Path) -> None:
    """CLI runs list/show works for existing run files."""
    ws_dir = tmp_path
    init_workspace("test-ws", directory=ws_dir)

    run_a = r.Run(
        id="run-a",
        agent="alpha",
        status="succeeded",
        started_at="2026-01-01 10:00:00+00:00",
        finished_at="2026-01-01 10:00:01+00:00",
        input="a",
        output="ok",
        error=None,
        log_path=".nexus/logs/run-a.log",
    )
    run_b = r.Run(
        id="run-b",
        agent="beta",
        status="failed",
        started_at="2026-01-01 12:00:00+00:00",
        finished_at="2026-01-01 12:00:01+00:00",
        input="b",
        output=None,
        error="exit=1",
        log_path=".nexus/logs/run-b.log",
    )
    r.get_run_path(ws_dir, run_a.id).write_text(yaml.safe_dump(run_a.to_dict(), sort_keys=False))
    r.get_run_path(ws_dir, run_b.id).write_text(yaml.safe_dump(run_b.to_dict(), sort_keys=False))

    list_output = run_cli(ws_dir, "runs", "list", "--list-all", "--sort", "started_at", "--order", "desc")
    assert list_output.returncode == 0
    assert "run-b" in list_output.stdout
    assert "run-a" in list_output.stdout

    show_output = run_cli(ws_dir, "runs", "show", "run-a")
    assert show_output.returncode == 0
    assert "run-a" in show_output.stdout
