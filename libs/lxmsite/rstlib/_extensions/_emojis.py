import os.path
from pathlib import Path

import docutils.utils
import docutils.nodes
import docutils.parsers.rst


def docutils_emoji_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: docutils.parsers.rst.states.Inliner,
    options: dict | None = None,
    content: list[str] | None = None,
) -> tuple[list, list]:
    """
    Args:
        name:
            The local name of the interpreted role, the role name actually used in the document.
        rawtext:
            A string containing the entire interpreted text input,
            including the role and markup. Return it as a problematic node
            linked to a system message if a problem is encountered.
        text:
            The interpreted text content.
        lineno:
            The line number where the text block containing the interpreted text begins.
        inliner:
            The docutils.parsers.rst.states.Inliner object that called role_fn.
            It contains the several attributes useful for error reporting and document tree access.
        options:
            A dictionary of directive options for customization (from the "role" directive),
            to be interpreted by the role function. Used for additional attributes for
            the generated elements and other functionality.
        content:
            A list of strings, the directive content for customization
            (from the "role" directive). To be interpreted by the role function.

    Returns:
        - A list of nodes which will be inserted into the document tree at the point
          where the interpreted role was encountered (can be an empty list).
        - A list of system messages, which will be inserted into the document tree
          immediately after the end of the current block (can also be empty).
    """
    text = docutils.utils.unescape(text)
    try:
        emojis_dir: Path = inliner.document.settings.emojis_dir
    except AttributeError:
        raise ValueError("docutils configuration is missing the 'emojis_dir' value.")

    if not emojis_dir.exists():
        raise FileNotFoundError(f"Provided emojis_dir '{emojis_dir}' does not exist.'")

    emoji_path: list[Path] = list(emojis_dir.glob(f"{text}.*"))
    if not emoji_path:
        raise ValueError(f"No emoji with name '{text}' found in '{emojis_dir}'")
    emoji_path: Path = emoji_path[0]

    alt_text_path: Path = emoji_path.with_suffix(".alt.txt")
    alt_text: str = alt_text_path.read_text() if alt_text_path.exists() else ""

    emoji_path: Path = Path(os.path.relpath(emoji_path, Path.cwd()))

    image_node = docutils.nodes.image(
        "",
        uri=emoji_path.as_posix(),
        alt=alt_text,
        classes=["emoji-role"],
        title=emoji_path.stem,
    )
    return [image_node], []
