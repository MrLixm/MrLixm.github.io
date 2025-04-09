import os
import re
from pathlib import Path

import unicodedata


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    References:
        - [1] https://github.com/django/django/blob/30e0a43937e685083fa1210c3594678a3b813806/django/utils/text.py#L444
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def mkpagerel(path: str, page_path: str) -> str:
    """
    Convert a site-root-relative path, to a path relative to the given page.
    """
    root_path: Path = Path("placeholder")
    pageabs = root_path.joinpath(page_path).resolve()
    pathabs = root_path.joinpath(path).resolve()
    return Path(os.path.relpath(pathabs, start=pageabs.parent)).as_posix()


def mksiterel(path: str, page_path: str) -> str:
    """
    Convert a page-relative path to a path relative to the site root.
    """
    root_path: Path = Path("placeholder")
    pageabs = root_path.joinpath(page_path).resolve()
    pathabs = pageabs.parent.joinpath(path).resolve()
    return Path(os.path.relpath(pathabs, start=root_path)).as_posix()
