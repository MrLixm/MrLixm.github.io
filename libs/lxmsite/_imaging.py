import dataclasses
import json
import logging
from pathlib import Path
from typing import Any

import PIL.Image

LOGGER = logging.getLogger(__name__)


def read_image_meta_file(file_path: Path) -> dict[str, str]:
    """
    Read a metadata dictionary from a custom file format.

    The image file it characterize is the meta file path minus the ".meta" suffix.

    The metadata is fully abritrary except for the "caption" key which much correspond
    to the text describing the image.

    Args:
        file_path: path to existing meta file.

    Returns:
        arbitrary metadata as 'name: value' pairs.
    """
    file_content = file_path.read_text(encoding="utf-8")
    file_lines = file_content.splitlines()

    # version check, not useful for now, maybe in the future ?
    format_version = file_lines.pop(0)
    if not format_version.startswith("__format__"):
        raise ValueError("Meta file first line must define '__format__: {version}'")
    format_version = format_version.split(":", maxsplit=1)[1].strip(" ")
    if format_version != "1":
        raise TypeError(
            f"Unsupported meta file format version: expected '1' got '{format_version}'"
        )

    # remove last empty line if any
    if not file_lines[-1].strip(" "):
        file_lines.pop(-1)

    metadata = {}
    key = None

    for line in file_lines:
        # indented lines are continuation of previous line
        if not line.strip(" "):
            if key is None:
                raise ValueError("Meta file content cannot start with an empty line.")
            metadata[key] += "\n"

        elif line.startswith("  "):
            if key is None:
                raise ValueError(
                    "Meta file content cannot start with an indented line."
                )
            prefix = "" if metadata[key][-1] == "\n" else " "
            metadata[key] += prefix + line.strip(" ")

        else:
            key, value = line.split(":", maxsplit=1)
            metadata[key] = value.strip(" ")

    return metadata


def get_image_weight_ratio(image_path: Path, threshold=2) -> float:
    with PIL.Image.open(image_path) as image:
        size = image.size
    npixels = size[0] * size[1]
    weight = image_path.stat().st_size
    return (weight**threshold / npixels) ** (1 / threshold) / 1000


@dataclasses.dataclass
class ImageOptimizer:
    convert_mode: str | None = None
    """
    Optional Pillow conversion mode to conver to. Usually "RGB" to convert RGBA pngs.
    """

    target_format: str | None = None
    """
    name of a format supported by Pillow to write the optimized file as.
    
    same as source file if not specified.
    """

    target_file_suffix: str | None = None
    """
    suffix for the optimized file written to disk.
    
    same as source file if not specified.
    """

    format_kwargs: dict[str, Any] = dataclasses.field(default_factory=dict)
    """
    Pillow compatible kwargs for the given `target_format`
    """

    max_dimensions: tuple[int, int] | None = None
    """
    Optional maximum pixel dimensions the image must not be larger than while
    preserving its aspect-ratio.
    """

    def optimize(self, src_path: Path, dst_path: Path):
        """
        Optimize the given image to the given location using this config.
        """
        with PIL.Image.open(src_path) as image:
            if self.convert_mode:
                image = image.convert(self.convert_mode)
            if self.max_dimensions:
                image.thumbnail(self.max_dimensions)
            LOGGER.debug(f"writing '{dst_path}'")
            image.save(dst_path, self.target_format, **self.format_kwargs)


def read_image_opti_file(file_path: Path) -> ImageOptimizer:
    """
    Get an ImageOptimizer instance seirlized from the given file.
    """
    asdict = json.loads(file_path.read_text(encoding="utf-8"))
    if "max_dimensions" in asdict:
        asdict["max_dimensions"] = tuple(asdict["max_dimensions"])
    return ImageOptimizer(**asdict)


if __name__ == "__main__":

    path = r"G:\personal\photo\workspace\outputs\241219_negscanTrip35\241219_negscanTrip35.1116.v0001.jpg"
    print(f"=== {Path(path).name}")
    print(round(get_image_weight_ratio(Path(path)), 2))

    path = r"Z:\packages-dev\MrLixm.github.io\site\src\work\photography\2406leftinthesun\240702_negscan2406.867.v0001.jpg"
    print(f"=== {Path(path).name}")
    print(round(get_image_weight_ratio(Path(path)), 2))

    path = (
        r"Z:\packages-dev\MrLixm.github.io\site\src\.static\images\emojis\cat-nerd.png"
    )
    print(f"=== {Path(path).name}")
    print(round(get_image_weight_ratio(Path(path)), 2))

    path = r"Z:\packages-dev\MrLixm.github.io\site\src\blog\website-redesign-2025\photography-figma-design.png"
    print(f"=== {Path(path).name}")
    print(round(get_image_weight_ratio(Path(path)), 2))

    path = r"Z:\packages-dev\MrLixm.github.io\site\src\blog\website-redesign-2025\screenshot-draft-photography-session.png"
    print(f"=== {Path(path).name}")
    print(round(get_image_weight_ratio(Path(path)), 2))

    path = r"G:\personal\photo\workspace\outputs\250419_uriage\250419_uriage.0005.v0002.jpg"
    print(f"=== {Path(path).name}")
    print(round(get_image_weight_ratio(Path(path)), 2))

    path = r"G:\personal\photo\workspace\outputs\250419_uriage\250419_uriage.0005.v0002..opti.jpg"
    print(f"=== {Path(path).name}")
    print(round(get_image_weight_ratio(Path(path)), 2))
