"""Offline mock drawer — works under TSPU / no foreign cards / no API."""

from __future__ import annotations

import hashlib
import struct
import zlib

from .base import DrawResult, ImageDrawer


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def render_prompt_png(prompt: str, width: int = 512, height: int = 512) -> bytes:
    """Build a tiny PNG (no Pillow): color field from prompt hash + scanlines."""
    digest = hashlib.sha256(prompt.encode("utf-8", errors="replace")).digest()
    r, g, b = digest[0], digest[1], digest[2]
    # Slight vertical gradient so it doesn't look like a flat error tile
    rows = bytearray()
    for y in range(height):
        rows.append(0)  # filter None
        t = y / max(height - 1, 1)
        rr = int(r * (1 - 0.35 * t) + 40 * t) % 256
        gg = int(g * (1 - 0.25 * t) + 60 * t) % 256
        bb = int(b * (1 - 0.15 * t) + 90 * t) % 256
        # Soft diagonal stripe from hash
        stripe = digest[3 + (y % 13)]
        for x in range(width):
            if (x + y) % 64 < 3:
                rows.extend((min(255, rr + 40), min(255, gg + 40), min(255, bb + 40)))
            elif abs(x - (stripe * 2 % width)) < 2:
                rows.extend((255 - rr, 255 - gg, 255 - bb))
            else:
                rows.extend((rr, gg, bb))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += _chunk(b"IEND", b"")
    return png


class MockDrawer(ImageDrawer):
    name = "mock"

    def __init__(self, width: int = 512, height: int = 512) -> None:
        self.width = width
        self.height = height

    async def draw(self, prompt: str) -> DrawResult:
        data = render_prompt_png(prompt, self.width, self.height)
        return DrawResult(
            image_bytes=data,
            caption_prefix="[mock / offline]",
            provider=self.name,
        )
