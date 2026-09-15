"""Leonardo.AI drawer adapter."""

from __future__ import annotations

from services.leonardo import LeonardoClient, LeonardoError

from .base import DrawerError, DrawResult, ImageDrawer


class LeonardoDrawer(ImageDrawer):
    name = "leonardo"

    def __init__(self, client: LeonardoClient) -> None:
        self._client = client

    async def draw(self, prompt: str) -> DrawResult:
        try:
            urls = await self._client.text_to_image(prompt)
            if not urls:
                raise DrawerError("Leonardo returned no images")
            data = await self._client.download_bytes(urls[0])
        except LeonardoError as exc:
            raise DrawerError(str(exc)) from exc
        return DrawResult(
            image_bytes=data,
            caption_prefix="[Leonardo]",
            provider=self.name,
        )

    async def aclose(self) -> None:
        await self._client.aclose()
