import dataclasses
import glob
import json
import logging
import os
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def read_siteignore(file_path: Path) -> list[Path]:
    """
    Read and resolve a list of paths that must be ignored in the filestructure.

    Warning:
        the current logic implies we only ignore files that exist at the time this
        function is executed. It's possible file that must be ignored are added after
        this function execution and will not be considered.

    Args:
        file_path: filesystem path to an existing .siteignore file.

    Returns:
        list of absolute paths to existing files or directories.
    """
    ignored = [
        line
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip(" ")
    ]
    ignored_paths = []
    for ignored_expr in ignored:
        ignored_paths += file_path.parent.glob(str(ignored_expr))
    return [Path(path) for path in ignored_paths]


def collect_site_files(site_root: Path) -> list[Path]:
    """
    Visit the given directory to collect all file path that will be used for the final website.

    Args:
        site_root: filesystem path to an existing directory.

    Returns:
        list of absolute path to existing files.
    """

    ignored: list[Path] = []
    visited: list[Path] = []

    for rootpath, dirnames, filenames in os.walk(site_root):
        if ".siteignore" in filenames:
            sitignore_path = Path(rootpath) / ".siteignore"
            ignored += read_siteignore(sitignore_path)
            filenames.remove(sitignore_path.name)

        for dirname in dirnames:
            dirpath = Path(rootpath) / dirname
            if dirpath in ignored:
                dirnames.remove(dirname)

        for filename in filenames:
            filepath = Path(rootpath) / filename
            if filepath in ignored:
                continue

            visited.append(filepath)

    return visited


def collect_shelves(site_files: list[Path]) -> dict[Path, list[Path]]:
    """
    Browse the given site files to find shelves and their children paths.

    Returns:
        mapping of "shelf config file path": list of "children path"
    """
    shelves = {path: [] for path in site_files if path.name == ".shelf"}
    for path in site_files:
        if path in shelves:
            continue
        for shelf_path in shelves:
            if path.is_relative_to(shelf_path.parent):
                shelves[shelf_path].append(path)
    return shelves


@dataclasses.dataclass
class MetaFile:
    """
    A file with user arbitrary content that correspond to default values to use for multiple pages metadata.

    The content is a simple mapping of "metadata name": "metadata value" where the name is exactly the same
    as you would set it in an individual page.

    The value can be a str, or a list str that in that case will be concatanted with any similar parent meta key.
    """

    path: Path
    """
    the original file path for the file
    """

    content: dict[str, str | list[str]]
    """
    mapping of "metadata name": "metadata value"
    """

    children: list[Path]
    """
    list of existing file paths this meta file affects
    """

    @classmethod
    def from_path(cls, path: Path) -> "MetaFile":
        LOGGER.debug(f"reading meta file '{path}'")
        content = json.loads(path.read_text(encoding="utf-8"))
        return cls(path=path, content=content, children=[])


class MetaFileCollection:
    """
    A collection of meta files with their associated path they must be applied to.
    """

    def __init__(self, meta_files: list[MetaFile]):
        self._meta_files = meta_files
        self._meta_by_src: dict[Path, list[MetaFile]] = {}
        for meta_file in meta_files:
            for child in meta_file.children:
                self._meta_by_src.setdefault(child, []).append(meta_file)

    @property
    def meta_files(self) -> list[MetaFile]:
        return self._meta_files

    def get_path_meta(self, path: Path, stringify_lists=",") -> dict[str, str]:
        """
        Get the meta file metadata corresponding to the given path.

        The path can be any kind of path and may not have any associated metadata, thus returning an empty dict.
        """
        meta_files = self._meta_by_src.get(path, [])

        default_meta: dict[str, str | list[str]] = {}

        for meta_file in meta_files:
            for k, v in meta_file.content.items():
                # deep merge lists
                if isinstance(v, list):
                    if k in default_meta and isinstance(default_meta[k], str):
                        default_meta[k] = [default_meta[k]] + v
                    else:
                        default_meta.setdefault(k, []).extend(v)
                else:
                    default_meta[k] = v

        default_meta = {
            k: stringify_lists.join(v) if isinstance(v, list) else v
            for k, v in default_meta.items()
        }
        return default_meta


def collect_meta_files(site_files: list[Path]) -> MetaFileCollection:
    """
    Browse the given site files to find meta files and their children paths they apply to.

    Returns:
        collection of meta files.
    """
    _site_files = site_files.copy()
    meta_files = []
    for path in site_files:
        if path.name == ".meta.json":
            meta_files.append(MetaFile.from_path(path))
            _site_files.remove(path)

    for path in _site_files:
        for meta_file in meta_files:
            if path.is_relative_to(meta_file.path.parent):
                meta_file.children.append(path)

    return MetaFileCollection(meta_files)
