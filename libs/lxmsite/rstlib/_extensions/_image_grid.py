import PIL.Image
from pathlib import Path

import docutils.nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive


class ImageGrid(Directive):
    """
    Allow the user to specify succesive row of images to form a grid.

    Concept from https://github.com/mosra/m.css/blob/master/plugins/m/images.py#L211.

    Each line of the content is treated as an image. You group images into one row
    by separating them by a blank space. The line must start by the image uri, relative
    to the page its in and is optionally followed by the image caption.
    """

    option_spec = {
        "link-images": directives.flag,
        "classes": directives.class_option,
        "loading": directives.unchanged,
    }
    has_content = True

    def run(self):
        grid_node = docutils.nodes.container(classes=["image-grid"])
        if "classes" in self.options:
            grid_node["classes"] += self.options["classes"]

        # https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img#loading
        image_loading = self.options["loading"] if "loading" in self.options else None
        image_loading = image_loading if image_loading in ["lazy", "eager"] else None

        rows = [[]]
        total_widths = [0]

        # pre-group the lines as we allow the caption to span multiple lines
        grouped_lines = []
        for line in self.content:
            if not line:
                grouped_lines.append([""])
            elif line.startswith("  "):
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
            image_path = Path(uri).resolve()
            image = PIL.Image.open(image_path)

            rel_width = image.width / image.height
            total_widths[-1] += rel_width
            rows[-1].append((uri, rel_width, caption))

        for i, row in enumerate(rows):
            row_node = docutils.nodes.container(classes=["image-grid-row"])

            for uri, rel_width, caption in row:
                image_reference = directives.uri(uri)
                image_attrs = {}
                if image_loading:
                    image_attrs["loading"] = image_loading
                image_node = docutils.nodes.image(
                    "",
                    uri=image_reference,
                    alt=caption,
                    **image_attrs,
                )
                target_width = rel_width * 100.0 / total_widths[i]

                caption_node = None
                if caption:
                    text_nodes, _ = self.state.inline_text(caption, self.lineno)
                    caption_node = docutils.nodes.caption("", "")
                    caption_node.extend(text_nodes)

                figure_node = docutils.nodes.figure(width=f"{target_width:.3f}%")
                figure_node.append(image_node)
                if caption_node:
                    figure_node.append(caption_node)

                if "link-images" in self.options:
                    wrap_node = docutils.nodes.reference("", refuri=image_reference)
                    wrap_node["classes"].append("image-reference")
                    wrap_node.append(figure_node)
                else:
                    wrap_node = figure_node

                row_node.append(wrap_node)

            grid_node.append(row_node)

        return [grid_node]
