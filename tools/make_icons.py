#!/usr/bin/env python3
"""Generate the PWA icons (no third-party deps — writes PNGs by hand).

    python3 tools/make_icons.py
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "app"

BG = (15, 17, 21, 255)      # --bg
FG = (163, 230, 53, 255)    # --accent

# --------------------------------------------------------------------------
# The mark: a lifter in the deadlift setup position, front on. Read as a
# letter "A" with the barbell doing double duty as the crossbar —
#
#            head            apex
#          /      \          <- arms   (upper diagonals)
#   ==============================    <- barbell (crossbar)
#        /          \        <- legs   (lower diagonals)
#      foot        foot      base
#
# All geometry is normalised 0..1 with y running downwards, so the same
# numbers produce a clean icon at any size.
# --------------------------------------------------------------------------


class Canvas:
    """Tiny software rasteriser: enough to compose a silhouette."""

    def __init__(self, size: int, background: tuple[int, int, int, int]) -> None:
        self.size = size
        self.buf = bytearray(bytes(background) * size * size)

    def _put(self, x: int, y: int, color: tuple[int, int, int, int]) -> None:
        if 0 <= x < self.size and 0 <= y < self.size:
            i = (y * self.size + x) * 4
            self.buf[i : i + 4] = bytes(color)

    def disc(self, cx: float, cy: float, radius: float, color) -> None:
        cx, cy, r = cx * self.size, cy * self.size, radius * self.size
        r2 = r * r
        for y in range(max(0, int(cy - r) - 1), min(self.size, int(cy + r) + 2)):
            dy = y + 0.5 - cy
            if abs(dy) > r:
                continue
            for x in range(max(0, int(cx - r) - 1), min(self.size, int(cx + r) + 2)):
                dx = x + 0.5 - cx
                if dx * dx + dy * dy <= r2:
                    self._put(x, y, color)

    def capsule(self, p0, p1, thickness: float, color) -> None:
        """Thick line segment with rounded ends — a limb."""
        x0, y0 = p0[0] * self.size, p0[1] * self.size
        x1, y1 = p1[0] * self.size, p1[1] * self.size
        r = thickness * self.size / 2
        vx, vy = x1 - x0, y1 - y0
        length2 = vx * vx + vy * vy

        for y in range(max(0, int(min(y0, y1) - r) - 1), min(self.size, int(max(y0, y1) + r) + 2)):
            for x in range(max(0, int(min(x0, x1) - r) - 1), min(self.size, int(max(x0, x1) + r) + 2)):
                px, py = x + 0.5 - x0, y + 0.5 - y0
                t = 0.0 if length2 == 0 else max(0.0, min(1.0, (px * vx + py * vy) / length2))
                dx, dy = px - t * vx, py - t * vy
                if dx * dx + dy * dy <= r * r:
                    self._put(x, y, color)


def draw_mark(canvas: Canvas, color) -> None:
    """Front-on deadlift setup. Arms and legs splay outward; the barbell is the crossbar."""
    bar_y = 0.625

    canvas.capsule((0.472, 0.487), (0.228, 0.918), 0.068, color)   # left leg
    canvas.capsule((0.528, 0.487), (0.772, 0.918), 0.068, color)   # right leg

    canvas.capsule((0.446, 0.262), (0.246, 0.602), 0.050, color)   # left arm
    canvas.capsule((0.554, 0.262), (0.754, 0.602), 0.050, color)   # right arm

    canvas.capsule((0.500, 0.240), (0.500, 0.465), 0.108, color)   # torso
    canvas.capsule((0.437, 0.253), (0.563, 0.253), 0.062, color)   # shoulders
    canvas.capsule((0.500, 0.180), (0.500, 0.215), 0.050, color)   # neck
    canvas.disc(0.500, 0.130, 0.062, color)                        # head

    # barbell = the crossbar of the A
    canvas.capsule((0.128, bar_y), (0.872, bar_y), 0.044, color)
    canvas.capsule((0.128, bar_y - 0.042), (0.128, bar_y + 0.042), 0.030, color)  # left collar
    canvas.capsule((0.872, bar_y - 0.042), (0.872, bar_y + 0.042), 0.030, color)  # right collar


def build_pixels(size: int) -> bytearray:
    canvas = Canvas(size, BG)
    draw_mark(canvas, FG)
    return canvas.buf


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
    try:
        shown = path.relative_to(APP_DIR.parent)
    except ValueError:  # rendered to somewhere outside the project
        shown = path
    print(f"{shown}  {size}x{size}  {len(png) / 1024:.1f} KB")


def main() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    write_png(APP_DIR / "icon-180.png", 180)  # apple-touch-icon
    write_png(APP_DIR / "icon-192.png", 192)
    write_png(APP_DIR / "icon-512.png", 512)


if __name__ == "__main__":
    main()
