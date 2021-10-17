
import os
import random
from os.path import join as pjoin
from pprint import pprint
from pathlib import Path

IMG_DIR = Path(r"G:\personal\code\Blog\workspace\v0001\Blog\content\images\blog\prodm")


def replace_spaces():

    files = [f for f in os.listdir(IMG_DIR) if os.path.isfile(pjoin(IMG_DIR, f))]

    for file_name in files:

        src_file = IMG_DIR / file_name
        new_file = IMG_DIR / file_name.replace(" ", "_")
        src_file.rename(new_file)

    return


def get_caption(file_name):
    """ Convert the filename to the file caption.

    Args:
        file_name(str): name of the file

    Returns:
        str:
    """
    caption = os.path.splitext(file_name)[0]

    caption = caption.replace("_", " ")

    caption = caption.replace("-1", "?")
    caption = caption.replace("-2", "!")
    caption = caption.replace("-3", "<")
    caption = caption.replace("-4", ">")
    caption = caption.replace("-5", "*")

    # 100+ are special cases
    caption = caption.replace("-100", "m̴͕̪̼̒́̐o̵̠̺̟̒͝o̴͎̻̺͐̽d̵̘̪͓͆͠")
    caption = caption.replace("-101", "a̵̵̢̡͉͉̟̒̾͑͆̚̕͜b̴̵̢͍̼͚̙̿̔͒̓͌͜b̸̴̡̻̘͙͙̺͑͑̀͌͠͝e̴̸̡̦͉̺̫̫͌̓̒̽͠r̸̵̡̺̟̫̦̈́̾̾̚͠͠a̴̸͙̘̦̺̙̺͊̒̔͝͝͝t̵̵͔͇̫͚̾͒̔̕͜͜͠i̵̸͔̞̪̠̝̪̐̐̕̚͝o̸̴͚͚͎͕̻͛͋̈́̚͠͝n̸̴̦͎̪̘̫̺͋̽͐̔͌͝")

    # 200+ are emojis
    caption = caption.replace("-200", "🤡")

    return caption


def get_image_grid():

    files = [f for f in os.listdir(IMG_DIR) if os.path.isfile(pjoin(IMG_DIR, f))]

    print(f"[get_image_grid] {len(files)} files found.")
    pprint(files)

    # randomize list order
    random.shuffle(files)

    out_str = ""
    for index, file_name in enumerate(files):

        caption = get_caption(file_name=file_name)

        out_str += f"   {{static}}/images/blog/prodm/{file_name} {caption}\n"
        # add a line break between, every three items
        if index % 3 == 1:
            out_str += "\n"

    print("[get_image_grid] Finished.")
    return out_str


if __name__ == '__main__':

    # replace_spaces()
    image_grid = get_image_grid()
    print(image_grid)