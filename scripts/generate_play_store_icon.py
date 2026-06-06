#!/usr/bin/env python3
from __future__ import annotations

import struct
import zlib
from pathlib import Path

from check_store_asset_pixels import PngImage, parse_png, pixel_at

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "store-assets" / "app-icon" / "play-store-icon-imagegen-source-04.png"
PLAY_OUTPUT = ROOT / "store-assets" / "app-icon" / "play-store-icon-512.png"

PLAY_SIZE = 512
LEGACY_LAUNCHER_SIZES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}
ADAPTIVE_FOREGROUND_SIZES = {
    "mipmap-mdpi": 108,
    "mipmap-hdpi": 162,
    "mipmap-xhdpi": 216,
    "mipmap-xxhdpi": 324,
    "mipmap-xxxhdpi": 432,
}

Color = tuple[int, int, int, int]


def lerp(left: float, right: float, amount: float) -> float:
    return left * (1.0 - amount) + right * amount


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def source_crop(image: PngImage) -> tuple[int, int, int]:
    crop_size = min(image.width, image.height)
    return (image.width - crop_size) // 2, (image.height - crop_size) // 2, crop_size


def sample_source(image: PngImage, source_x: float, source_y: float) -> Color:
    x0 = max(0, min(image.width - 1, int(source_x)))
    y0 = max(0, min(image.height - 1, int(source_y)))
    x1 = max(0, min(image.width - 1, x0 + 1))
    y1 = max(0, min(image.height - 1, y0 + 1))
    tx = source_x - x0
    ty = source_y - y0

    p00 = pixel_at(image, x0, y0)
    p10 = pixel_at(image, x1, y0)
    p01 = pixel_at(image, x0, y1)
    p11 = pixel_at(image, x1, y1)

    channels: list[int] = []
    for index in range(4):
        p00_channel = p00[index] if p00[index] is not None else 255
        p10_channel = p10[index] if p10[index] is not None else 255
        p01_channel = p01[index] if p01[index] is not None else 255
        p11_channel = p11[index] if p11[index] is not None else 255
        top = lerp(p00_channel, p10_channel, tx)
        bottom = lerp(p01_channel, p11_channel, tx)
        channels.append(clamp(round(lerp(top, bottom, ty)), 0, 255))

    channels[3] = 255
    return tuple(channels)  # type: ignore[return-value]


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, size: int, pixels: list[list[Color]]) -> None:
    raw_rows = bytearray()
    for row in pixels:
        raw_rows.append(0)
        for red, green, blue, alpha in row:
            raw_rows.extend((red, green, blue, alpha))

    path.parent.mkdir(parents=True, exist_ok=True)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(bytes(raw_rows), 9))
    data += chunk(b"IEND", b"")
    path.write_bytes(data)


def resize_square(image: PngImage, size: int) -> list[list[Color]]:
    offset_x, offset_y, crop_size = source_crop(image)
    pixels: list[list[Color]] = []

    scale = crop_size / size
    for y in range(size):
        row: list[Color] = []
        source_y = offset_y + (y + 0.5) * scale - 0.5
        for x in range(size):
            source_x = offset_x + (x + 0.5) * scale - 0.5
            row.append(sample_source(image, source_x, source_y))
        pixels.append(row)
    return pixels


def write_resized(image: PngImage, output: Path, size: int) -> None:
    write_png(output, size, resize_square(image, size))


def write_launcher_assets(image: PngImage) -> list[Path]:
    written: list[Path] = []
    res_dir = ROOT / "app" / "src" / "main" / "res"

    for density, size in LEGACY_LAUNCHER_SIZES.items():
        for filename in ("ic_launcher.png", "ic_launcher_round.png"):
            path = res_dir / density / filename
            write_resized(image, path, size)
            written.append(path)

    for density, size in ADAPTIVE_FOREGROUND_SIZES.items():
        path = res_dir / density / "ic_launcher_foreground.png"
        write_resized(image, path, size)
        written.append(path)

    return written


def main() -> int:
    image = parse_png(SOURCE)

    write_resized(image, PLAY_OUTPUT, PLAY_SIZE)
    launcher_outputs = write_launcher_assets(image)
    print(f"Generated {PLAY_OUTPUT} from {SOURCE}")
    print(f"Generated {len(launcher_outputs)} Android launcher PNG assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
