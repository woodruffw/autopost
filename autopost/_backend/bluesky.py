from __future__ import annotations

import re
import urllib.parse
from textwrap import dedent
from typing import TYPE_CHECKING

from atproto import Client, models
from result import Err, Ok, Result

from autopost._backend.interface import Backend, Url

if TYPE_CHECKING:
    from autopost._config import BlueskyConfig


# Adapted from: https://github.com/MarshalX/atproto/blob/main/examples/advanced_usage/auto_hyperlinks.py
def _extract_url_byte_positions(text: str) -> tuple[str, int, int]:
    encoded_text = text.encode()

    pattern = rb"https?\:\/\/(?:[\w\d-]+\.)*[\w-]+[\.\:]\w+\/?(?:[\/\?\=\&\#\.]?[\w-]+)+\/?"

    matches = re.finditer(pattern, encoded_text)
    url_byte_positions = []
    for match in matches:
        url_bytes = match.group(0)
        url = url_bytes.decode()
        url_byte_positions.append((url, match.start(), match.end()))

    return url_byte_positions


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
        post = dedent(
            f"""
            {content}

            {url}
            """
        )

        url_positions = _extract_url_byte_positions(post)
        facets = [
            models.AppBskyRichtextFacet.Main(
                features=[models.AppBskyRichtextFacet.Link(uri=url)],
                index=models.AppBskyRichtextFacet.ByteSlice(byte_start=start, byte_end=end),
            )
            for (url, start, end) in url_positions
        ]

        try:
            resp = self._client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Data(
                    repo=self._client.me.did,
                    collection=models.ids.AppBskyFeedPost,
                    record=models.AppBskyFeedPost.Main(
                        created_at=self._client.get_current_time_iso(), text=post, facets=facets
                    ),
                )
            )

            # Bluesky returns a ridiculous at:// URI.
            # Mash it into something people actually use. These URIs look something like:
            #
            #   at://did:plc:SOMEJUNK/app.bsky.feed.post/IMPORTANTIDHERE
            #
            # ...where the only part we care about is "IMPORTANTIDHERE".
            post_id = urllib.parse.urlparse(resp.uri).path.split("/")[-1]
            return Ok(f"https://bsky.app/profile/{self._config.username}/post/{post_id}")
        except Exception as e:
            return Err(str(e))
