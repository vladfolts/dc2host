import argparse
from git import Repo
from pathlib import Path

from .helpers import open_in_browser


def main():
    parser = argparse.ArgumentParser(description="VS Code Host")
    subparsers = parser.add_subparsers(dest="action", required=True)
    open_parser = subparsers.add_parser("open", help=f"open in a web browser")
    open_parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        help="path to the file or directory, default is current directory",
    )
    open_parser.add_argument(
        "--line", dest="line", type=int, help="highlight line number in the file"
    )
    open_parser.set_defaults(func=_handle_open)

    result = parser.parse_args()
    result.func(result)


def _handle_open(args: argparse.Namespace):
    file_path: Path = Path(args.path).absolute() if args.path else Path.cwd()
    open_in_browser(file_path, args.line)
