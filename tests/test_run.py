"""Tests for run module: Run dataclass, from_dict/to_dict, and path helpers."""
import datetime
from pathlib import Path

import yaml
import nexus.run as r
from nexus.workspace import init_workspace
import pytest


def test_run_roundtrip(tmp_path: Path) -> None:
    """Writing a Run to YAML and loading back via from_dict yields an equal Run."""
    ws_dir = tmp_path
    init_workspace("test-ws", directory=ws_dir)

    run_id = "myid"
    log_rel_path = f".nexus/logs/{run_id}.log"

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

    run_path = ws_dir / ".nexus/runs" / f"{run_id}.yaml"
    assert run_path.exists()

    loaded_dict = yaml.safe_load(run_path.read_text())
    loaded_run = r.Run.from_dict(loaded_dict)

    assert loaded_run == run


def test_get_run_modes_and_sorting(tmp_path: Path) -> None:
    """get_run returns expected runs for all/last/single modes and sorting."""
    ws_dir = tmp_path
    init_workspace("test-ws", directory=ws_dir)

    run_a = r.Run(
        id="run-a",
        agent="alpha",
        status="succeeded",
        started_at="2026-01-01 10:00:00+00:00",
        finished_at="2026-01-01 10:00:02+00:00",
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
        finished_at="2026-01-01 12:00:02+00:00",
        input="b",
        output=None,
        error="exit=1",
        log_path=".nexus/logs/run-b.log",
    )

    r.get_run_path(ws_dir, run_a.id).write_text(yaml.safe_dump(run_a.to_dict(), sort_keys=False))
    r.get_run_path(ws_dir, run_b.id).write_text(yaml.safe_dump(run_b.to_dict(), sort_keys=False))

    all_runs = r.get_run(ws_dir, "all", opt_sort="started_at", opt_order="desc")
    assert [item.id for item in all_runs] == ["run-b", "run-a"]

    last_run = r.get_run(ws_dir, "last")
    assert len(last_run) == 1
    assert last_run[0].id == "run-b"

    single_run = r.get_run(ws_dir, "single", run_id="run-a")
    assert len(single_run) == 1
    assert single_run[0].id == "run-a"

    missing = r.get_run(ws_dir, "single", run_id="missing-id")
    assert missing == []


def test_get_run_invalid_sort_and_order_raise(tmp_path: Path) -> None:
    """Invalid sort/order options raise dedicated errors in all mode."""
    ws_dir = tmp_path
    init_workspace("test-ws", directory=ws_dir)

    base_run = r.Run(
        id="run-x",
        agent="alpha",
        status="succeeded",
        started_at="2026-01-01 10:00:00+00:00",
        finished_at="2026-01-01 10:00:01+00:00",
        input="x",
        output="ok",
        error=None,
        log_path=".nexus/logs/run-x.log",
    )
    r.get_run_path(ws_dir, base_run.id).write_text(yaml.safe_dump(base_run.to_dict(), sort_keys=False))

    with pytest.raises(r.InvalidSortOptionError):
        r.get_run(ws_dir, "all", opt_sort="unknown", opt_order="desc")

    with pytest.raises(r.InvalidOrderOptionError):
        r.get_run(ws_dir, "all", opt_sort="started_at", opt_order="sideways")