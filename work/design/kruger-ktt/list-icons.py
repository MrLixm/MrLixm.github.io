from pathlib import Path

from typing import Iterable

import lxmsite

THIS_DIR = Path(__file__).parent


def generate(template_renderer: lxmsite.TemplateRenderer) -> str:
    site_root = template_renderer.site_config.SRC_ROOT

    icons_dir = THIS_DIR / "icons"
    icons_paths: Iterable[Path] = icons_dir.glob("*.png")

    html = []
    for icon_path in icons_paths:
        node_name = icon_path.stem.removeprefix("ktt-")
        icon_url = icon_path.relative_to(site_root).as_posix()
        caption = f"icon for the {node_name} node"
        html.append(
            f'<img src="{{{{"{icon_url}"|mkpagerel}}}}" alt="{caption}" title="{caption}">'
        )

    return "\n".join(html)
