from __future__ import annotations

from typing import TYPE_CHECKING

import praw

from autopost._backend.interface import Backend, Failure, Result, Success

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

    def health_check(self) -> Result:
        try:
            self._client.user.me()
            return Success()
        except Exception as e:
            return Failure(reason=str(e))

    def post(
        self, content: str, url: str, *, dry_run: bool = False, tags: list[str] = []
    ) -> Result:
        try:
            subreddit = self._client.subreddit(self._config.subreddit)
            subreddit.submit(content, url=url)
            return Success()
        except Exception as e:
            return Failure(reason=str(e))
