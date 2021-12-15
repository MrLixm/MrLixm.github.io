"""
Create a new project for the work area
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
    project_title = scc.utils.get_n_verify_input(
        "Give the project name :\n"
    )
    project_file_name = scc.utils.get_n_verify_input(
        "Give the project rst file name :\n"
    )

    # create project directory

    # # find the next project id
    project_id = scc.utils.find_last_increment(scc.ppaths.work_projects)
    # # build the article dir
    project_dir = scc.ppaths.work_projects / project_id
    if project_dir.exists():
        raise RuntimeError(
            f"[Unexcepted Error] The directory <{project_dir}> already exists."
        )
    # # create dir with id
    project_dir.mkdir()

    project_img_dir = scc.ppaths.images / "work" / "projects" / project_id
    if project_img_dir.exists():
        raise RuntimeError(
            f"[Unexcepted Error] The directory <{project_img_dir}> already exists."
        )
    # # create dir with id
    project_img_dir.mkdir()

    # duplicate the template file inside
    shutil.copy2(scc.ppaths.work_projects_template, project_dir)
    # rename it to the name we queried before
    project_path = project_dir / "template.rst"
    new_path = project_dir/f"{project_file_name}.rst"
    project_path.rename(new_path)
    project_path = new_path

    # read the template content and replace tokens
    project_content = project_path.read_text()
    project_content = project_content.replace("$summary", "")
    project_content = project_content.replace("$id", project_id)
    project_content = project_content.replace("$title", project_title)
    project_content = project_content.replace("$tfooter", str("#"*len(project_title)))
    project_content = project_content.replace("$date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    project_path.write_text(project_content, encoding="utf-8")

    print(
        f"[run] Finished, project id <{project_id}> with title "
        f"<{project_title}> created."
    )
    return


if __name__ == '__main__':

    run()