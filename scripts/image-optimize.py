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
    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="Additional characters to suffix to the output file name.",
    )
    parsed = parser.parse_args(argv)
    return parsed


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    LOGGER.debug(f"started with argv={argv}")
    cli = get_cli(argv)
    u_quality: int = cli.quality
    u_src_path: Path = cli.src_path
    u_max_size: str = cli.maxsize
    u_suffix: str = cli.suffix
    max_size = u_max_size.split("x") if u_max_size else None
    max_size = (float(max_size[0]), float(max_size[1])) if max_size else None

    if u_src_path.is_file():
        paths = [u_src_path]
    else:
        paths = list(map(Path, glob.glob(str(u_src_path))))

    dst_suffix = "." + u_suffix if u_suffix else ""
    for path in paths:
        dst_path = path.with_suffix(f"{dst_suffix}.jpg")
        if dst_path == path:
            LOGGER.warning(f"beware: overwriting '{dst_path}'")

        presize = path.stat().st_size / 1024 / 1024

        with PIL.Image.open(path) as image:
            image = image.convert("RGB")
            if max_size:
                image.thumbnail(max_size)
            LOGGER.info(f"writing '{dst_path}'")
            # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving
            # note this intentionally doesn't preserve any metadata
            image.save(
                dst_path,
                "JPEG",
                quality=u_quality,
                subsampling=1,
            )

        postsize = dst_path.stat().st_size / 1024 / 1024
        LOGGER.info(f"optimized from {presize:.1f}MiB to {postsize:.1f}MiB")

    LOGGER.info(f"finished optimizing '{len(paths)}' images")


if __name__ == "__main__":
    lxmsite.configure_logging(logging.WARNING)
    LOGGER.setLevel(logging.DEBUG)
    main()
