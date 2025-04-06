import glob
import os
from pathlib import Path


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
        file_path.parent / line
        for line in file_path.read_text(encoding="utf-8").splitlines()
    ]
    ignored_paths = []
    for ignored_expr in ignored:
        ignored_paths += glob.glob(
            str(ignored_expr),
            recursive=True,
            # only in python 3.11+
            # include_hidden=True,
        )
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
