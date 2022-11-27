import argparse
import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import frontmatter
import tomllib
from rich import traceback
from rich.console import Console
from rich.logging import RichHandler

from autopost import __version__
from autopost._config import Config

_HERE = Path.cwd().resolve()
_DEFAULT_CONFIG = _HERE / "autopost.toml"

console = Console(log_path=False, file=sys.stderr)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("AUTOPOST_LOGLEVEL", "INFO").upper(),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)],
)

traceback.install(show_locals=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autopost",
        description="auto-posts social media updates",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="be more verbose while running"
    )
    parser.add_argument("--dry-run", action="store_true", help="perform a dry-run")
    parser.add_argument(
        "--config-file",
        type=Path,
        help="the file to load for configuration",
        default=Path(os.getenv("AUTOPOST_CONFIG_FILE", _DEFAULT_CONFIG)),
    )
    subcommands = parser.add_subparsers(dest="subcommand", required=True)

    manual = subcommands.add_parser(
        "manual",
        help="auto-post manually",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    manual.add_argument(
        "--url", metavar="URL", help="the URL to include in the post", required=False
    )
    manual.add_argument(
        "--tags",
        metavar="TAGS",
        help="content tags to include in the post",
        required=False,
        nargs="*",
        default=[],
    )
    manual.add_argument("content", metavar="CONTENT", help="the post body")

    jekyll = subcommands.add_parser(
        "jekyll",
        help="auto-post for a Jekyll-based blog",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    jekyll.add_argument(
        "path",
        metavar="PATH",
        help="the blog's root directory",
        type=Path,
        default=_HERE,
        nargs="?",
    )

    return parser


@contextmanager
def _get_post(args: argparse.Namespace) -> Iterator[tuple[str, str, list[str]]]:
    if args.subcommand == "manual":
        yield args.content, args.url, args.tags
    elif args.subcommand == "jekyll":
        if not (args.path / "_config.yml").is_file() or not (args.path / "_posts").is_dir():
            raise ValueError(f"{args.path} does not look like a Jekyll-based blog")

        # Jekyll posts are always prefixed with the date, so the latest post is always
        # the last one (or the first one, reverse-sorted).
        latest_path = sorted((args.path / "_posts").glob("*.md"), reverse=True)[0].resolve()
        post = frontmatter.loads(latest_path.read_text())

        yield post["title"], None, []
    else:
        logger.error("unreachable")
        sys.exit(1)


def main() -> None:
    parser = _parser()
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"parsed arguments: {args}")

    if not args.config_file.is_file():
        parser.error(f"missing config: {args.config_file}")

    with args.config_file.open("rb") as io:
        raw_config = tomllib.load(io)
    config = Config.parse_obj(raw_config)
    logger.debug(f"loaded config: {config}")

    with _get_post(args) as (content, url, tags):
        logger.debug(f"{content=} {url=} {tags=}")

        backends = list(config.backends)
        for backend in backends:
            if not (status := backend.health_check()):
                print(status)
                sys.exit(1)

        # for backend in backends:
        #     backend.post(args.content, args.url, tags=args.tags, dry_run=args.dry_run)
