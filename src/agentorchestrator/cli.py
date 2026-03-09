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
import pprint
import sys

from .workspace import init_workspace, load_workspace, ManifestAlreadyExistsError, ManifestNotFoundError

def parse_args() -> argparse.Namespace:

    # Parser
    parser = argparse.ArgumentParser(
        prog="agentorchestrator",
        description="Workspace CLI parser."
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
    command = args.cmd
    if command == "init":
        try:
            manifest = init_workspace(args.name, args.description, args.version)
        except ManifestAlreadyExistsError:
            sys.exit(1)
    if command == "status":
        try:
            manifest = load_workspace()
        except ManifestNotFoundError:
            sys.exit(1)
    pprint.pprint(manifest)
    sys.exit(0)


if __name__=="__main__":
    main()