#!/usr/bin/env python3
"""Generate the 16x16 textures used by the Mundus Foci KubeJS content.

Pure standard library (no Pillow) so it runs anywhere. Output is deterministic,
so re-running only changes files when this script changes.

    python tools/gen_textures.py
"""
from __future__ import annotations

import random
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "kubejs" / "assets" / "mundusfoci" / "textures"

RGBA = tuple[int, int, int, int]
Grid = list[list[RGBA]]
CLEAR: RGBA = (0, 0, 0, 0)


# --------------------------------------------------------------------------- png
def write_png(path: Path, px: Grid) -> None:
    h, w = len(px), len(px[0])
    raw = b"".join(b"\x00" + b"".join(bytes(c) for c in row) for row in px)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != png:
        path.write_bytes(png)
        print("wrote", path.relative_to(ROOT))


def hexc(s: str, a: int = 255) -> RGBA:
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def shade(c: RGBA, f: float) -> RGBA:
    return (*(max(0, min(255, round(v * f))) for v in c[:3]), c[3])  # type: ignore[return-value]


def from_art(art: list[str], palette: dict[str, RGBA]) -> Grid:
    assert len(art) == 16 and all(len(r) == 16 for r in art), "art must be 16x16"
    return [[palette.get(ch, CLEAR) for ch in row] for row in art]


# ------------------------------------------------------------------------ blocks
HEARTH = [hexc("8a4a36"), hexc("96543d"), hexc("a35f45"), hexc("7d4231"), hexc("b0694c")]
MORTAR = hexc("4a2e25")


def noise_stone(seed: int) -> Grid:
    rnd = random.Random(seed)
    g = [[rnd.choice(HEARTH[:4]) for _ in range(16)] for _ in range(16)]
    # a few lighter flecks and darker pits for texture
    for _ in range(14):
        x, y = rnd.randrange(16), rnd.randrange(16)
        g[y][x] = HEARTH[4]
    for _ in range(10):
        x, y = rnd.randrange(16), rnd.randrange(16)
        g[y][x] = shade(HEARTH[3], 0.85)
    return g


def bricks(seed: int) -> Grid:
    rnd = random.Random(seed)
    g = noise_stone(seed)
    for y in range(16):
        row = y // 4
        offset = 4 if row % 2 else 0
        for x in range(16):
            if y % 4 == 3 or (x + offset) % 8 == 7:
                g[y][x] = MORTAR
            elif y % 4 == 0:  # top highlight on each brick course
                g[y][x] = shade(g[y][x], 1.12)
    for _ in range(6):
        x, y = rnd.randrange(16), rnd.randrange(16)
        if g[y][x] != MORTAR:
            g[y][x] = shade(g[y][x], 0.9)
    return g


def chiseled(seed: int) -> Grid:
    g = noise_stone(seed)
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            g[y][x] = MORTAR
        for (x, y) in ((i, 1), (1, i)):
            if 0 < i < 15:
                g[y][x] = shade(HEARTH[2], 1.15)
        for (x, y) in ((i, 14), (14, i)):
            if 0 < i < 15:
                g[y][x] = shade(HEARTH[3], 0.8)
    flame = [
        "................",
        "................",
        "................",
        "................",
        ".......#........",
        "......##........",
        "......#o#.......",
        ".....#oo#.......",
        ".....#oyo#......",
        "....#oyyo#......",
        "....#oyyo#......",
        ".....#oo#.......",
        "......##........",
        "................",
        "................",
        "................",
    ]
    pal = {"#": MORTAR, "o": shade(HEARTH[4], 1.1), "y": hexc("d98a5a")}
    for y, row in enumerate(flame):
        for x, ch in enumerate(row):
            if ch in pal:
                g[y][x + 1] = pal[ch]
    return g


def lamp() -> Grid:
    frame, frame_hi = hexc("3b3330"), hexc("5a4d47")
    glow = [hexc("ffe4a3"), hexc("ffd27a"), hexc("ffbf5c"), hexc("f5a043")]
    g: Grid = [[CLEAR] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            edge = min(x, y, 15 - x, 15 - y)
            if edge == 0:
                g[y][x] = frame
            elif edge == 1:
                g[y][x] = frame_hi if (x + y) % 2 == 0 else frame
            elif x in (7, 8) or y in (7, 8):
                g[y][x] = frame
            else:
                d = max(abs(x - 7.5), abs(y - 7.5))
                g[y][x] = glow[min(3, int((d - 1.5) / 1.6))]
    return g


# ------------------------------------------------------------------------- items
STEW = from_art(
    [
        "................",
        "................",
        "................",
        "................",
        "....g..c...g....",
        "..wwwwwwwwwwww..",
        ".bsscsoscsogssb.",
        ".bssossscssossb.",
        ".BbsssosssscsbB.",
        "..BbbbbbbbbbbB..",
        "...BbbbbbbbbB...",
        "....BBbbbbBB....",
        "......BBBB......",
        "................",
        "................",
        "................",
    ],
    {
        "w": hexc("c98a4d"),
        "s": hexc("a85a2a"),
        "o": hexc("e08a2c"),
        "c": hexc("e7c27a"),
        "g": hexc("5f9e3a"),
        "b": hexc("8b5a2b"),
        "B": hexc("5c3a1b"),
    },
)

TRAIL_MIX = from_art(
    [
        "................",
        "................",
        "......tTt.......",
        ".....t...t......",
        "......tTt.......",
        ".....LLLLLL.....",
        "....LllllllL....",
        "...LlrlylplL....",
        "...LllnllrlL....",
        "...LlplllynL....",
        "...LllylrllL....",
        "...LlnllpllL....",
        "....LllllllL....",
        ".....LLLLLL.....",
        "................",
        "................",
    ],
    {
        "t": hexc("7a5a3a"),
        "T": hexc("b0884f"),
        "L": hexc("6e5232"),
        "l": hexc("c9a46a"),
        "r": hexc("b02a2a"),
        "y": hexc("e8d27a"),
        "p": hexc("6b3f8f"),
        "n": hexc("8a5a2a"),
    },
)

CHARM = from_art(
    [
        "................",
        "................",
        "....sss..sss....",
        "...sSSs..sSSs...",
        "...sSs....sSs...",
        "...rRr....rRr...",
        "...rRr....rRr...",
        "...rRr....rRr...",
        "...rRRr..rRRr...",
        "....rRRrrRRr....",
        ".....rRRRRr.....",
        "......rrrr......",
        "......cggc......",
        ".......gg.......",
        "......cggc......",
        "................",
    ],
    {
        "r": hexc("7a1f1f"),
        "R": hexc("c23b3b"),
        "s": hexc("6e7378"),
        "S": hexc("c9ced3"),
        "g": hexc("d4af37"),
        "c": hexc("8a6d1e"),
    },
)


def main() -> None:
    write_png(ASSETS / "block" / "hearthstone.png", noise_stone(11))
    write_png(ASSETS / "block" / "hearthstone_bricks.png", bricks(23))
    write_png(ASSETS / "block" / "chiseled_hearthstone.png", chiseled(37))
    write_png(ASSETS / "block" / "hearth_lamp.png", lamp())
    write_png(ASSETS / "item" / "hearth_stew.png", STEW)
    write_png(ASSETS / "item" / "trail_mix.png", TRAIL_MIX)
    write_png(ASSETS / "item" / "lodestone_charm.png", CHARM)


if __name__ == "__main__":
    main()
