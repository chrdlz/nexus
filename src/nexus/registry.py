from pathlib import Path

class AgentsRegistryNotFound(Exception):
    """Raise when agents registry "agents.yaml" is not found"""
    pass


def get_agents(workspace_root: Path) -> Path:

    agents_path = workspace_root / ".nexus" / "agents.yaml"

    if not agents_path.exists():
        raise AgentsRegistryNotFound
    
    return agents_path
