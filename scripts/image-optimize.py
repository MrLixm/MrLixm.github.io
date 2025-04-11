import argparse
import glob
import logging
import sys
from pathlib import Path

import PIL.Image

LIBS_DIR = Path(__file__).parent.parent / "libs"
if str(LIBS_DIR) not in sys.path:
    sys.path.append(str(LIBS_DIR))

import lxmsite

LOGGER = logging.getLogger(__name__)


def get_cli(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an imager to an optimized jpeg for web viewing."
    )
    parser.add_argument(
        "src_path",
        type=Path,
        help="filesystem path to an existing image or a glob expression matching multiple images.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=90,
        help="JPEG quality. 0-100 range.",
    )
    parser.add_argument(
        "--maxsize",
        type=str,
        default=None,
        help="maximum dimensions the image must have; specified as {width}x{height}",
    )
    parsed = parser.parse_args(argv)
    return parsed


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    LOGGER.debug(f"started with argv={argv}")
    cli = get_cli(argv)
    u_src_path: Path = cli.src_path
    u_max_size: str = cli.maxsize
    max_size = u_max_size.split("x") if u_max_size else None
    max_size = (float(max_size[0]), float(max_size[1])) if max_size else None

    if u_src_path.is_file():
        paths = [u_src_path]
    else:
        paths = list(map(Path, glob.glob(str(u_src_path))))

    for path in paths:
        dst_path = path.with_suffix(".jpg")
        if dst_path == path:
            LOGGER.warning(f"beware: overwriting '{dst_path}'")

        with PIL.Image.open(path) as image:
            image = image.convert("RGB")
            if max_size:
                image.thumbnail(max_size)
            LOGGER.info(f"writing '{dst_path}'")
            # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving
            image.save(
                dst_path,
                "JPEG",
                quality=90,
                subsampling=1,
            )

    LOGGER.info(f"finished optimizing '{len(paths)}' images")


if __name__ == "__main__":
    lxmsite.configure_logging()
    main()
