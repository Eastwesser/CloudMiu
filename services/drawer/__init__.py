"""Factory + optional fallback to mock when remote APIs die (TSPU / payments)."""

from __future__ import annotations

import logging

from config import Settings

from .base import DrawerError, DrawResult, ImageDrawer
from .craiyon import CraiyonAdTimeDrawer
from .fusionbrain import FusionBrainDrawer
from .leonardo_drawer import LeonardoDrawer
from .mock import MockDrawer
from .pollinations import PollinationsDrawer

logger = logging.getLogger(__name__)


class FallbackDrawer(ImageDrawer):
    """Try primary; on DrawerError use mock so the bot still answers."""

    name = "fallback"

    def __init__(self, primary: ImageDrawer, fallback: ImageDrawer) -> None:
        self._primary = primary
        self._fallback = fallback
        self.name = f"{primary.name}+{fallback.name}"

    async def draw(self, prompt: str) -> DrawResult:
        try:
            return await self._primary.draw(prompt)
        except DrawerError as exc:
            logger.warning(
                "Drawer %s failed (%s); using %s",
                self._primary.name,
                exc,
                self._fallback.name,
            )
            result = await self._fallback.draw(prompt)
            return DrawResult(
                image_bytes=result.image_bytes,
                caption_prefix=f"[fallback→{self._fallback.name}] {result.caption_prefix}",
                provider=self.name,
            )

    async def aclose(self) -> None:
        await self._primary.aclose()
        await self._fallback.aclose()


class ChainDrawer(ImageDrawer):
    """Try drawers in order until one succeeds."""

    name = "chain"

    def __init__(self, drawers: list[ImageDrawer]) -> None:
        if not drawers:
            raise DrawerError("ChainDrawer needs at least one backend")
        self._drawers = drawers
        self.name = "+".join(d.name for d in drawers)

    async def draw(self, prompt: str) -> DrawResult:
        errors: list[str] = []
        for drawer in self._drawers:
            try:
                return await drawer.draw(prompt)
            except DrawerError as exc:
                logger.warning("Chain: %s failed (%s)", drawer.name, exc)
                errors.append(f"{drawer.name}: {exc}")
        raise DrawerError("All drawers failed: " + " | ".join(errors))

    async def aclose(self) -> None:
        for drawer in self._drawers:
            await drawer.aclose()


def _has_craiyon(settings: Settings) -> bool:
    return bool(
        settings.craiyon_base_url
        and settings.craiyon_username
        and settings.craiyon_password
    )


def _make_craiyon(settings: Settings) -> CraiyonAdTimeDrawer:
    return CraiyonAdTimeDrawer(
        settings.craiyon_base_url,
        settings.craiyon_username,
        settings.craiyon_password,
        model_version=settings.craiyon_model_version or "craiyon-v3",
    )


def _make_pollinations(settings: Settings) -> PollinationsDrawer:
    return PollinationsDrawer(
        base_url=settings.pollinations_base_url,
        model=settings.pollinations_model or "flux",
        width=min(settings.leonardo_width, 1024),
        height=min(settings.leonardo_height, 1024),
        api_token=settings.pollinations_token,
    )


def build_drawer(settings: Settings) -> ImageDrawer:
    backend = (settings.drawer_backend or "pollinations").strip().lower()
    mock = MockDrawer(
        width=min(settings.leonardo_width, 512),
        height=min(settings.leonardo_height, 512),
    )

    if backend in {"mock", "offline", "local"}:
        return mock

    if backend in {"pollinations", "poll", "free"}:
        primary: ImageDrawer = _make_pollinations(settings)
    elif backend in {"craiyon", "adtime", "gifty"}:
        if not _has_craiyon(settings):
            logger.warning("Craiyon incomplete — using pollinations")
            primary = _make_pollinations(settings)
        else:
            primary = _make_craiyon(settings)
    elif backend in {"leonardo", "leo"}:
        from services.leonardo import LeonardoClient

        if not settings.leonardo_api_key:
            logger.warning("Leonardo missing — using pollinations")
            primary = _make_pollinations(settings)
        else:
            primary = LeonardoDrawer(
                LeonardoClient(
                    api_key=settings.leonardo_api_key,
                    model=settings.leonardo_model,
                    mode=settings.leonardo_mode,
                    width=settings.leonardo_width,
                    height=settings.leonardo_height,
                )
            )
    elif backend in {"fusionbrain", "kandinsky", "fb"}:
        primary = FusionBrainDrawer(
            settings.fusion_brain_token,
            settings.fb_key,
            width=settings.leonardo_width,
            height=settings.leonardo_height,
        )
    elif backend == "auto":
        chain: list[ImageDrawer] = [_make_pollinations(settings)]
        if settings.fusion_brain_token and settings.fb_key:
            chain.append(
                FusionBrainDrawer(
                    settings.fusion_brain_token,
                    settings.fb_key,
                    width=settings.leonardo_width,
                    height=settings.leonardo_height,
                )
            )
        if _has_craiyon(settings):
            chain.append(_make_craiyon(settings))
        if settings.leonardo_api_key:
            from services.leonardo import LeonardoClient

            chain.append(
                LeonardoDrawer(
                    LeonardoClient(
                        api_key=settings.leonardo_api_key,
                        model=settings.leonardo_model,
                        mode=settings.leonardo_mode,
                        width=settings.leonardo_width,
                        height=settings.leonardo_height,
                    )
                )
            )
        primary = chain[0] if len(chain) == 1 else ChainDrawer(chain)
    else:
        raise DrawerError(
            f"Unknown DRAWER_BACKEND={backend!r} "
            "(use mock|pollinations|fusionbrain|craiyon|leonardo|auto)"
        )

    if settings.drawer_fallback_mock:
        return FallbackDrawer(primary, mock)
    return primary
