"""Pollinations.AI — free image API, no key required.

Docs: https://github.com/pollinations/pollinations/blob/master/APIDOCS.md
GET https://image.pollinations.ai/prompt/{prompt}?width=&height=&model=&nologo=
Anonymous ~1 req / 15s; free signup at auth.pollinations.ai raises limits.
"""

from __future__ import annotations

from urllib.parse import quote

import aiohttp

from .base import DrawerError, DrawResult, ImageDrawer

DEFAULT_BASE = "https://image.pollinations.ai"


class PollinationsDrawer(ImageDrawer):
    name = "pollinations"

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE,
        model: str = "flux",
        width: int = 768,
        height: int = 768,
        nologo: bool = True,
        api_token: str = "",
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE).rstrip("/")
        self.model = model
        self.width = width
        self.height = height
        self.nologo = nologo
        self.api_token = api_token
        self._session = session
        self._owns_session = session is None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def aclose(self) -> None:
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    def _build_url(self, prompt: str) -> str:
        encoded = quote(prompt[:500], safe="")
        url = (
            f"{self.base_url}/prompt/{encoded}"
            f"?width={self.width}&height={self.height}"
            f"&model={quote(self.model)}"
            f"&nologo={'true' if self.nologo else 'false'}"
            f"&private=true"
        )
        return url

    async def draw(self, prompt: str) -> DrawResult:
        session = await self._get_session()
        url = self._build_url(prompt)
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        try:
            async with session.get(
                url,
                headers=headers or None,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status >= 400:
                    body = await resp.text()
                    raise DrawerError(
                        f"Pollinations HTTP {resp.status}: {body[:300]}"
                    )
                data = await resp.read()
                if not data or len(data) < 100:
                    raise DrawerError("Pollinations returned empty image")
        except aiohttp.ClientError as exc:
            raise DrawerError(f"Pollinations network error: {exc}") from exc

        return DrawResult(
            image_bytes=data,
            caption_prefix=f"[Pollinations/{self.model}]",
            provider=self.name,
        )
