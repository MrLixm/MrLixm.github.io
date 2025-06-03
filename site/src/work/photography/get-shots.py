import logging
import math
import random
from pathlib import Path

import jinja2.filters

import lxmsite

LOGGER = logging.getLogger(__name__)

THISDIR = Path(__file__).parent


def build_column(
    column: str,
    site_root: Path,
    meta_paths: list[Path],
) -> list[str]:

    template = [f'<div class="{column} shot-gallery-item">']
    for meta_path in meta_paths:
        metadata = lxmsite.read_image_meta_file(meta_path)
        image_path = Path(str(meta_path).removesuffix(".meta"))
        image_url = image_path.relative_to(site_root).as_posix()
        caption = metadata.pop("caption", "")
        caption = jinja2.filters.escape(caption)
        image_id = image_path.parent.name + "-" + image_path.stem
        metadata_str = "\n".join([f"- {mn}: {mv}" for mn, mv in metadata.items()])
        img_node = f'<img loading="lazy" src={{{{"{image_url}"|mkpagerel}}}} alt="{caption}" title="{caption}\n{"-"*20}\nMetadata:\n{metadata_str}">'
        template += [
            '  <div class="shot-item">',
            f'    <a href="#{image_id}">{img_node}</a>',
            f'    <a href="#_" class="img-fullscreen" id="{image_id}">{img_node}</a>',
            "  </div>",
        ]
    template += ['<div class="empty-image"></div>']
    template += ["</div>"]
    return template


def generate(template_renderer: lxmsite.TemplateRenderer) -> str:
    site_root = template_renderer.site_config.SRC_ROOT
    template = []

    meta_paths = list(THISDIR.rglob("*.meta"))
    random.shuffle(meta_paths)

    column_number = 4
    meta_paths_columns = [
        meta_paths[
            math.floor(len(meta_paths) / column_number)
            * i : (
                None
                if i == column_number - 1
                else math.floor(len(meta_paths) / column_number) * (i + 1)
            )
        ]
        for i in range(0, column_number)
    ]
    for index, paths in enumerate(meta_paths_columns):
        template += build_column(
            str(index),
            site_root=site_root,
            meta_paths=paths,
        )

    return "\n".join(template)
