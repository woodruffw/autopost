from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

from mastodon import Mastodon as MastodonClient

from autopost._backend.interface import Backend, Failure, Result, Success

if TYPE_CHECKING:
    from autopost._config import MastodonConfig


class Mastodon(Backend):
    def __init__(self, config: MastodonConfig):
        self._config = config
        self._client = MastodonClient(
            api_base_url=self._config.server,
            client_id=self._config.client_key.get_secret_value(),
            client_secret=self._config.client_secret.get_secret_value(),
            access_token=self._config.access_token.get_secret_value(),
        )

    def health_check(self) -> Result:
        try:
            # TODO(ww): Use this once a new version of Mastodon.py is released.
            # See: https://github.com/halcy/Mastodon.py/issues/258
            ok = self._client.instance_health()
            if ok:
                return Success()
            return Failure(reason=f"{self._config.server} failed instance health check")
        except Exception as e:
            return Failure(reason=str(e))

    def post(
        self, content: str, url: str | None, *, dry_run: bool = False, tags: list[str] = []
    ) -> Result:
        tags = [f"#{tag}" for tag in tags]

        if url:
            status = dedent(
                f"""
                {content}

                {url}

                {' '.join(tags)}
                """
            )
        else:
            status = dedent(
                f"""
                {content}

                {' '.join(tags)}
                """
            )

        try:
            # TODO: check response here to confirm the post was actually made.
            _ = self._client.status_post(status)
            return Success()
        except Exception as e:
            return Failure(reason=str(e))
