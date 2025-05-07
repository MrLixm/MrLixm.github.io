import argparse
import logging
import sys
from pathlib import Path

LIBS_DIR = Path(__file__).parent.parent / "libs"
if str(LIBS_DIR) not in sys.path:
    sys.path.append(str(LIBS_DIR))

import lxmsite

LOGGER = logging.getLogger(__name__)


def get_cli(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a page and its extra-files for a photography session."
    )
    parser.add_argument(
        "src_path",
        type=Path,
        help="filesystem path to an existing directory with images already added inside",
    )
    parsed = parser.parse_args(argv)
    return parsed


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    LOGGER.debug(f"started with argv={argv}")
    cli = get_cli(argv)
    u_src_path: Path = cli.src_path

    images: list[Path] = list(u_src_path.glob("*.jpg"))
    if not images:
        LOGGER.warning(f"no jpg images found in '{u_src_path}'")
        return

    meta_file_template = (
        "__format__: 1\n"
        "date: \n"
        "location: \n"
        "film: \n"
        "lens: Minolta MD 35mm\n"
        "camera: Minolta X-500\n"
        "caption: placeholder text\n"
    )
    directive_str = (
        ".. image-gallery::\n"
        "    :left:\n"
        "    :right:\n"
        "    :left-width: 50\n"
        "    :right-width: 50\n"
    )

    for index, image_path in enumerate(images):
        meta_path = image_path.with_name(f"{image_path.name}.meta")
        LOGGER.info(f"writing '{meta_path}'")
        meta_path.write_text(meta_file_template)

        index += 1
        directive_str += (
            "\n"
            f"    .. image-frame:: image{index} label{index} {meta_path.name}\n"
            "\n"
            "        :code:`<>∧∨` {caption}\n"
        )

    print(directive_str)


if __name__ == "__main__":
    lxmsite.configure_logging(logging.WARNING)
    LOGGER.setLevel(logging.DEBUG)
    main()
