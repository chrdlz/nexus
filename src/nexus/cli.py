"""CLI entrypoint: argument parsing and command dispatch for Nexus.

Provides the ``nexus`` command with subcommands (e.g. init, status)
and -C/--directory for workspace path. Delegates to workspace and run modules
for actual work.
"""
import argparse
from ast import arg
from pathlib import Path
from pprint import pprint
import sys
import traceback

from yaml import add_path_resolver

from nexus.orchestrator import spawn_agent
from nexus.registry import UnknownAgentError, get_agent
from nexus.run import get_run
from .workspace import (
    init_workspace,
    load_workspace,
    ManifestAlreadyExistsError,
    ManifestNotFoundError,
)

# User-facing messages for init and status commands
MSG_WS_INIT_SUCCESS = "Workspace manifest created successfully"
MSG_MANIFEST_ALREADY_EXISTS = "Manifest.yaml already exists in current directory."
MSG_MANIFEST_EXISTS = "Existing manifest."
MSG_MANIFEST_EXPECTED_BUT_NOT_FOUND = "Warning: manifest was expected but has not been found."
MSG_MANIFEST_NOT_FOUND = "Error: manifest.yaml not found in this directory. Is this a workspace?"

def parse_args() -> argparse.Namespace:
    """Build and parse CLI arguments (global -C and subcommands init, status).

    Returns
    -------
    argparse.Namespace
        Parsed arguments; ``cmd`` is the subcommand name, plus command-specific
        fields (e.g. name, description, version for init).
    """
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="Workspace CLI parser."
    )

    parser.add_argument(
        "-C",
        "--directory",
        type=str,
        default=None,
        help="Workspace directory (default to current working directory)."
    )

    subparser = parser.add_subparsers(dest="cmd", required=True)

    # ----- init workspace parser -----
    init_parser = subparser.add_parser("init", help="Initialise workspace.")

    # init: required positional
    init_parser.add_argument(
        'name',
        type=str,
        help="[required] Workspace name",
    )

    # init: optional
    init_parser.add_argument(
        "-d",
        "--description",
        default=None,
        help="Workspace description. Please make a short summary of the intent and project in this workspace."
    )

    init_parser.add_argument(
        "-v",
        "--version",
        default=None,
        help="Workspace version."
    )

    # ----- Status parser -----
    subparser.add_parser("status", help="Show workspace status.")

    # ----- Agentic parser -----
    run_parser = subparser.add_parser("run")

    run_parser.add_argument(
        'agent',
        type=str,
        help="[required] Agent name"
    )

    run_parser.add_argument(
        "-p",
        '--prompt',
        type=str,
        default=None
    )

    # ----- Runs parser -----
    runs_parser = subparser.add_parser("runs")

    runs_subparser = runs_parser.add_subparsers(dest="cmd_runs", required=True)

    runs_list_parser = runs_subparser.add_parser("list")
    runs_list_opgroup = runs_list_parser.add_mutually_exclusive_group()
    runs_list_opgroup.add_argument(
        "-l",
        "--last",
        action="store_true",
        help="only shows last run"
    )

    runs_list_opgroup.add_argument(
        "-la",
        "--list-all",
        action="store_true",
        help="shows all run"
    )

    runs_show_parser = runs_subparser.add_parser("show")
    runs_show_parser.add_argument(
        "id",
        type=str,
        help="[required] run id"
    )

    return parser.parse_args()


def main() -> None:
    """Parse CLI args, dispatch to init or status, and exit with appropriate code."""
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

    elif args.cmd == "run":
        try:
            agent = get_agent(workspace_dir, args.agent)
            (run, exit_code) = spawn_agent(workspace_dir=workspace_dir, agent=agent, input=args.prompt)
            sys.exit(0)
        except UnknownAgentError as e:
            print(f"{type(e).__name__}: {e}")
            sys.exit(1)

    elif args.cmd == "runs":
        if args.cmd_runs == "list":
            if args.last:
                # list all runs id
                runs_dict = get_run(workspace_dir, "last")

            elif args.list_all:
                # list last run id
                runs_dict = get_run(workspace_dir, "all")

            else:
                # list all runs id
                runs_dict = get_run(workspace_dir, "all")

            pprint(runs_dict)
            sys.exit(0)

        elif args.cmd_runs == "show":
            run_dict = get_run(workspace_dir, "single", args.id)
            pprint(run_dict)
            sys.exit(0)


if __name__=="__main__":
    main()
