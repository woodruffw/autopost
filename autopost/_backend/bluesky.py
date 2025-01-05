from __future__ import annotations

import urllib.parse
from typing import TYPE_CHECKING

from atproto import Client, client_utils
from result import Err, Ok, Result

from autopost._backend.interface import Backend, Url

if TYPE_CHECKING:
    from autopost._config import BlueskyConfig


class Bluesky(Backend):
    def __init__(self, config: BlueskyConfig):
        self._config = config
        self._client = Client()
        self._client.login(self._config.username, self._config.password.get_secret_value())

    @property
    def name(self) -> str:
        return self._config.name

    def health_check(self) -> Result[None, str]:
        if self._client.me is not None:
            return Ok(None)
        else:
            return Err(f"{self._config.name} failed profile health check")

    def post(self, content: str, url: str, *, tags: list[str] = []) -> Result[Url, str]:
        post = client_utils.TextBuilder().text(f"{content}\n").link(url, url)

        if tags:
            post.text("\n")

        for tag in tags:
            post = post.tag(f"#{tag}", tag)
            post.text(" ")

        try:
            resp = self._client.send_post(post)

            # Bluesky returns a ridiculous at:// URI.
            # Mash it into something people actually use. These URIs look something like:
            #
            #   at://did:plc:SOMEJUNK/app.bsky.feed.post/IMPORTANTIDHERE
            #
            # ...where the only part we care about is "IMPORTANTIDHERE".
            post_id = urllib.parse.urlparse(resp.uri).path.split("/")[-1]
            return Ok(Url(f"https://bsky.app/profile/{self._config.username}/post/{post_id}"))
        except Exception as e:
            return Err(str(e))
