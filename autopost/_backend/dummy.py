from __future__ import annotations

from typing import TYPE_CHECKING

from result import Ok, Result

from autopost._backend.interface import Backend, Url

if TYPE_CHECKING:
    from autopost._config import DummyConfig


class Dummy(Backend):
    def __init__(self, config: DummyConfig):
        self._config = config

    @property
    def name(self) -> str:
        return self._config.name

    def health_check(self) -> Result[None, str]:
        return Ok(None)

    def post(self, content: str, url: str, *, tags: list[str] = []) -> Result[Url, str]:
        print(f"DUMMY ({self.name}): {content=} {url=} {tags=}")
        return Ok(Url(url))
