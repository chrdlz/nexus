import os
from pathlib import Path
import subprocess
from agentorchestrator.cli import MSG_WS_INIT_SUCCESS, MSG_MANIFEST_NOT_FOUND

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # tests/ → project root

def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    cmd = ["python3",
        "-m",
        "agentorchestrator.cli",
        "-C",
        str(tmp_path),
        *args
    ]

    results = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        env={ # inherit env then override PYTHONPATH
            **os.environ,
            "PYTHONPATH": "src",
        },
        capture_output=True,
        text=True
    )

    return results

def test_manifest_init(tmp_path: Path) -> None:
    cli_output = run_cli(tmp_path,"init", "myworkspace", "-d", "mydesc", "-v", "myvers")

    # assert process uscceeded
    assert cli_output.returncode == 0
    assert MSG_WS_INIT_SUCCESS in cli_output.stdout

    # assert manifest created successfully
    manifest_path = tmp_path / "manifest.yaml"
    assert manifest_path.exists()

def test_manifest_not_found(tmp_path: Path) -> None:
    cli_output = run_cli(tmp_path,"status")

    # assert process uscceeded
    assert cli_output.returncode == 1
    assert MSG_MANIFEST_NOT_FOUND in cli_output.stdout
