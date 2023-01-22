"""
Create a new article for the blog
"""
import logging
import shutil
from datetime import datetime

import dev.creating.templates
import dev.hierarchy

logger = logging.getLogger(__name__)


def create_new_article(article_title: str, article_file_name: str):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    article_id = dev.hierarchy.get_next_article_id()

    article_dir = dev.hierarchy.ARTICLES / article_id
    if article_dir.exists():
        raise RuntimeError(
            f"[Unexcepted Error] The directory <{article_dir}> already exists."
        )
    article_dir.mkdir()
    logger.info(f"Created {article_dir=}")

    article_img_dir = dev.hierarchy.IMAGES_BLOG / article_id
    if article_img_dir.exists():
        raise RuntimeError(
            f"[Unexcepted Error] The directory <{article_img_dir}> already exists."
        )
    article_img_dir.mkdir()
    logger.info(f"Created {article_img_dir=}")

    # duplicate the template file inside
    template_path = dev.creating.templates.article_rst
    logger.info(f"Copying {template_path} -> {article_dir}")
    shutil.copy2(template_path, article_dir)
    # rename it to the name provided
    article_path = article_dir / template_path.name
    new_path = article_dir / f"{article_file_name}.rst"
    article_path.rename(new_path)
    article_path = new_path

    # read the template content and replace tokens
    logger.info(f"About to read and process {article_path} ...")
    article_content = article_path.read_text()
    article_content = article_content.replace("$summary", "")
    article_content = article_content.replace("$id", article_id)
    article_content = article_content.replace("$title", article_title)
    article_content = article_content.replace("$tfooter", str("#" * len(article_title)))
    article_content = article_content.replace("$date", current_time)
    article_path.write_text(article_content, encoding="utf-8")

    logger.info(
        f" Finished, article id <{article_id}> with title "
        f"<{article_title}> created."
    )
    return
