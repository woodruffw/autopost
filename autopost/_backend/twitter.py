from __future__ import annotations

from typing import TYPE_CHECKING

from result import Err, Result

from autopost._backend.interface import Backend, Url

if TYPE_CHECKING:
    from autopost._config import TwitterConfig


class Twitter(Backend):
    def __init__(self, config: TwitterConfig):
        self._config = config

    def health_check(self) -> Result[None, str]:
        return Err("unimplemented")

    def post(self, content: str, url: str, *, tags: list[str] = []) -> Result[Url, str]:
        return Err("unimplemented")
