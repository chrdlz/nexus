from csv import Error
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Optional

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

class InvalidStatusError(Exception): pass

@dataclass
class Run:
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
        # validation
        raw_status = d["status"]
        if raw_status not in ALLOWED_RUN_STATUSES:
            raise InvalidStatusError

        return cls(
            id = d["id"],
            agent = d["agent"],
            status = raw_status,
            started_at = d["started_at"],
            finished_at = d.get("finished_at",RUN_CLS_DEFAULT_FINISHEDAT),
            input = d["input"],
            output = d.get("output",RUN_CLS_DEFAULT_OUTPUT),
            error = d.get("error",RUN_CLS_DEFAULT_ERROR),
            log_path = d["log_path"]
        )

    def to_dict(self) -> dict:
        return asdict(self)


def get_run_path(root: Path, run_id: str) -> Path:
    """Retrieves the path of a run's yaml files."""
    return root / ".coral" / "runs" / f"{run_id}.yaml"
    

def get_log_path(root: Path, log_id: str) -> Path:
    """Retrieves the path of a run's logs files."""
    return root / ".coral" / "logs" / f"{log_id}.log"