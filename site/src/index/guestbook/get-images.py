import logging
import random
from pathlib import Path

import lxmsite

LOGGER = logging.getLogger(__name__)

THISDIR = Path(__file__).parent


def generate(template_renderer: lxmsite.PageTemplateRenderer) -> str:
    site_root = template_renderer.site_config.SRC_ROOT
    template = []

    meta_paths = list(THISDIR.glob("*.meta"))
    metadatas = [(path, lxmsite.read_image_meta_file(path)) for path in meta_paths]

    def sorter(m):
        return int(m[1].get("index", 0))

    metadatas.sort(key=sorter)

    # metadatas *= 4

    for index, (meta_path, meta) in enumerate(metadatas):
        # image
        image_path = Path(str(meta_path).removesuffix(".meta"))
        assert image_path.exists(), image_path
        image_url = image_path.relative_to(site_root).as_posix()
        # metadata
        caption = meta.get("caption", "")
        link = meta.get("link", "")
        author = meta.get("author", "")
        # index = meta.get("index", random.randint(0, len(metadatas) - 1))
        if not author:
            author = image_path.stem

        random.seed(index * 3)
        left = random.randrange(-5, 80)
        top = random.randrange(-5, 70)
        rotation = random.randrange(-200, 200) / 10
        variables = f"--drawing-left:{left}%;--drawing-top:{top}%;--drawing-rotation:{rotation}deg;"
        if link:
            template += [f'  <a href="{link}" target="_blank">']
        img_attrs = [
            'class="drawing"',
            f'id="drawing-{image_path.stem}-{index}"'
            f'src="{{{{"{image_url}"|mkpagerel}}}}"',
            f'alt="{{{{{repr(caption)}|e}}}}"',
            f'title="Created by {{{{{repr(author)}|e}}}} !"',
            f'style="{variables}"',
        ]
        template += [f'    <img {" ".join(img_attrs)}>']
        if link:
            template += ["  </a>"]

    return "\n".join(template)
