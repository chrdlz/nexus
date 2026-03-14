"""Tests for run module: Run dataclass, from_dict/to_dict, and path helpers."""
import datetime
from pathlib import Path

import yaml
import agentorchestrator.run as r
from agentorchestrator.workspace import init_workspace


def test_run_roundtrip(tmp_path: Path) -> None:
    """Writing a Run to YAML and loading back via from_dict yields an equal Run."""
    ws_dir = tmp_path
    init_workspace("test-ws", directory=ws_dir)

    run_id = "myid"
    log_rel_path = f".coral/logs/{run_id}.log"

    run = r.Run(
        id = run_id,
        agent="myagent",
        status="succeeded",
        started_at=str(datetime.datetime.now(datetime.timezone.utc)).split('.')[0],
        finished_at=None,
        input="some inputs..",
        output="some outputs..",
        error=None,
        log_path=log_rel_path
    )

    # create runs.yaml with helper
    run_path_created = r.get_run_path(ws_dir, run_id)
    run_path_created.write_text(yaml.safe_dump(run.to_dict(), sort_keys=False))

    run_path = ws_dir / ".coral/runs" / f"{run_id}.yaml"
    assert run_path.exists()

    loaded_dict = yaml.safe_load(run_path.read_text())
    loaded_run = r.Run.from_dict(loaded_dict)

    assert loaded_run == run