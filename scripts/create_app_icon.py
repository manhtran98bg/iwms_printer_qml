from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "src" / "assets" / "icon" / "icon.png"
DEFAULT_OUTPUT = PROJECT_ROOT / "src" / "assets" / "icon" / "icon.ico"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def create_icon(source: Path, output: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Source image does not exist: {source}")

    with Image.open(source) as image:
        image = image.convert("RGBA")
        if image.width != image.height:
            raise ValueError(
                f"Source image must be square, got {image.width}x{image.height}: {source}"
            )
        if image.width < max(ICON_SIZES):
            raise ValueError(
                f"Source image must be at least {max(ICON_SIZES)}x{max(ICON_SIZES)}."
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(
            output,
            format="ICO",
            sizes=[(size, size) for size in ICON_SIZES],
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a multi-size Windows ICO file from a square PNG."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source PNG path (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output ICO path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    create_icon(source, output)

    sizes = ", ".join(f"{size}x{size}" for size in ICON_SIZES)
    print(f"Created: {output}")
    print(f"Embedded sizes: {sizes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
