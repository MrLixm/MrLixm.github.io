"""
Create a new article for the blog
"""
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# add sitecreatecontent package to path
sys.path.append(str(Path(__file__).parent))

import sitecreatecontent as scc


def run():

    # get input from user
    article_title = scc.utils.get_n_verify_input(
        "Give the article name :\n"
    )
    article_file_name = scc.utils.get_n_verify_input(
        "Give the article rst file name :\n"
    )

    # create article directory

    # # find the next article id
    article_id = scc.utils.find_last_increment(scc.ppaths.articles)
    # # build the article dir
    article_dir = scc.ppaths.articles / article_id
    if article_dir.exists():
        raise RuntimeError(
            f"[Unexcepted Error] The directory <{article_dir}> already exists."
        )
    # # create dir with id
    article_dir.mkdir()

    article_img_dir = scc.ppaths.images / "blog" / article_id
    if article_img_dir.exists():
        raise RuntimeError(
            f"[Unexcepted Error] The directory <{article_img_dir}> already exists."
        )
    # # create dir with id
    article_img_dir.mkdir()

    # duplicate the template file inside
    shutil.copy2(scc.ppaths.article_template, article_dir)
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
    article_content = article_content.replace("$tfooter", str("#"*len(article_title)))
    article_content = article_content.replace("$date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    article_path.write_text(article_content, encoding="utf-8")

    print(
        f"[run] Finished, article id <{article_id}> with title "
        f"<{article_title}> created."
    )
    return


if __name__ == '__main__':

    run()