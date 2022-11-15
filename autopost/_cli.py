import argparse
import logging
import os
import sys
from pathlib import Path

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
    parser = argparse.ArgumentParser(prog="autopost", description="auto-posts social media updates")
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
    parser.add_argument(
        "--url", metavar="URL", help="the URL to include in the post", required=False
    )
    parser.add_argument(
        "--tags",
        metavar="TAGS",
        help="content tags to include in the post",
        required=False,
        nargs="*",
        default=[],
    )
    parser.add_argument("content", metavar="CONTENT", help="the post body")

    return parser


def main() -> None:
    parser = _parser()
    args = parser.parse_args()

    logger.debug(f"parsed arguments: {args}")

    if not args.config_file.is_file():
        parser.error(f"missing config: {args.config_file}")

    with args.config_file.open("rb") as io:
        raw_config = tomllib.load(io)
    config = Config.parse_obj(raw_config)
    logger.debug(f"loaded config: {config}")

    backends = list(config.backends)
    for backend in backends:
        if not (status := backend.health_check()):
            print(status)
            sys.exit(1)

    # for backend in backends:
    #     backend.post(args.content, args.url, tags=args.tags, dry_run=args.dry_run)
