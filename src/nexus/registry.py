from ast import List
from csv import Error
from pathlib import Path
from typing import Any, Dict
import yaml
from nexus import workspace
from nexus.agent import Agent

class AgentsRegistryNotFound(Exception):
    """Raise when agents registry "agents.yaml" is not found."""
    pass

class UnknownAgentError(Exception):
    """Raise when agent name doesn't exist in registry."""
    pass


def get_agents_path(workspace_root: Path) -> Path:

    agents_path = workspace_root / ".nexus" / "agents.yaml"

    if not agents_path.exists():
        raise AgentsRegistryNotFound
    
    return agents_path


def load_agents(workspace_root: str) -> dict:
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
            command=list[str](item['command']),
            allowed_tools=item.get('allowed_tools'),
            llm_profile=item.get('llm_profile'),
        )
        agents[agent.name] = agent
    return agents


def get_agent(workspace_root: Path, agent_name: str) -> Agent:
    agents = load_agents(workspace_root)

    try:
        return agents[agent_name]
    except KeyError:
        raise UnknownAgentError(f"Unknowns agent: {agent_name!r}") from None
    pass


def list_agents(workspace_root: Path) -> List[Agent]:
    return list[Agent](load_agents(workspace_root).values())


