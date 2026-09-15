"""Craiyon-compatible drawer (AdTime-shaped or any compatible host).

Official craiyon.com: **no public developer API** (login ≠ API key).
FAQ: https://www.craiyon.com/pricing — "we don't have a public API at the moment".

This client talks to a *compatible* server:
  POST {base}/api/v1/auth/login
  POST {api}/api/v1/generate  {prompt, model_version: craiyon-v3}

Point CRAIYON_BASE_URL at your own generate service when you have one.
Until then use DRAWER_BACKEND=fusionbrain|mock.
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .base import DrawerError, DrawResult, ImageDrawer

logger = logging.getLogger(__name__)


class CraiyonAdTimeDrawer(ImageDrawer):
    name = "craiyon"

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        *,
        model_version: str = "craiyon-v3",
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        if not base_url or not username or not password:
            raise DrawerError("CRAIYON/ADTIME base_url + username + password required")
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.model_version = model_version
        self._token: str | None = None
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

    async def login(self) -> str:
        session = await self._get_session()
        url = f"{self.base_url}/api/v1/auth/login"
        try:
            async with session.post(
                url,
                data={"username": self.username, "password": self.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                body = await resp.text()
                if resp.status >= 400:
                    raise DrawerError(f"Craiyon login HTTP {resp.status}: {body[:300]}")
                data: Any = await resp.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise DrawerError(f"Craiyon login network error: {exc}") from exc

        token = None
        if isinstance(data, dict):
            tok = data.get("token") or {}
            if isinstance(tok, dict):
                token = tok.get("access_token")
            token = token or data.get("access_token")
        if not token:
            raise DrawerError(f"Craiyon login: no access_token in response: {data!r}")
        self._token = str(token)
        return self._token

    async def _ensure_token(self) -> str:
        if self._token:
            return self._token
        return await self.login()

    async def generate(self, prompt: str) -> str:
        session = await self._get_session()
        token = await self._ensure_token()
        url = f"{self.base_url}/api/v1/generate"
        payload = {
            "prompt": prompt[:2000],
            "model_version": self.model_version,
        }
        try:
            async with session.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                body = await resp.text()
                if resp.status == 401:
                    # refresh once
                    self._token = None
                    token = await self.login()
                    async with session.post(
                        url,
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                        },
                        timeout=aiohttp.ClientTimeout(total=120),
                    ) as resp2:
                        body = await resp2.text()
                        if resp2.status >= 400:
                            raise DrawerError(f"Craiyon generate HTTP {resp2.status}: {body[:300]}")
                        data = await resp2.json(content_type=None)
                elif resp.status >= 400:
                    raise DrawerError(f"Craiyon generate HTTP {resp.status}: {body[:300]}")
                else:
                    data = await resp.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise DrawerError(f"Craiyon generate network error: {exc}") from exc

        result_url = data.get("result_url") if isinstance(data, dict) else None
        if not result_url:
            raise DrawerError(f"Craiyon generate: no result_url: {data!r}")
        return str(result_url)

    async def download_bytes(self, url: str) -> bytes:
        session = await self._get_session()
        # result_url may be relative
        if url.startswith("/"):
            url = f"{self.base_url}{url}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status >= 400:
                    raise DrawerError(f"Craiyon download HTTP {resp.status}")
                return await resp.read()
        except aiohttp.ClientError as exc:
            raise DrawerError(f"Craiyon download network error: {exc}") from exc

    async def draw(self, prompt: str) -> DrawResult:
        result_url = await self.generate(prompt)
        data = await self.download_bytes(result_url)
        return DrawResult(
            image_bytes=data,
            caption_prefix=f"[Craiyon {self.model_version}]",
            provider=self.name,
        )
