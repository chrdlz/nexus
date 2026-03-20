"""Run representation and persistence: run records and log paths.

This module defines the Run dataclass (agent run metadata and status), validates
run status values, and provides helpers to resolve paths to run YAML files and
log files under .nexus/runs and .nexus/logs.
"""
from csv import Error
from dataclasses import asdict, dataclass
import datetime
from pathlib import Path
from typing import Any, Literal, Optional
import secrets
import nexus.utils as u
import datetime as dt

import yaml

# Defaults for optional Run fields when loading from dict
RUN_CLS_DEFAULT_FINISHEDAT = None
RUN_CLS_DEFAULT_OUTPUT = None
RUN_CLS_DEFAULT_ERROR = None

PATH_TO_RUNS = ".nexus/runs"

RunStatus = Literal["pending", "running", "succeeded", "failed"]

ALLOWED_RUN_STATUSES: set[RunStatus] = {
    "pending",
    "running",
    "succeeded",
    "failed",
}


class InvalidStatusError(Exception):
    """Raised when a run dict contains a status not in ALLOWED_RUN_STATUSES."""
    pass


class RunsPathNotExisting(Exception):
    """Raised when a run dict contains a status not in ALLOWED_RUN_STATUSES."""
    pass


class InvalidRunsModeError(Exception):
    pass

class InvalidSortOptionError(Exception):
    pass

class InvalidOrderOptionError(Exception):
    pass

@dataclass
class Run:
    """Single agent run: id, agent, status, timestamps, input/output, and log path."""

    id: str
    agent: str
    status: RunStatus
    started_at: str
    finished_at: Optional[str]
    input: str
    output: Optional[str]
    error: Optional[str]
    log_path: str

    @classmethod
    def from_dict(cls, d: dict) -> "Run":
        """Build a Run instance from a dictionary (e.g. from run YAML).

        Parameters
        ----------
        d : dict
            Must contain: id, agent, status, started_at, input, log_path.
            finished_at, output, error are optional.

        Returns
        -------
        Run
            Populated run instance.

        Raises
        ------
        InvalidStatusError
            If ``d["status"]`` is not one of the allowed run statuses.
        """
        raw_status = d["status"]
        if raw_status not in ALLOWED_RUN_STATUSES:
            raise InvalidStatusError

        return cls(
            id=d["id"],
            agent=d["agent"],
            status=raw_status,
            started_at=d["started_at"],
            finished_at=d.get("finished_at", RUN_CLS_DEFAULT_FINISHEDAT),
            input=d["input"],
            output=d.get("output", RUN_CLS_DEFAULT_OUTPUT),
            error=d.get("error", RUN_CLS_DEFAULT_ERROR),
            log_path=d["log_path"],
        )

    def to_dict(self) -> dict:
        """Convert run to a dict suitable for YAML serialization.

        Returns
        -------
        dict
            All fields as key-value pairs.
        """
        return asdict(self)


def get_run_path(root: Path, run_id: str) -> Path:
    """Return the path to a run's YAML file under .nexus/runs.

    Parameters
    ----------
    root : Path
        Workspace root directory.
    run_id : str
        Run identifier (used as filename stem).

    Returns
    -------
    Path
        Path to ``.nexus/runs/{run_id}.yaml``.
    """
    return root / get_nexus_path_relative(run_id=run_id, type="runs")


def get_log_path(root: Path, log_id: str) -> Path:
    """Return the path to a run's log file under .nexus/logs.

    Parameters
    ----------
    root : Path
        Workspace root directory.
    log_id : str
        Log identifier (typically same as run id; used as filename stem).

    Returns
    -------
    Path
        Path to ``.nexus/logs/{log_id}.log``.
    """
    return root / get_nexus_path_relative(run_id=log_id)


def get_nexus_path_relative(run_id: str, type: str = "log") -> str:
    """Return relative path for a run YAML or log file under .nexus/runs or .nexus/logs."""
    if type == "runs":
        return f".nexus/runs/{run_id}.yaml"
    return f".nexus/logs/{run_id}.log"
    

def record_run(
    root: Path, 
    agent: str,
    input: str,
    ) -> Run:
    """Create and persist a new run record and initialize its log.

    Parameters
    ----------
    root:
        Workspace root directory.
    agent:
        Agent name being executed.
    input:
        Input/prompt text recorded with the run.

    Returns
    -------
    Run
        Newly created run object with status `"running"`.
    """

    run_id = secrets.token_hex(8)   # 8 bytes → 16 hex chars
    log_path = get_log_path(root=root, log_id=run_id)

    r = Run(
        id = run_id, 
        agent = agent,
        status = "running",
        started_at = str(datetime.datetime.now(datetime.timezone.utc)).split(".")[0],
        finished_at=None,
        input=input,
        output=None,
        error=None,
        log_path=get_nexus_path_relative(run_id)
    )

    get_run_path(root=root, run_id=run_id).write_text(yaml.safe_dump(r.to_dict(), sort_keys=False))

    with open(log_path, "a") as f:
        f.write(r.started_at + ": Run started\n")

    return r

def end_run(
    root: Path, 
    run: Run,
    exit_code: int,
    output_text: str,
    error_text: str = None,
    ) -> Run:
    """Finalize a run: set terminal status, persist YAML, and append to log.

    Parameters
    ----------
    root:
        Workspace root directory.
    run:
        Run object to finalize.
    exit_code:
        Subprocess exit code. `0` becomes `"succeeded"`, non-zero becomes `"failed"`.
    output_text:
        Short human-readable summary to store in the run YAML.
    error_text:
        Optional short error summary to store in the run YAML.

    Returns
    -------
    dict
        YAML-serializable run record (the run converted to a dict).
    """

    log_path = get_log_path(root=root, log_id=run.id)

    r = run.to_dict()

    r['finished_at'] = str(datetime.datetime.now(datetime.timezone.utc)).split(".")[0]
    r['status'] = "succeeded" if exit_code == 0 else "failed"
    r['output'] = output_text
    r['error'] = error_text if error_text!=None else None

    # write on id.yamls
    u.overwrite_yaml(
        path=get_run_path(root=root, run_id=r["id"]),
        data=r
    )

    # write on id.log
    log_entry = r['finished_at'] + ": Run finished (" + r['status'] + ", exit=" + str(exit_code) + ")"
    u.append_text(log_path, log_entry)

    return r


def load_runs(workspace_root: Path) -> list[Run]:
    """Load all run YAML records from `.nexus/runs` in a workspace.

    Parameters
    ----------
    workspace_root:
        Workspace root directory.

    Returns
    -------
    list[Run]
        All runs found under `.nexus/runs` (empty list if none exist).

    Raises
    ------
    RunsPathNotExisting
        If the `.nexus/runs` directory does not exist.
    """
    cfg_path = workspace_root / ".nexus/runs"

    if not cfg_path.exists():
        raise RunsPathNotExisting()

    runs_list = list(cfg_path.glob("*.yaml")) or []

    if runs_list == []:
        return []
    else:
        return [Run.from_dict(u.laod_yaml(x)) for x in runs_list ]


def get_run(
    workspace_root: Path,
    mode: str | None = None,
    run_id: str | None = None,
    *,
    opt_sort: str = "started_at",
    opt_order: str = "desc"
    ) -> list:
    """Query run records for a workspace.

    Parameters
    ----------
    workspace_root:
        Workspace root directory.
    mode:
        Query mode:
        - `"all"` or `None`: return a dict of all runs keyed by run id
        - `"last"`: return the most recent run (by `started_at`)
        - `"single"`: return one run by `run_id`
    run_id:
        Run identifier used when `mode == "single"`.

    Returns
    -------
    dict
        A run dict (for `"last"`/`"single"`) or a dict of run dicts (for `"all"`).
        Returns `{}` if no runs are found or the requested run id is missing.

    Raises
    ------
    InvalidRunsModeError
        If `mode` is not one of the supported values.
    """
    try:
        runs_list = load_runs(workspace_root)
    except RunsPathNotExisting:
        return []

    if runs_list != []:

        runs_dicts = {}
        last_date_dt = None
        last_run = None

        for item in runs_list:
            runs_dicts[item.id] = item.to_dict()
            item_date_dt = dt.datetime.fromisoformat(item.started_at)

            if (last_run is None) or (item_date_dt > last_date_dt):
                last_run = item
                last_date_dt = item_date_dt

        if (mode == "all") or (mode is None):
            
            if opt_sort not in ["id", "agent", "started_at", "finished_at"] and opt_sort is not None:
                raise InvalidSortOptionError()
            
            if opt_order not in ["asc", "desc"] and opt_order is not None:
                raise InvalidOrderOptionError()

            runs_dict_sorted_ordered = []
            for tmp_id, tmp_run_dict in runs_dicts.items():
                runs_dict_sorted_ordered.append(tmp_run_dict)

            # sort
            def make_key_fn(sort_key: str = "started_at"):
                def key_fn(item: dict) -> str:
                    value = item.get(sort_key)
                    return "" if value is None else value
                return key_fn

            runs_dict_sorted_ordered.sort(key=make_key_fn(opt_sort), reverse=(opt_order=="desc"))

            return runs_dict_sorted_ordered

        elif mode == "last":
            return [last_run.to_dict()]

        elif mode == "single":
            run_found = {}

            for item in runs_list:
                if item.id == run_id:
                    return [item.to_dict()]

            return [run_found]

        else:
            raise InvalidRunsModeError() # this to be fixed / improved

    else:
        return []
