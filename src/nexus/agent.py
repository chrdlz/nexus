from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Agent:
    name: str
    description: str
    command: List[str]
    allowed_tools: Optional[List[str]] = None
    llm_profile: Optional[str] = None
    