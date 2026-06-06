#!/usr/bin/env python3
from __future__ import annotations

import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import check_store_asset_pixels as checker


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(kind)
    checksum = zlib.crc32(payload, checksum) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def write_png(path: Path, width: int, height: int, color_type: int, pixel: callable) -> None:
    channels = 3 if color_type == 2 else 4
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            value = pixel(x, y)
            if len(value) != channels:
                raise ValueError("pixel function returned the wrong channel count")
            rows.extend(value)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    path.write_bytes(
        PNG_SIGNATURE
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(bytes(rows)))
        + png_chunk(b"IEND", b"")
    )


def rgb_gradient(x: int, y: int) -> tuple[int, int, int]:
    return (x * 17 % 256, y * 19 % 256, (x * 11 + y * 7) % 256)


def rgba_gradient(x: int, y: int) -> tuple[int, int, int, int]:
    red, green, blue = rgb_gradient(x, y)
    return red, green, blue, 255


class StoreAssetPixelsSelfTest(unittest.TestCase):
    def test_rgb_png_parses_and_validates_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="poryadok5-png.") as tmp_dir:
            path = Path(tmp_dir) / "feature.png"
            write_png(path, 16, 16, 2, rgb_gradient)

            image = checker.parse_png(path)
            failures: list[str] = []
            stats = checker.validate_image(
                image,
                (16, 16),
                2,
                failures,
                min_unique_colors=8,
                min_luminance_range=20,
            )

            self.assertEqual([], failures)
            self.assertGreaterEqual(stats.unique_sample_colors, 8)

    def test_rgba_png_with_transparency_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="poryadok5-png.") as tmp_dir:
            path = Path(tmp_dir) / "transparent.png"
            write_png(path, 8, 8, 6, lambda x, y: (x * 20, y * 20, 120, 128 if x == y else 255))

            image = checker.parse_png(path)
            failures: list[str] = []
            checker.validate_image(
                image,
                (8, 8),
                6,
                failures,
                min_unique_colors=4,
                min_luminance_range=10,
            )

            self.assertTrue(any("transparent" in failure for failure in failures), msg=failures)

    def test_wrong_dimensions_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="poryadok5-png.") as tmp_dir:
            path = Path(tmp_dir) / "wrong-size.png"
            write_png(path, 8, 8, 2, rgb_gradient)

            image = checker.parse_png(path)
            failures: list[str] = []
            checker.validate_image(
                image,
                (16, 8),
                2,
                failures,
                min_unique_colors=4,
                min_luminance_range=10,
            )

            self.assertTrue(any("dimensions" in failure for failure in failures), msg=failures)

    def test_flat_image_fails_luminance_gate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="poryadok5-png.") as tmp_dir:
            path = Path(tmp_dir) / "flat.png"
            write_png(path, 8, 8, 2, lambda _x, _y: (120, 120, 120))

            image = checker.parse_png(path)
            failures: list[str] = []
            checker.validate_image(
                image,
                (8, 8),
                2,
                failures,
                min_unique_colors=2,
                min_luminance_range=10,
            )

            self.assertTrue(any("luminance range" in failure for failure in failures), msg=failures)

    def test_non_png_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="poryadok5-png.") as tmp_dir:
            path = Path(tmp_dir) / "not-png.bin"
            path.write_bytes(b"not a png")

            with self.assertRaises(ValueError):
                checker.parse_png(path)

    def test_average_hash_distance_detects_identical_images(self) -> None:
        with tempfile.TemporaryDirectory(prefix="poryadok5-png.") as tmp_dir:
            left = Path(tmp_dir) / "left.png"
            right = Path(tmp_dir) / "right.png"
            write_png(left, 16, 16, 2, rgb_gradient)
            write_png(right, 16, 16, 2, rgb_gradient)

            left_hash = checker.average_hash(checker.parse_png(left))
            right_hash = checker.average_hash(checker.parse_png(right))

            self.assertEqual(0, checker.hamming_distance(left_hash, right_hash))


if __name__ == "__main__":
    unittest.main(verbosity=2)
