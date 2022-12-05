from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NewType

from result import Result

Url = NewType("Url", str)


class Backend(ABC):
    @abstractmethod
    def health_check(self) -> Result:
        pass

    @abstractmethod
    def post(
        self, content: str, url: str, *, dry_run: bool = False, tags: list[str] = []
    ) -> Result[Url, str]:
        pass
