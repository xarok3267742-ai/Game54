#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "screenshots" / "play-store"
FEATURE_GRAPHIC = ROOT / "store-assets" / "feature-graphic" / "feature-graphic-candidate-03.png"
PLAY_STORE_ICON = ROOT / "store-assets" / "app-icon" / "play-store-icon-512.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

EXPECTED_SCREENSHOTS = (
    "01-onboarding.png",
    "02-home.png",
    "03-timer.png",
    "04-result.png",
    "05-progress.png",
    "06-settings.png",
)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


@dataclass(frozen=True)
class PngImage:
    path: Path
    width: int
    height: int
    bit_depth: int
    color_type: int
    interlace: int
    pixels: bytes
    channels: int


@dataclass(frozen=True)
class PixelStats:
    unique_sample_colors: int
    min_luminance: int
    max_luminance: int
    average_luminance: int
    alpha_min: int | None
    alpha_max: int | None
    digest: str
    average_hash: int


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def parse_png(path: Path) -> PngImage:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("file is not a PNG")

    offset = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = interlace = None
    idat_parts: list[bytes] = []

    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        offset += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or bit_depth is None or color_type is None or interlace is None:
        raise ValueError("PNG is missing IHDR")
    if not idat_parts:
        raise ValueError("PNG is missing IDAT")
    if bit_depth != 8:
        raise ValueError(f"unsupported bit depth {bit_depth}")
    if color_type not in (2, 6):
        raise ValueError(f"unsupported color type {color_type}")
    if interlace != 0:
        raise ValueError("interlaced PNG is not supported")

    channels = 3 if color_type == 2 else 4
    row_size = width * channels
    decompressed = zlib.decompress(b"".join(idat_parts))
    expected_size = (row_size + 1) * height
    if len(decompressed) != expected_size:
        raise ValueError(f"unexpected decompressed size {len(decompressed)}; expected {expected_size}")

    rows = bytearray(width * height * channels)
    previous = bytearray(row_size)
    source_offset = 0
    target_offset = 0

    for _row in range(height):
        filter_type = decompressed[source_offset]
        source_offset += 1
        current = bytearray(decompressed[source_offset : source_offset + row_size])
        source_offset += row_size

        if filter_type == 0:
            pass
        elif filter_type == 1:
            for index in range(row_size):
                left = current[index - channels] if index >= channels else 0
                current[index] = (current[index] + left) & 0xFF
        elif filter_type == 2:
            for index in range(row_size):
                current[index] = (current[index] + previous[index]) & 0xFF
        elif filter_type == 3:
            for index in range(row_size):
                left = current[index - channels] if index >= channels else 0
                up = previous[index]
                current[index] = (current[index] + ((left + up) // 2)) & 0xFF
        elif filter_type == 4:
            for index in range(row_size):
                left = current[index - channels] if index >= channels else 0
                up = previous[index]
                upper_left = previous[index - channels] if index >= channels else 0
                current[index] = (current[index] + paeth(left, up, upper_left)) & 0xFF
        else:
            raise ValueError(f"unsupported PNG filter type {filter_type}")

        rows[target_offset : target_offset + row_size] = current
        previous = current
        target_offset += row_size

    return PngImage(
        path=path,
        width=width,
        height=height,
        bit_depth=bit_depth,
        color_type=color_type,
        interlace=interlace,
        pixels=bytes(rows),
        channels=channels,
    )


def luminance(red: int, green: int, blue: int) -> int:
    return (red * 299 + green * 587 + blue * 114) // 1000


def pixel_at(image: PngImage, x: int, y: int) -> tuple[int, int, int, int | None]:
    offset = (y * image.width + x) * image.channels
    red = image.pixels[offset]
    green = image.pixels[offset + 1]
    blue = image.pixels[offset + 2]
    alpha = image.pixels[offset + 3] if image.channels == 4 else None
    return red, green, blue, alpha


def average_hash(image: PngImage, grid_size: int = 8) -> int:
    values: list[int] = []
    for cell_y in range(grid_size):
        for cell_x in range(grid_size):
            x_start = (cell_x * image.width) // grid_size
            x_end = ((cell_x + 1) * image.width) // grid_size
            y_start = (cell_y * image.height) // grid_size
            y_end = ((cell_y + 1) * image.height) // grid_size

            total = 0
            count = 0
            step_x = max(1, (x_end - x_start) // 16)
            step_y = max(1, (y_end - y_start) // 16)
            for y in range(y_start, y_end, step_y):
                for x in range(x_start, x_end, step_x):
                    red, green, blue, _alpha = pixel_at(image, x, y)
                    total += luminance(red, green, blue)
                    count += 1
            values.append(total // max(1, count))

    average = sum(values) // len(values)
    result = 0
    for index, value in enumerate(values):
        if value >= average:
            result |= 1 << index
    return result


def collect_stats(image: PngImage) -> PixelStats:
    sample_colors: set[tuple[int, int, int]] = set()
    min_lum = 255
    max_lum = 0
    total_lum = 0
    count = 0
    alpha_min = 255 if image.channels == 4 else None
    alpha_max = 0 if image.channels == 4 else None

    step_x = max(1, image.width // 96)
    step_y = max(1, image.height // 96)
    for y in range(0, image.height, step_y):
        for x in range(0, image.width, step_x):
            red, green, blue, alpha = pixel_at(image, x, y)
            lum = luminance(red, green, blue)
            min_lum = min(min_lum, lum)
            max_lum = max(max_lum, lum)
            total_lum += lum
            count += 1
            sample_colors.add((red, green, blue))
            if alpha is not None:
                assert alpha_min is not None and alpha_max is not None
                alpha_min = min(alpha_min, alpha)
                alpha_max = max(alpha_max, alpha)

    return PixelStats(
        unique_sample_colors=len(sample_colors),
        min_luminance=min_lum,
        max_luminance=max_lum,
        average_luminance=total_lum // max(1, count),
        alpha_min=alpha_min,
        alpha_max=alpha_max,
        digest=hashlib.sha256(image.pixels).hexdigest(),
        average_hash=average_hash(image),
    )


def hamming_distance(left: int, right: int) -> int:
    return bin(left ^ right).count("1")


def validate_image(
    image: PngImage,
    expected_size: tuple[int, int],
    expected_color_type: int,
    failures: list[str],
    min_unique_colors: int = 64,
    min_luminance_range: int = 40,
) -> PixelStats:
    relative = display_path(image.path)
    if (image.width, image.height) != expected_size:
        failures.append(f"{relative} dimensions are {image.width}x{image.height}; expected {expected_size[0]}x{expected_size[1]}")
    if image.bit_depth != 8:
        failures.append(f"{relative} bit depth is {image.bit_depth}; expected 8")
    if image.color_type != expected_color_type:
        failures.append(f"{relative} color type is {image.color_type}; expected {expected_color_type}")
    if image.interlace != 0:
        failures.append(f"{relative} is interlaced; expected non-interlaced PNG")

    stats = collect_stats(image)
    if stats.unique_sample_colors < min_unique_colors:
        failures.append(f"{relative} has too few sampled colors: {stats.unique_sample_colors}")
    if stats.max_luminance - stats.min_luminance < min_luminance_range:
        failures.append(f"{relative} has too little sampled luminance range")
    if image.channels == 4 and (stats.alpha_min != 255 or stats.alpha_max != 255):
        failures.append(f"{relative} has transparent or semi-transparent pixels in the sampled frame")
    return stats


def load_required_png(path: Path, failures: list[str]) -> PngImage | None:
    if not path.exists():
        failures.append(f"missing PNG asset: {display_path(path)}")
        return None
    try:
        return parse_png(path)
    except ValueError as exc:
        failures.append(f"{display_path(path)} failed PNG parse: {exc}")
        return None


def main() -> int:
    failures: list[str] = []

    actual_screenshots = sorted(path.name for path in SCREENSHOT_DIR.glob("*.png")) if SCREENSHOT_DIR.exists() else []
    if tuple(actual_screenshots) != EXPECTED_SCREENSHOTS:
        failures.append(
            "screenshot set mismatch: expected "
            + ", ".join(EXPECTED_SCREENSHOTS)
            + "; found "
            + ", ".join(actual_screenshots)
        )

    screenshot_stats: dict[str, PixelStats] = {}
    for filename in EXPECTED_SCREENSHOTS:
        image = load_required_png(SCREENSHOT_DIR / filename, failures)
        if image is None:
            continue
        screenshot_stats[filename] = validate_image(image, (1080, 2400), 6, failures)

    seen_digests: dict[str, str] = {}
    for filename, stats in screenshot_stats.items():
        if stats.digest in seen_digests:
            failures.append(f"{filename} duplicates screenshot pixels from {seen_digests[stats.digest]}")
        seen_digests[stats.digest] = filename

    names = list(screenshot_stats)
    for index, left_name in enumerate(names):
        for right_name in names[index + 1 :]:
            distance = hamming_distance(
                screenshot_stats[left_name].average_hash,
                screenshot_stats[right_name].average_hash,
            )
            if distance < 4:
                failures.append(f"{left_name} and {right_name} look too similar by average hash distance {distance}")

    feature = load_required_png(FEATURE_GRAPHIC, failures)
    if feature is not None:
        validate_image(feature, (1024, 500), 2, failures)

    icon = load_required_png(PLAY_STORE_ICON, failures)
    if icon is not None:
        validate_image(icon, (512, 512), 6, failures, min_unique_colors=4, min_luminance_range=30)

    if failures:
        print("Store asset pixel check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: store asset pixels validated "
        f"({len(EXPECTED_SCREENSHOTS)} screenshots 1080x2400, feature graphic 1024x500, icon 512x512)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
