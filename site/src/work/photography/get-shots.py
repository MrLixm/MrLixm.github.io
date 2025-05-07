import logging
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

    template = [f'<div class="{column}">']
    for meta_path in meta_paths:
        metadata = lxmsite.read_image_meta_file(meta_path)
        image_path = Path(str(meta_path).removesuffix(".meta"))
        image_url = image_path.relative_to(site_root).as_posix()
        caption = metadata.get("caption", "")
        caption = jinja2.filters.escape(caption)
        image_id = image_path.parent.name + "-" + image_path.stem
        img_node = f'<img loading="lazy" src={{{{"{image_url}"|mkpagerel}}}} alt="{caption}" title="{caption}">'
        template += [
            '  <div class="shot-item">',
            f'    <a href="#{image_id}">{img_node}</a>',
            f'    <a href="#_" class="img-fullscreen" id="{image_id}">{img_node}</a>',
            "  </div>",
        ]
    template += ["</div>"]
    return template


def generate(template_renderer: lxmsite.TemplateRenderer) -> str:
    site_root = template_renderer.site_config.SRC_ROOT
    template = []

    meta_paths = list(THISDIR.rglob("*.meta"))
    random.shuffle(meta_paths)

    template += build_column(
        "left",
        site_root=site_root,
        meta_paths=meta_paths[: len(meta_paths) // 2],
    )
    template += build_column(
        "right",
        site_root=site_root,
        meta_paths=meta_paths[len(meta_paths) // 2 :],
    )

    return "\n".join(template)
