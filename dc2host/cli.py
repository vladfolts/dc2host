import argparse
from git import Repo
from pathlib import Path

from .helpers import open_in_browser


def main():
    parser = argparse.ArgumentParser(description="VS Code Host")
    subparsers = parser.add_subparsers(
        dest="action", required=True
    )
    open_parser = subparsers.add_parser("open", help=f"open in a web browser")
    open_parser.add_argument("path", type=Path)
    open_parser.add_argument("--line", dest="line", type=int, help="highlight line number in the file")
    open_parser.set_defaults(func=_handle_open)

    result = parser.parse_args()
    result.func(result)


def _handle_open(args):
    file_path: Path = args.path.absolute()
    repo_path = file_path
    if repo_path.is_file():
        repo_path = repo_path.parent
    git = Repo(repo_path)
    open_in_browser(git, file_path.relative_to(git.working_dir), args.line)
