"""
Project's file hierarchy
"""
import os
import re
from pathlib import Path

from dev import cfg


def get_blog_project_dir_from(source_path: Path) -> Path:
    """
    From the given path, iterate **up** until you find the blog's project root dir.

    Args:
        source_path: An existing file or directory path. Can already be the project path.

    Returns:
        path of blog's root directory. (git repo)
    """
    previous_path = Path(source_path)
    if source_path.is_file():
        previous_path = source_path.parent

    # iterate parents dir until finding the project's one
    while True:

        new_path = previous_path.parent

        # avoid infinite loop
        if new_path == previous_path:
            raise RecursionError(
                f"Can't find the project directory,"
                f"reached top parent of <{source_path}>"
            )

        current_content = os.listdir(str(new_path))
        if "content" and "dev" in current_content:
            break

        previous_path = new_path
        continue

    return new_path


PROJECT = get_blog_project_dir_from(Path(__file__))
"""
Root directory for this blog. (git repository)
"""

CONTENT = PROJECT / "content"
"""
Directory for the blog content.
"""

ARTICLES = CONTENT / "blog"

IMAGES = CONTENT / "images"

IMAGES_BLOG = IMAGES / "blog"

PAGES = CONTENT / "pages"

WORK_PROJECTS = PAGES / "work" / "projects"


def get_last_article_id() -> int:
    """
    Get the identifier number of the last article that can be found in the project.
    """

    existing_projects = os.listdir(str(ARTICLES))

    pattern = re.compile(r"\d\d\d\d")
    existing_projects = list(filter(pattern.match, existing_projects))
    if not existing_projects:
        return 1

    existing_projects.sort()
    project_id = int(existing_projects[-1])
    return project_id


def get_next_article_id() -> str:
    """
    Retrieve the identifier of the next non-existing article as a formatted string.
    """

    last_id = get_last_article_id()
    next_id = last_id + 1
    return str(next_id).zfill(cfg.ZFILL)
