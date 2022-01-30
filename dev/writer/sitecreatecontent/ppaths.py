"""
"""
import os
from pathlib import Path
import sys


def get_project_dir():
    """
    From the path of this file, iterate up until you find the project root dir.

    Returns:
        Path: path of the root directory of the blog project
    """
    previous = Path(__file__)

    # iterate parents dir until finding the project's one
    while True:
        new = previous.parent
        # avoid infinite loop
        if new == previous:
            raise RecursionError(
                f"Can't find the project directory,"
                f"reached top parent of <{__file__}>"
            )

        current_content = os.listdir(str(new))
        if "content" and "dev" in current_content:
            break

        previous = new
        continue

    return new


class PPaths(object):
    """
    This is actually registered as a module...
    """

    project = get_project_dir()

    @property
    def root(self):
        return self.project / "content"

    @property
    def articles(self):
        return self.root / "blog"

    @property
    def images(self):
        return self.root / "images"

    @property
    def pages(self):
        return self.root / "pages"

    @property
    def work_projects(self):
        return self.pages / "work" / "projects"

    @property
    def article_template(self):
        return self.articles / "__template" / "template.rst"

    @property
    def work_projects_template(self):
        return self.work_projects / "__template" / "template.rst"


# register the class holding the variables as a module
sys.modules[__name__] = PPaths()