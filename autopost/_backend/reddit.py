from __future__ import annotations

from typing import TYPE_CHECKING

import praw
from result import Err, Ok, Result

from autopost._backend.interface import Backend, Url

if TYPE_CHECKING:
    from autopost._config import RedditConfig


class Reddit(Backend):
    def __init__(self, config: RedditConfig):
        self._config = config
        self._client = praw.Reddit(
            client_id=self._config.client_id.get_secret_value(),
            client_secret=self._config.client_secret.get_secret_value(),
            password=self._config.password.get_secret_value(),
            username=self._config.username,
            user_agent="autopost by u/yossarian_flew_away",
        )

    @property
    def name(self) -> str:
        return self._config.name

    def health_check(self) -> Result[None, str]:
        try:
            self._client.user.me()
            return Ok(None)
        except Exception as e:
            return Err(str(e))

    def post(self, content: str, url: str, *, tags: list[str] = []) -> Result[Url, str]:
        try:
            subreddit = self._client.subreddit(self._config.subreddit)
            submission = subreddit.submit(content, url=url)
            # `permalink` is formatted as `/r/subreddit/...`
            url = f"https://reddit.com{submission.permalink}"
            return Ok(Url(url))
        except Exception as e:
            return Err(str(e))
