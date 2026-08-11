from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NewType

from result import Result

Url = NewType("Url", str)


class Backend(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Result:
        raise NotImplementedError

    @abstractmethod
    def post(self, content: str, url: str, *, tags: list[str] = []) -> Result[Url, str]:
        raise NotImplementedError
