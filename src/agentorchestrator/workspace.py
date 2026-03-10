from nt import mkdir
from pathlib import Path
import yaml
import datetime
from dataclasses import asdict, dataclass


# Manifest filename
MANIFEST_FILENAME = "manifest.yaml"
DEFAULT_DESCRIPTION = "Manifest created without description."
DEFAULT_VERSION = "0.1.0"


@dataclass
class Workspace:
    name: str
    created_at: str
    description: str = DEFAULT_DESCRIPTION
    version: str = DEFAULT_VERSION

    @classmethod
    def from_dict(cls, d: dict) -> "Workspace":
        """Build Workspace from dict."""
        return cls(
            name=d["name"],
            description=d.get("description", DEFAULT_DESCRIPTION),
            created_at=d["created_at"],
            version=d.get("version", DEFAULT_DESCRIPTION)
        )

    def to_dict(self) -> dict:
        """Converts Workspace into dict for yaml.safe_dump."""
        return asdict(self)


# Exceptions
class ManifestAlreadyExistsError(Exception): pass
class ManifestNotFoundError(Exception): pass


# Helper functions
def get_manifest_path(directory=None) -> Path:
    if directory is None: 
        return Path.cwd() / MANIFEST_FILENAME

    directory_path = Path(directory)
    manifest_path = directory_path / MANIFEST_FILENAME # manifest in the root by design
    return manifest_path


def manifest_exists(directory=None) -> bool:
    """Check if manifest.yaml exist in provided directory or in cwd by default.
    Returns [bool]"""
    manifest_path = get_manifest_path(directory)
    return manifest_path.exists()


def init_workspace(
    name: str,
    description: str | None = None,
    version: str | None = None,
    directory: str | None = None) -> Workspace:
    """Initialize workspace.  Checks if workspace.yaml exists in provided directory or in cwd.
    If already exists, raises ManifestAlreadyExistsError.
    
    Output: [Workspace]"""

    # Deal with empty fields
    if description is None: description = DEFAULT_DESCRIPTION
    if version is None: version = DEFAULT_VERSION
    if directory is None: directory = Path.cwd()
    
    # Check if manifest already exists
    if manifest_exists(directory): raise ManifestAlreadyExistsError 
    
    # Create manifest
    manifest_path = get_manifest_path(directory)
    w = Workspace(
        name=name,
        description=description,
        created_at= str(datetime.datetime.now(datetime.timezone.utc)).split('.')[0],
        version=version
        )

    manifest_path.write_text(yaml.safe_dump(w.to_dict(), sort_keys=False))

    # Check existance of .coral/runs & .coral/logs
    coral_path = directory / ".coral"
    coral_runs_path = coral_path / "runs"
    coral_logs_path = coral_path / "logs"

    coral_path.mkdir(parents=True, exist_ok=True)
    coral_runs_path.mkdir(parents=True, exist_ok=True)
    coral_logs_path.mkdir(parents=True, exist_ok=True)

    return w

def load_workspace(directory=None) -> Workspace:
    """Load workspace manifest.  Checks if workspace.yaml exists in provided directory or in cwd.
    If manifest is not found, raises ManifestNotFoundError.

    Output: [Workspace]"""

    # if manifest not exists raise error
    if not manifest_exists(directory): raise ManifestNotFoundError

    # if manifest exists retrieve data
    manifest_path = get_manifest_path(directory)
    data = yaml.safe_load(manifest_path.read_text())
    return Workspace.from_dict(data)

