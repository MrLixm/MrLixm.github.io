"""

"""
import os
import re


def get_n_verify_input(message):
    """
    Ask the user to enter some input in the terminal, ask if the input is ok.
    If yes return it if no ask again and repeat.

    Args:
        message(str):

    Returns:
        str:
    """

    uresult = "{empty}"
    ucontinue = "y"
    while ucontinue == "y" or ucontinue == "Y" or ucontinue == "yes":
        uresult = input(message)
        print(
            f"[Answer](between <>):\n"
            f"-----\n"
            f"<{uresult}>\n"
            f"-----\n"
        )
        ucontinue = input("Do you want to re-enter your answer ? (y for yes): ")
        print("\n")
        continue

    return uresult


def find_last_increment(root_dir):
    """
    From the given root directory that contains a bunch of 4 digit directory
    , return the one up increment.

    Args:
        root_dir(str): any object that once converted to str is a dir path.

    Returns:
        str: 4 digit identifier found
    """

    existing_projects = os.listdir(str(root_dir))
    regex = re.compile(r"\d\d\d\d")
    existing_projects = list(filter(regex.match, existing_projects))
    if not existing_projects:
        return "0001"
    existing_projects.sort()
    project_id = int(existing_projects[-1]) + 1
    project_id = str(project_id).zfill(4)  # str like "0007"

    return project_id
