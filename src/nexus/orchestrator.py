"""Agent execution orchestration.

This module implements the Stage-1 orchestration loop:

1) record a new run (run YAML + initial log line)
2) execute the agent command inside the workspace
3) finalize the run with status/output/error summary and append logs
"""

from pathlib import Path
import traceback
from nexus.agent import Agent
from nexus.run import Run, get_log_path, record_run, end_run
import subprocess

from nexus.utils import append_text

RUN_SUCCESSFUL = "Run successful"
RUN_FAILED = "Run Failed"
RUN_FAILED_BEFORE_RUNNING = "Run Failed before running"

def spawn_agent(workspace_dir: Path, agent: Agent, input: str) -> (Run, int):
    """Record, execute, and finalize a single agent run.

    Parameters
    ----------
    workspace_dir:
        Workspace root directory (contains manifest and `.nexus/`).
    agent:
        Agent definition (loaded from `agents.yaml`).
    input:
        Optional input/prompt text to record in the run metadata.

    Returns
    -------
    (Run, int)
        Finalized run (as returned by `end_run`) and the command exit code.
    """
    r = record_run(root=workspace_dir, agent=agent.name, input=input)
    log_file = get_log_path(workspace_dir, log_id=r.id)

    error_summary = None
    exit_code = 1 # error by default
    output_text=RUN_FAILED_BEFORE_RUNNING

    try:
        exit_code = run_and_log_separate(running_dir=workspace_dir,agent=agent, log_path=log_file)
    
    except Exception as e:
        error_summary = f"{type(e).__name__}: {e}"
        tb = traceback.format_exc()
        append_text(log_file, text=tb)
    
    finally:

        if exit_code == 0:
            output_text = RUN_SUCCESSFUL
            error_summary = None
        else:
            output_text = RUN_FAILED
            error_summary = f"exit={exit_code}"

        r_end = end_run(
            root=workspace_dir,
            run=r,
            exit_code=exit_code,
            output_text=output_text,
            error_text=error_summary
        )
    
    return r_end, exit_code


def run_and_log_separate(running_dir: Path, agent: Agent, log_path: Path) -> int:
    """Run the agent command and stream its output into the run log file.

    Parameters
    ----------
    running_dir:
        Working directory used for the subprocess execution.
    agent:
        Agent whose command will be executed.
    log_path:
        Path to the run log file (append mode).

    Returns
    -------
    int
        Subprocess return code.
    """
    with log_path.open("a", encoding="utf-8") as f:
        result = subprocess.run(
            args=agent.command,
            cwd=running_dir,
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,             # decode bytes to str
        )
    
    return result.returncode
    