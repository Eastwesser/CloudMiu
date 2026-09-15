"""Async Leonardo.AI client for text-to-image (drawer mode)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

V2_GENERATE_URL = "https://cloud.leonardo.ai/api/rest/v2/generations"
V1_GENERATION_URL = "https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"


class LeonardoError(Exception):
    """Raised when Leonardo API fails or generation does not complete."""


class LeonardoClient:
    def __init__(
        self,
        api_key: str,
        *,
        model: str = "phoenix-v1.0",
        mode: str = "FAST",
        width: int = 1024,
        height: int = 1024,
        quantity: int = 1,
        poll_attempts: int = 40,
        poll_delay: float = 3.0,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        if not api_key:
            raise LeonardoError("LEONARDO_API_KEY is not configured")
        self._api_key = api_key
        self.model = model
        self.mode = mode
        self.width = width
        self.height = height
        self.quantity = quantity
        self.poll_attempts = poll_attempts
        self.poll_delay = poll_delay
        self._session = session
        self._owns_session = session is None

    def _headers(self) -> dict[str, str]:
        return {
            "accept": "application/json",
            "authorization": f"Bearer {self._api_key}",
            "content-type": "application/json",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def aclose(self) -> None:
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def create_generation(self, prompt: str) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "public": False,
            "parameters": {
                "prompt": prompt[:2000],
                "quantity": self.quantity,
                "width": self.width,
                "height": self.height,
                "mode": self.mode,
            },
        }
        session = await self._get_session()
        async with session.post(
            V2_GENERATE_URL,
            headers=self._headers(),
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise LeonardoError(f"create failed HTTP {resp.status}: {body[:400]}")
            data = await resp.json(content_type=None)

        generation_id = data.get("generationId") or (
            data.get("sdGenerationJob") or {}
        ).get("generationId")
        if not generation_id:
            raise LeonardoError(f"no generationId in response: {data!r}")
        return generation_id

    async def get_generation(self, generation_id: str) -> dict[str, Any]:
        session = await self._get_session()
        url = V1_GENERATION_URL.format(generation_id=generation_id)
        async with session.get(
            url,
            headers=self._headers(),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise LeonardoError(f"get failed HTTP {resp.status}: {body[:400]}")
            return await resp.json(content_type=None)

    @staticmethod
    def _extract_status_and_urls(payload: dict[str, Any]) -> tuple[str | None, list[str]]:
        gen = payload.get("generations_by_pk") or payload.get("generation") or payload
        status = gen.get("status") if isinstance(gen, dict) else None
        images: list = []
        if isinstance(gen, dict):
            images = gen.get("generated_images") or gen.get("images") or []
        urls: list[str] = []
        for item in images:
            if isinstance(item, dict) and item.get("url"):
                urls.append(item["url"])
            elif isinstance(item, str):
                urls.append(item)
        return status, urls

    async def wait_for_images(self, generation_id: str) -> list[str]:
        last_status: str | None = None
        for attempt in range(self.poll_attempts):
            payload = await self.get_generation(generation_id)
            status, urls = self._extract_status_and_urls(payload)
            last_status = status
            if urls:
                return urls
            if status in {"FAILED", "FAILED_FINAL", "CANCELLED"}:
                raise LeonardoError(f"generation {generation_id} failed: {status}")
            logger.info(
                "Leonardo generation %s status=%s attempt=%s/%s",
                generation_id,
                status,
                attempt + 1,
                self.poll_attempts,
            )
            await asyncio.sleep(self.poll_delay)
        raise LeonardoError(
            f"generation {generation_id} timed out (last status={last_status})"
        )

    async def text_to_image(self, prompt: str) -> list[str]:
        generation_id = await self.create_generation(prompt)
        return await self.wait_for_images(generation_id)

    async def download_bytes(self, url: str) -> bytes:
        session = await self._get_session()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            if resp.status >= 400:
                raise LeonardoError(f"download failed HTTP {resp.status}")
            return await resp.read()
