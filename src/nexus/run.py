"""Run representation and persistence: run records and log paths.

This module defines the Run dataclass (agent run metadata and status), validates
run status values, and provides helpers to resolve paths to run YAML files and
log files under .nexus/runs and .nexus/logs.
"""
from dataclasses import asdict, dataclass
import datetime
from pathlib import Path
from typing import Literal, Optional
import secrets

import yaml

# Defaults for optional Run fields when loading from dict
RUN_CLS_DEFAULT_FINISHEDAT = None
RUN_CLS_DEFAULT_OUTPUT = None
RUN_CLS_DEFAULT_ERROR = None

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
