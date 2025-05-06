import logging
from pathlib import Path

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
