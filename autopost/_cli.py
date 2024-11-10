import argparse
import json
import logging
import os
import sys
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import feedparser
from result import Err, Ok
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
    parser.add_argument("--json", action="store_true", help="write output as JSON")

    subcommands = parser.add_subparsers(dest="subcommand", required=True)

    manual = subcommands.add_parser(
        "manual",
        help="auto-post manually",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    manual.add_argument(
        "--url", metavar="URL", help="the URL to include in the post", required=True
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

    atom = subcommands.add_parser(
        "atom",
        help="auto-post from an Atom RSS feed",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    atom.add_argument(
        "url",
        metavar="URL",
        help="the feed's URL",
        type=str,
    )

    return parser


@contextmanager
def _get_post(args: argparse.Namespace) -> Iterator[tuple[str, str, list[str]]]:
    if args.subcommand == "manual":
        yield args.content, args.url, args.tags
    elif args.subcommand == "atom":
        feed = feedparser.parse(args.url)
        if not feed.entries:
            raise ValueError("feed is missing entries")
        latest = feed.entries[0]
        tags = latest.get("tags", [])
        yield latest.title, latest.link, [t["term"] for t in tags]
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
        config = Config.parse_obj(tomllib.load(io))
    logger.debug(f"loaded config: {config}")

    with _get_post(args) as (content, url, tags):
        logger.debug(f"{content=} {url=} {tags=}")

        backends = list(config.backends)
        for backend in backends:
            status = backend.health_check()
            logger.debug(f"health check: {backend}: {status}")
            if not status:
                sys.exit(1)

        if args.dry_run:
            console.print(f"dry run: would have posted {content} with URL: {url} and tags: {tags}")
            sys.exit(0)

        results = []
        for backend in backends:
            status = backend.post(content, url, tags=tags)
            result = {
                "backend": backend.__class__.__name__,
                "name": backend.name,
            }
            match status:
                case Ok(link):
                    console.print(f":tada: {backend.name}: {link}")
                    result["link"] = str(link)
                case Err(msg):
                    console.print(f":skull: {backend.name}: {msg}")
                    result["failure"] = msg
            results.append(result)

    if args.json:
        print(json.dumps(results), file=sys.stdout)
