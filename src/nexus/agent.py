"""Agent definitions.

This module defines the core `Agent` unit: a named, runnable entity that Nexus
can execute inside a workspace.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Agent:
    """Agent definition loaded from the workspace registry.

    Parameters
    ----------
    name:
        Unique agent name (registry key).
    description:
        Human-readable summary shown in CLI/UI.
    command:
        Command argv used to execute the agent (passed to `subprocess.run`).
    allowed_tools:
        Optional allowlist of tool identifiers the agent may use (future).
    llm_profile:
        Optional LLM profile name to resolve to a provider/model (future).
    """
    name: str
    description: str
    command: List[str]
    allowed_tools: Optional[List[str]] = None
    llm_profile: Optional[str] = None
    