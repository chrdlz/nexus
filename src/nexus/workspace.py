"""Workspace manifest handling: load, create, and validate workspace configuration.

This module manages the manifest.yaml file that defines a workspace (name,
description, version, created_at) and ensures the expected directory layout
(.nexus/runs, .nexus/logs) exists after initialization.
"""
from pathlib import Path
import yaml
import datetime
from dataclasses import asdict, dataclass


# ---------------------------------------------------------------------------
# Manifest constants (filename and defaults)
# ---------------------------------------------------------------------------
MANIFEST_FILENAME = "manifest.yaml"
DEFAULT_DESCRIPTION = "Manifest created without description."
DEFAULT_VERSION = "0.1.0"


@dataclass
class Workspace:
    """Workspace metadata loaded from or written to manifest.yaml."""

    name: str
    created_at: str
    description: str = DEFAULT_DESCRIPTION
    version: str = DEFAULT_VERSION

    @classmethod
    def from_dict(cls, d: dict) -> "Workspace":
        """Build a Workspace instance from a dictionary (e.g. from YAML).

        Parameters
        ----------
        d : dict
            Must contain "name" and "created_at". "description" and "version"
            are optional and default to module defaults.

        Returns
        -------
        Workspace
            Populated workspace instance.
        """
        return cls(
            name=d["name"],
            description=d.get("description", DEFAULT_DESCRIPTION),
            created_at=d["created_at"],
            version=d.get("version", DEFAULT_VERSION)
        )

    def to_dict(self) -> dict:
        """Convert workspace to a dict suitable for yaml.safe_dump.

        Returns
        -------
        dict
            All fields as key-value pairs (e.g. for serialization).
        """
        return asdict(self)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class ManifestAlreadyExistsError(Exception):
    """Raised when initializing a workspace in a directory that already has a manifest."""

    pass


class ManifestNotFoundError(Exception):
    """Raised when a manifest is required but not found in the given directory."""

    pass


# ---------------------------------------------------------------------------
# Path and existence helpers
# ---------------------------------------------------------------------------
def get_manifest_path(directory=None) -> Path:
    """Return the path to manifest.yaml for the given directory or cwd.

    Parameters
    ----------
    directory : path-like or None, optional
        Workspace directory. If None, uses current working directory.

    Returns
    -------
    Path
        Path to manifest.yaml (manifest is always at workspace root by design).
    """
    if directory is None:
        return Path.cwd() / MANIFEST_FILENAME

    directory_path = Path(directory)
    manifest_path = directory_path / MANIFEST_FILENAME
    return manifest_path


def manifest_exists(directory=None) -> bool:
    """Return True if manifest.yaml exists in the given directory or cwd.

    Parameters
    ----------
    directory : path-like or None, optional
        Workspace directory. If None, uses current working directory.

    Returns
    -------
    bool
        True if manifest file exists, False otherwise.
    """
    manifest_path = get_manifest_path(directory)
    return manifest_path.exists()


def init_workspace(
    name: str,
    description: str | None = None,
    version: str | None = None,
    directory: str | None = None,
) -> Workspace:
    """Create a new workspace: write manifest.yaml and ensure .nexus layout.

    Creates manifest.yaml in the given directory (or cwd) and creates
    .nexus/runs and .nexus/logs if they do not exist.

    Parameters
    ----------
    name : str
        Workspace name (required).
    description : str or None, optional
        Short summary of the workspace. Defaults to DEFAULT_DESCRIPTION.
    version : str or None, optional
        Version string. Defaults to DEFAULT_VERSION.
    directory : str or path-like or None, optional
        Directory in which to create the workspace. Defaults to cwd.

    Returns
    -------
    Workspace
        The created workspace instance.

    Raises
    ------
    ManifestAlreadyExistsError
        If manifest.yaml already exists in the directory.
    """
    if description is None:
        description = DEFAULT_DESCRIPTION
    if version is None:
        version = DEFAULT_VERSION
    if directory is None:
        directory = Path.cwd()
    else:
        directory = Path(directory)

    if manifest_exists(directory):
        raise ManifestAlreadyExistsError

    manifest_path = get_manifest_path(directory)
    w = Workspace(
        name=name,
        description=description,
        created_at=str(datetime.datetime.now(datetime.timezone.utc)).split(".")[0],
        version=version,
    )

    manifest_path.write_text(yaml.safe_dump(w.to_dict(), sort_keys=False))

    # Ensure .nexus/runs and .nexus/logs exist for run and log storage
    nexus_path = directory / ".nexus"
    nexus_runs_path = nexus_path / "runs"
    nexus_logs_path = nexus_path / "logs"

    nexus_path.mkdir(parents=True, exist_ok=True)
    nexus_runs_path.mkdir(parents=True, exist_ok=True)
    nexus_logs_path.mkdir(parents=True, exist_ok=True)

    return w


def load_workspace(directory=None) -> Workspace:
    """Load and parse manifest.yaml from the given directory or cwd.

    Parameters
    ----------
    directory : path-like or None, optional
        Workspace directory. If None, uses current working directory.

    Returns
    -------
    Workspace
        Loaded workspace instance.

    Raises
    ------
    ManifestNotFoundError
        If manifest.yaml does not exist in the directory.
    """
    if not manifest_exists(directory):
        raise ManifestNotFoundError

    manifest_path = get_manifest_path(directory)
    data = yaml.safe_load(manifest_path.read_text())
    return Workspace.from_dict(data)
