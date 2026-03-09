# Exceptions:
# - ManifestAlreadyExistsError
# - ManifestNotFoundError

# def get_manifest_path(directoy=None) -> Path:
#     """Return path to manifest.yaml in directory (default: current working directory)."""

# def manifest_exists(directory=None) -> bool:
#     """Check if manifest exists in directory (default: current working directory)."""

# def init_workspace(name, description=None, version=None, directory=None, ) -> dict:
#     """Creates a new workspace manifest.
#     Raises ManifestAlreadyExistsError if manifest already exists.
#     Returns dict with workspace data (name, creates_at, description, version)."""

# def load_workspace(directory=None) -> dict:
#     """Load existing workspace manifest.
#       Raises ManifestNotFoundError if manifest doesn't exist (=manifest is not found).
#       Returns dict with workspace data:
#       {
#           name : ..
#           description: ..
#           created_at: ..
#           version: ..
#       }"""


from pathlib import Path
from typing import Dict
import yaml
import datetime

# Exceptions

class ManifestAlreadyExistsError(Exception):
    pass

class ManifestNotFoundError(Exception):
    pass

# Manifest filename
MANIFEST_FILENAME = "manifest.yaml"
DEFAULT_DESCRIPTION = "Manifest created without description."
DEFAULT_VERSION = "0.1.0"


# Helper functions

def get_manifest_path(directory=None) -> Path:
    if directory is None: 
        return Path.cwd() / MANIFEST_FILENAME

    directory_path = Path(directory)
    manifest_path = directory_path / MANIFEST_FILENAME # manifest in the root by design
    return manifest_path


def manifest_exists(directory=None) -> bool:
    manifest_path = get_manifest_path(directory)
    return manifest_path.exists()


def init_workspace(name, description=DEFAULT_DESCRIPTION, version=DEFAULT_VERSION, directory=None) -> dict:
    if directory is None:
        directory = Path.cwd()
    
    if manifest_exists(directory):
        raise ManifestAlreadyExistsError 
    
    manifest_path = get_manifest_path(directory)
    data = {
        "name": name,
        "description": description,
        "created_at": str(datetime.datetime.now(datetime.timezone.utc)).split('.')[0],
        "version": version
    }
    manifest_path.write_text(yaml.safe_dump(data, sort_keys=False))
    return data

def load_workspace(directory=None) -> dict:
    if not manifest_exists(directory):
        raise ManifestNotFoundError
    manifest_path = get_manifest_path(directory)
    data = yaml.safe_load(manifest_path.read_text())
    return data

