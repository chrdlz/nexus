from dataclasses import dataclass
from pathlib import Path
import yaml


def laod_yaml(path: Path) -> dict:
    with open(path, 'r', encodinf="utf-8") as f:
        return yaml.safe_load(f) or {} # empty file -> None


def overwrite_yaml(path: str, data: dict) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


def append_text(path: str | Path, text: str, *, newline: bool = True) -> None:
    """
    Append `text` to `path`. If newline=True, ensure the appended record ends
    with a single '\n' so log entries don't run together.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    record = text
    if newline and not record.endswith("\n"):
        record += "\n"

    with p.open("a", encoding="utf-8") as f:
        f.write(record)