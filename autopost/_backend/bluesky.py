from textwrap import dedent
from typing import TYPE_CHECKING

from result import Err, Ok, Result

from autopost._backend.interface import Backend, Url

if TYPE_CHECKING:
    from autopost._config import BlueskyConfig


class Bluesky(Backend):
    def __init__(self, config: BlueskyConfig):
        self._config = config

    @property
    def name(self) -> str:
        return self._config.name

    def health_check(self) -> Result[None, str]:
        try:
            ok = self._client.instance_health()
            if ok:
                return Ok(None)
            return Err(f"{self._config.server} failed instance health check")
        except Exception as e:
            return Err(str(e))

    def post(self, content: str, url: str, *, tags: list[str] = []) -> Result[Url, str]:
        tags = [f"#{tag}" for tag in tags]

        status = dedent(
            f"""
            {content}

            {url}

            {' '.join(tags)}
            """
        )

        try:
            resp = self._client.status_post(status)
            return Ok(Url(resp["url"]))
        except Exception as e:
            return Err(str(e))
