"""Pluggable text→image drawers (mock / Leonardo / FusionBrain)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DrawResult:
    image_bytes: bytes
    caption_prefix: str = ""
    provider: str = ""


class DrawerError(Exception):
    """Provider failed to produce an image."""


class ImageDrawer(ABC):
    """Swap backends without touching Telegram handlers."""

    name: str

    @abstractmethod
    async def draw(self, prompt: str) -> DrawResult:
        """Return PNG/JPEG bytes for the prompt."""

    async def aclose(self) -> None:
        return None
