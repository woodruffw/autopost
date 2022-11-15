from __future__ import annotations

from typing import TYPE_CHECKING

from autopost._backend.interface import Backend, Failure, Result, Success

if TYPE_CHECKING:
    from autopost._config import TwitterConfig


class Twitter(Backend):
    def __init__(self, config: TwitterConfig):
        self._config = config

    def health_check(self) -> Result:
        return Success()

    def post(
        self, content: str, url: str, *, dry_run: bool = False, tags: list[str] = []
    ) -> Result:
        return Failure(reason="unimplemented")
