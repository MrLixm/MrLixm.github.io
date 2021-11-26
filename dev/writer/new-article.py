"""
Create a new article for the blog
"""
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


def get_project_dir():
    """
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


class PPaths:

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
    def article_template(self):
        return self.articles / "_template" / "template.rst"


PPATHS = PPaths()


def get_n_verify_input(message):

    uresult = "{empty}"
    ucontinue = "y"
    while ucontinue == "y" or ucontinue == "Y" or ucontinue == "yes":
        uresult = input(message)
        print(f"[Answer]:\n-----\n{uresult}\n-----\n")
        ucontinue = input("Do you want to re-enter your answer ? (y for yes): ")
        print("\n")
        continue

    return uresult


def run():

    # get input from user
    article_title = get_n_verify_input("Give the article name :\n")
    article_file_name = get_n_verify_input("Give the article rst file name :\n")

    # create article directory
    existing_articles = os.listdir(str(PPATHS.articles))
    regex = re.compile(r"\d\d\d\d")
    existing_articles = list(filter(regex.match, existing_articles))
    existing_articles.sort()
    article_id = int(existing_articles[-1]) + 1
    article_id = str(article_id).zfill(4)  # str like "0007"

    article_dir = PPATHS.articles / article_id
    if article_dir.exists():
        raise RuntimeError(
            f"[Unexcepted Error] The directory <{article_dir}> already exists."
        )
    # create dir with id
    article_dir.mkdir()

    # duplicate the template file inside
    shutil.copy2(PPATHS.article_template, article_dir)
    # rename it to the name we queried before
    article_path = article_dir / "template.rst"
    new_path = article_dir/f"{article_file_name}.rst"
    article_path.rename(new_path)
    article_path = new_path

    # read the template content and replace tokens
    article_content = article_path.read_text()
    article_content = article_content.replace("$summary", "")
    article_content = article_content.replace("$id", article_id)
    article_content = article_content.replace("$title", article_title)
    article_content = article_content.replace("$title-footer", str("#"*len(article_title)))
    article_content = article_content.replace("$date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    article_path.write_text(article_content, encoding="utf-8")

    print(
        f"[run] Finished, article id <{article_id}> with title "
        f"<{article_title}> created."
    )
    return


if __name__ == '__main__':

    run()