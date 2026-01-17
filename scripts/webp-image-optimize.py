import argparse
import glob
import logging
import os
import subprocess
import sys
from pathlib import Path

LIBS_DIR = Path(__file__).parent.parent / "libs"
if str(LIBS_DIR) not in sys.path:
    sys.path.append(str(LIBS_DIR))

import lxmsite


OIIOTOOL = Path(os.environ["OIIOTOOL"])
assert OIIOTOOL.exists(), OIIOTOOL

LOGGER = logging.getLogger(Path(__file__).stem)


def get_cli(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an imager to an optimized webp for web viewing."
    )
    parser.add_argument(
        "src_path",
        type=Path,
        help="filesystem path to an existing image or a glob expression matching multiple images.",
    )
    parser.add_argument(
        "--lossless",
        action="store_true",
        help="If specified, the compression will be lossless, else lossy.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="WEBP quality. 0-100 range.",
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


def oiio_export(
    src_path: Path,
    dst_path: Path,
    compression: int,
    lossless: bool,
    resize: tuple[int, int] | None = None,
):
    command = [
        str(OIIOTOOL),
        str(src_path),
    ]
    if resize:
        command += ["--resize", f"{resize[0]}x{resize[1]}"]

    if lossless:
        compression = f"lossless:{compression}"
    else:
        compression = f"webp:{compression}"

    command += ["--compression", compression]
    command += ["-o", str(dst_path)]
    LOGGER.debug(f"subprocess.run({command})")
    subprocess.run(command)


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    LOGGER.debug(f"started with argv={argv}")
    cli = get_cli(argv)
    u_quality: int = cli.quality
    u_src_path: Path = cli.src_path
    u_max_size: str = cli.maxsize
    u_suffix: str = cli.suffix
    u_lossless: bool = cli.lossless
    max_size = u_max_size.split("x") if u_max_size else None
    max_size = (int(max_size[0]), int(max_size[1])) if max_size else None

    if u_src_path.is_file():
        paths = [u_src_path]
    else:
        paths = list(map(Path, glob.glob(str(u_src_path))))

    dst_suffix = "." + u_suffix if u_suffix else ""
    for path in paths:
        dst_path = path.with_suffix(f"{dst_suffix}.webp")
        if dst_path == path:
            LOGGER.warning(f"beware: overwriting '{dst_path}'")

        presize = path.stat().st_size / 1024 / 1024

        oiio_export(
            src_path=path,
            dst_path=dst_path,
            compression=u_quality,
            lossless=u_lossless,
            resize=max_size,
        )

        postsize = dst_path.stat().st_size / 1024 / 1024
        LOGGER.info(f"optimized from {presize:.1f}MiB to {postsize:.3f}MiB")

    LOGGER.info(f"finished optimizing '{len(paths)}' images")


if __name__ == "__main__":
    lxmsite.configure_logging(logging.WARNING)
    LOGGER.setLevel(logging.DEBUG)
    main()
