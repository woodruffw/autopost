from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty
from typing import NewType

from result import Result

Url = NewType("Url", str)


class Backend(ABC):
    @abstractproperty
    def name(self) -> str:
        pass

    @abstractmethod
    def health_check(self) -> Result:
        pass

    @abstractmethod
    def post(self, content: str, url: str, *, tags: list[str] = []) -> Result[Url, str]:
        pass
