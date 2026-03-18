"""Workspace agent registry.

Loads agent definitions from `.nexus/agents.yaml` and provides lookup and list
helpers for other parts of Nexus (CLI and orchestrator).
"""

from typing import List
from pathlib import Path
from typing import Dict
import yaml
from nexus.agent import Agent

class AgentsRegistryNotFound(Exception):
    """Raise when agents registry "agents.yaml" is not found."""
    pass

class UnknownAgentError(Exception):
    """Raise when agent name doesn't exist in registry."""
    pass


def get_agents_path(workspace_root: Path) -> Path:
    """Return the path to `.nexus/agents.yaml` for a workspace.

    Parameters
    ----------
    workspace_root:
        Workspace root directory.

    Returns
    -------
    Path
        Absolute path to the agent registry file.

    Raises
    ------
    AgentsRegistryNotFound
        If `.nexus/agents.yaml` does not exist.
    """

    agents_path = workspace_root / ".nexus" / "agents.yaml"
    
    if not agents_path.exists():
        raise AgentsRegistryNotFound()
    
    return agents_path


def load_agents(workspace_root: Path) -> Dict[str, Agent]:
    """Load all agents for a workspace from `.nexus/agents.yaml`.

    Parameters
    ----------
    workspace_root:
        Workspace root directory.

    Returns
    -------
    dict[str, Agent]
        Agents keyed by agent name.
    """
    cfg_path = get_agents_path(workspace_root)
    if not cfg_path.exists():
        # raise error
        return {}

    raw = yaml.safe_load(cfg_path.read_text()) or {}
    raw_agents = raw.get("agents", []) or []

    agents: Dict[str, Agent] = {}
    for item in raw_agents:
        agent = Agent(
            name=item['name'],
            description=item['description'],
            command=list(item['command']),
            allowed_tools=item.get('allowed_tools'),
            llm_profile=item.get('llm_profile'),
        )
        agents[agent.name] = agent
    return agents


def get_agent(workspace_root: Path, agent_name: str) -> Agent:
    """Return a single agent by name from the workspace registry.

    Parameters
    ----------
    workspace_root:
        Workspace root directory.
    agent_name:
        Agent name to look up.

    Returns
    -------
    Agent
        Resolved agent definition.

    Raises
    ------
    UnknownAgentError
        If the agent is not present in the registry.
    """
    agents = load_agents(workspace_root)

    try:
        return agents[agent_name]
    except KeyError:
        raise UnknownAgentError(f"Unknowns agent: {agent_name!r}") from None


def list_agents(workspace_root: Path) -> List[Agent]:
    """List all agents defined in the workspace registry.

    Parameters
    ----------
    workspace_root:
        Workspace root directory.

    Returns
    -------
    list[Agent]
        All agents from `.nexus/agents.yaml`.
    """
    return list(load_agents(workspace_root).values())


