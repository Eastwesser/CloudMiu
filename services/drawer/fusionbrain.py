"""FusionBrain / Kandinsky drawer — RU-friendly API (api.fusionbrain.ai)."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any

import aiohttp

from .base import DrawerError, DrawResult, ImageDrawer

logger = logging.getLogger(__name__)

API_ROOT = "https://api.fusionbrain.ai/"


class FusionBrainDrawer(ImageDrawer):
    name = "fusionbrain"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        *,
        width: int = 1024,
        height: int = 1024,
        poll_attempts: int = 20,
        poll_delay: float = 3.0,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        if not api_key or not api_secret:
            raise DrawerError("FUSION_BRAIN_TOKEN / FB_KEY not configured")
        self._headers = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {api_secret}",
        }
        self.width = width
        self.height = height
        self.poll_attempts = poll_attempts
        self.poll_delay = poll_delay
        self._session = session
        self._owns_session = session is None

    async def _session_get(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def aclose(self) -> None:
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def _get_model_id(self, session: aiohttp.ClientSession) -> str:
        async with session.get(
            API_ROOT + "key/api/v1/models",
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise DrawerError(f"FusionBrain models HTTP {resp.status}: {body[:300]}")
            data: Any = await resp.json(content_type=None)
        if not data:
            raise DrawerError("FusionBrain returned empty models list")
        return str(data[0]["id"])

    async def _run(self, session: aiohttp.ClientSession, model_id: str, prompt: str) -> str:
        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": self.width,
            "height": self.height,
            "generateParams": {"query": prompt[:1000]},
        }
        form = aiohttp.FormData()
        form.add_field("model_id", model_id)
        form.add_field(
            "params",
            json.dumps(params),
            content_type="application/json",
        )
        async with session.post(
            API_ROOT + "key/api/v1/text2image/run",
            headers=self._headers,
            data=form,
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise DrawerError(f"FusionBrain run HTTP {resp.status}: {body[:300]}")
            data = await resp.json(content_type=None)
        uuid = data.get("uuid")
        if not uuid:
            raise DrawerError(f"FusionBrain no uuid: {data!r}")
        return str(uuid)

    async def _wait_images(self, session: aiohttp.ClientSession, uuid: str) -> list[str]:
        for attempt in range(self.poll_attempts):
            async with session.get(
                API_ROOT + f"key/api/v1/text2image/status/{uuid}",
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                body = await resp.text()
                if resp.status >= 400:
                    raise DrawerError(f"FusionBrain status HTTP {resp.status}: {body[:300]}")
                data = await resp.json(content_type=None)
            status = data.get("status")
            if status == "DONE":
                images = data.get("images") or []
                if not images:
                    raise DrawerError("FusionBrain DONE but no images")
                return images
            if status in {"FAIL", "FAILED", "ERROR"}:
                raise DrawerError(f"FusionBrain generation failed: {status}")
            logger.info(
                "FusionBrain %s status=%s attempt=%s/%s",
                uuid,
                status,
                attempt + 1,
                self.poll_attempts,
            )
            await asyncio.sleep(self.poll_delay)
        raise DrawerError(f"FusionBrain timed out for {uuid}")

    async def draw(self, prompt: str) -> DrawResult:
        session = await self._session_get()
        try:
            model_id = await self._get_model_id(session)
            uuid = await self._run(session, model_id, prompt)
            images_b64 = await self._wait_images(session, uuid)
            raw = base64.b64decode(images_b64[0])
        except aiohttp.ClientError as exc:
            raise DrawerError(f"FusionBrain network error: {exc}") from exc
        return DrawResult(
            image_bytes=raw,
            caption_prefix="[Kandinsky / FusionBrain]",
            provider=self.name,
        )
