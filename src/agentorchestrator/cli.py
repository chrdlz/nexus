import argparse
from pathlib import Path
from pprint import pprint
import sys
from .workspace import init_workspace, load_workspace, ManifestAlreadyExistsError, ManifestNotFoundError

MSG_WS_INIT_SUCCESS = "Workspace manifest created successfully"
MSG_MANIFEST_ALREADY_EXISTS = "Manifest.yaml already exists in current directory."
MSG_MANIFEST_EXISTS = "Existing manifest."
MSG_MANIFEST_EXPECTED_BUT_NOT_FOUND = "Warning: manifest was expected but has not been found."
MSG_MANIFEST_NOT_FOUND = "Error: manifest.yaml not found in this directory. Is this a workspace?"

def parse_args() -> argparse.Namespace:

    # Parser
    parser = argparse.ArgumentParser(
        prog="agentorchestrator",
        description="Workspace CLI parser."
    )

    parser.add_argument(
        "-C",
        "--directory",
        type=str,
        default=None,
        help="Workspace directory (default to current working directory)."
    )

    subparser = parser.add_subparsers(dest='cmd', required=True)
    init_parser = subparser.add_parser('init', help="Initialise workspace.")

    # Required
    init_parser.add_argument(
        'name',
        type=str,
        help='[required] Workspace name'
    )

    # Optional
    init_parser.add_argument(
        '-d',
        '--description',
        default=None,
        help="Workspace description. Please make a short summary of the intent and project in this workspace."
    )

    # Optional
    init_parser.add_argument(
        '-v',
        '--version',
        default=None,
        help="Workspace version."
    )

    status_parser = subparser.add_parser('status', help="Show workspace status.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    workspace_dir = Path(args.directory) if args.directory is not None else Path.cwd()

    if args.cmd == "init":
        try:
            manifest = init_workspace(
                args.name,
                args.description,
                args.version,
                directory=workspace_dir
            )
            print(MSG_WS_INIT_SUCCESS + ":")
            pprint(manifest.to_dict())
            sys.exit(0)

        except ManifestAlreadyExistsError:
            print(MSG_MANIFEST_ALREADY_EXISTS)
            try:
                existing = load_workspace(directory=workspace_dir)
                print(MSG_MANIFEST_EXISTS)
                pprint(existing.to_dict())
            except ManifestNotFoundError:
                print(MSG_MANIFEST_EXPECTED_BUT_NOT_FOUND)
                sys.exit(1)

    elif args.cmd == "status":
        try:
            manifest = load_workspace(directory=workspace_dir)
            print("Workspace status:")
            pprint(manifest.to_dict())
            sys.exit(0)
        except ManifestNotFoundError:
            print(MSG_MANIFEST_NOT_FOUND)
            sys.exit(1)


if __name__=="__main__":
    main()