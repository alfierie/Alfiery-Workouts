#!/usr/bin/env python3
"""Generate the PWA icons (no third-party deps — writes PNGs by hand).

    python3 tools/make_icons.py
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "app"

BG = (15, 17, 21, 255)      # --bg
FG = (163, 230, 53, 255)    # --accent


def build_pixels(size: int) -> bytearray:
    """A dark square with a flat dumbbell silhouette, drawn as raw RGBA."""
    pixels = bytearray(bytes(BG) * size * size)

    def rect(x0: float, y0: float, x1: float, y1: float) -> None:
        for y in range(max(0, int(y0 * size)), min(size, int(y1 * size))):
            row = y * size * 4
            for x in range(max(0, int(x0 * size)), min(size, int(x1 * size))):
                pixels[row + x * 4 : row + x * 4 + 4] = bytes(FG)

    rect(0.29, 0.455, 0.71, 0.545)   # bar
    rect(0.165, 0.295, 0.275, 0.705)  # left outer plate
    rect(0.725, 0.295, 0.835, 0.705)  # right outer plate
    rect(0.305, 0.355, 0.375, 0.645)  # left inner plate
    rect(0.625, 0.355, 0.695, 0.645)  # right inner plate
    return pixels


def write_png(path: Path, size: int) -> None:
    pixels = build_pixels(size)
    stride = size * 4
    raw = b"".join(b"\x00" + bytes(pixels[y * stride : (y + 1) * stride]) for y in range(size))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)
    print(f"{path.relative_to(APP_DIR.parent)}  {size}x{size}  {len(png) / 1024:.1f} KB")


def main() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    write_png(APP_DIR / "icon-180.png", 180)  # apple-touch-icon
    write_png(APP_DIR / "icon-192.png", 192)
    write_png(APP_DIR / "icon-512.png", 512)


if __name__ == "__main__":
    main()
