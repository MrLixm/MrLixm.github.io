import logging
from xml.etree import ElementTree

import PIL.Image
from pathlib import Path

from . import directive as Directive

LOGGER = logging.getLogger(__name__)


class ImageGridDirective(Directive.BaseDirectiveBlock):
    """
    Allow the user to specify succesive row of images to form a grid.

    Concept from https://github.com/mosra/m.css/blob/master/plugins/m/images.py#L211.

    Each line of the content is treated as an image. You group images into one row
    by separating them by a blank space. The line must start by the image uri, relative
    to the page its in and is optionally followed by the image caption.
    """

    name = "image-grid"
    expected_arguments = 0
    expected_content = True
    options_schema = {
        "link-images": Directive.BoolOption(False),
        "loading": Directive.StrOption(""),
        "classes": Directive.StrArrayOption([]),
    }

    def run(self, parent, blocks: list[str]):
        directive = self.parse_blocks(blocks)

        u_link_images: bool = directive.options["link-images"]
        u_loading: str = directive.options["loading"]
        u_classes: str = " ".join(directive.options["classes"])
        u_content = directive.content.splitlines()

        # https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img#loading
        if u_loading and u_loading not in ["lazy", "eager"]:
            LOGGER.warning(
                f"Unexpected value for option 'loading' in directive '{self.name}': "
                f"expected 'lazy' or 'eager', got '{u_loading}'"
            )
            u_loading = ""

        rows = [[]]
        total_widths = [0]

        # pre-group the lines as we allow the caption to span multiple lines
        grouped_lines = []
        for line in u_content:
            if not line:
                grouped_lines.append([""])
            elif line.startswith(" " * self.tab_length):
                grouped_lines[-1].append(line.strip(" "))
            else:
                grouped_lines.append([line])

        content = [" ".join(lines) for lines in grouped_lines]

        for uri_caption in content:
            # New line, calculating width from 0 again
            if not uri_caption:
                rows.append([])
                total_widths.append(0)
                continue

            uri, _, caption = uri_caption.partition(" ")
            uri = Path(uri)
            image_path = self.md.mk_path_abs(uri)
            image = PIL.Image.open(image_path)

            rel_width = image.width / image.height
            total_widths[-1] += rel_width
            rows[-1].append((uri, rel_width, caption))

        grid_node = ElementTree.Element("div")
        grid_node.set("class", "image-grid " + u_classes)

        for i, row in enumerate(rows):
            row_node = ElementTree.Element("div")
            row_node.set("class", "image-grid-row")

            for uri, rel_width, caption in row:

                image_node = ElementTree.Element("img")
                image_node.set("src", str(uri))
                image_node.set("alt", caption)
                if u_loading:
                    image_node.set("loading", u_loading)

                target_width = rel_width * 100.0 / total_widths[i]

                caption_node = None
                if caption:
                    caption_node = ElementTree.Element("figcaption")
                    self.parser.parseChunk(caption_node, caption)

                figure_node = ElementTree.Element("figure")
                figure_node.set("style", f"width: {target_width:.3f}%;")

                figure_node.append(image_node)
                if caption_node:
                    figure_node.append(caption_node)

                if u_link_images:
                    wrap_node = ElementTree.Element("a")
                    wrap_node.set("href", str(uri))
                    wrap_node.set("class", "image-reference")
                    wrap_node.append(figure_node)
                else:
                    wrap_node = figure_node

                row_node.append(wrap_node)

            grid_node.append(row_node)

        parent.append(grid_node)
