from dataclasses import asdict, dataclass
from typing import Optional

RUN_CLS_DEFAULT_FINISHEDAT = ""
RUN_CLS_DEFAULT_OUTPUT = ""
RUN_CLS_DEFAULT_ERROR = ""

@dataclass
class Run:
    id: str
    agent: str
    status: str
    started_at: str
    finished_at: Optional[str]
    input: str
    output: Optional[str]
    error: Optional[str]
    log_path: str

    @classmethod
    def from_dict(cls, d: dict) -> "Run":
        return cls(
            id = d["id"],
            agent = d["agent"],
            status = d["status"],
            started_at = d["started_at"],
            finished_at = d.get("finished_at",RUN_CLS_DEFAULT_FINISHEDAT),
            input = d["input"],
            output = d.get("output",RUN_CLS_DEFAULT_OUTPUT),
            error = d.get("error",RUN_CLS_DEFAULT_ERROR),
            log_path = d["log_path"]
        )

    def as_dict(self) -> dict:
        return asdict(self)