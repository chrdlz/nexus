# Parse command line and save command and options in variables

# if command == "init":
#   try:
#       workspace_data = init_workspace(name=.., description=.., version=..)
#       print success & workspace data
#       exit(0)
#   except ManifestAlreadyExistsError:
#       print "Manifest already exists."
#       load and show manifest
#       exit(1)
#
# if command == "status":
#     try:
#         workspace_data = load_workspace()
#         print formatted status from workspace_data
#         exit(0)
#     except ManifestNotFoundError:
#         print "Manifest not found. This is not a repository."
#         exit(1)

import argparse
from pathlib import Path
from pprint import pprint
import sys

from .workspace import init_workspace, load_workspace, ManifestAlreadyExistsError, ManifestNotFoundError

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
            print("Workspace manifest created successfully:")
            pprint.pprint(manifest)
            sys.exit(0)

        except ManifestAlreadyExistsError:
            print("Manifest.yaml already exists in current directory.")
            try:
                existing = load_workspace(directory=workspace_dir)
                print("Existing manifest.")
                pprint.pprint(existing)
            except ManifestNotFoundError:
                print("Warning: manifest was expected but has not been found.")
                sys.exit(1)

    elif args.cmd == "status":
        try:
            manifest = load_workspace(directory=workspace_dir)
            print("Workspace status:")
            pprint.pprint(manifest)
            sys.exit(0)
        except ManifestNotFoundError:
            print("Error: manifest.yaml not found in this directory. Is this a workspace?")
            sys.exit(1)


if __name__=="__main__":
    main()