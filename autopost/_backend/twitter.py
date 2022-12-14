from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import twitter
from result import Err, Ok, Result

from autopost._backend.interface import Backend, Url

if TYPE_CHECKING:
    from autopost._config import TwitterConfig


class Twitter(Backend):
    def __init__(self, config: TwitterConfig):
        self._config = config
        self._client = twitter.Api(
            consumer_key=self._config.api_key.get_secret_value(),
            consumer_secret=self._config.api_key_secret.get_secret_value(),
            access_token_key=self._config.access_token.get_secret_value(),
            access_token_secret=self._config.access_token_secret.get_secret_value(),
        )

    @property
    def name(self) -> str:
        return self._config.name

    def health_check(self) -> Result[None, str]:
        return Err("unimplemented")

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
            resp = self._client.PostUpdate(status)
            url = f"https://twitter.com/{resp.user.screen_name}/status/{resp.id_str}"
            return Ok(Url(url))
        except Exception as e:
            return Err(str(e))
