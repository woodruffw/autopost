from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class Success:
    def __bool__(self) -> bool:
        return True


@dataclass(frozen=True, slots=True, kw_only=True)
class Failure:
    reason: str

    def __bool__(self) -> bool:
        return False


Result = Success | Failure


class Backend(ABC):
    @abstractmethod
    def health_check(self) -> Result:
        pass

    @abstractmethod
    def post(
        self, content: str, url: str, *, dry_run: bool = False, tags: list[str] = []
    ) -> Result:
        pass
