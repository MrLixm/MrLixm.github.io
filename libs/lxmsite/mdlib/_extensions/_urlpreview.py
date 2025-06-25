import re
from xml.etree import ElementTree
from pathlib import Path

from . import directive as Directive

THISDIR = Path(__file__).parent


def set_svg_size(svg: str, width: int | str, height: int | str | None = None) -> str:
    """
    Quick & dirty way to modify the width height attribute of a svg.

    Args:
        svg: svg as string.
        width:
        height:

    Returns:
        svg with the updated width & height attributes.
    """

    if not height:
        height = width

    width_pattern = re.compile(r"width=[\"-'](\w+)[\"-']")
    height_pattern = re.compile(r"height=[\"-'](\w+)[\"-']")

    if width_pattern.match(svg):

        new_svg = width_pattern.sub(
            repl=rf"width=\"{width}\"",
            string=svg,
        )

    else:

        new_svg = re.sub(
            pattern="<svg",
            repl=f'<svg width="{width}"',
            string=svg,
        )

    if height_pattern.match(new_svg):

        new_svg = height_pattern.sub(
            repl=rf"width=\"{width}\"",
            string=new_svg,
        )

    else:

        new_svg = re.sub(
            pattern="<svg",
            repl=f'<svg height="{height}"',
            string=new_svg,
        )

    return new_svg


class SizeOption(Directive.BaseOption[tuple[int, int]]):

    def unserialize(self, value: str) -> tuple[int, int]:

        # convenient hint in case the user forget
        if "px" in value or "%" in value:
            raise ValueError(
                f"Incorrect option value '{value}': cannot have 'px' or"
                " '%', it should be made of floats or ints."
            )

        size = value.split(",", 1)
        if len(size) == 2:
            output = (int(size[0]), int(size[1]))
        else:
            output = (int(size[0]), int(size[0]))

        return output


class UrlPreviewDirective(Directive.BaseDirectiveBlock):
    """
    As you can't embed url preview without Js, this will make it looks more
    pretty than a static url::

        [-------][   Title            ]
        [ Image ][   Url              ]
        [_______][   Description      ]

    * ``Image`` is based on the instance ``__type`` attribute
    * ``Url`` is teh directive argument
    * ``Title`` is a directive :title: option
    * ``Description`` is the directive's content.

    Here is the Markdown syntax:
    ::

        .. url-preview:: https://liamcollod.xyz
            :title: Check my website !
            :image: ./img-url/relative-to-page/img.jpg

    """

    name = "url-preview"
    expected_arguments = 1
    expected_content = False
    options_schema = {
        "title": Directive.StrOption(""),
        "image": Directive.StrOption(""),
        "svg": Directive.StrOption(""),
        "svg-size": SizeOption((-1, -1)),
        "color": Directive.StrOption(""),
    }
    cssclass_prefix = "url-preview"

    # a circle with a carved "link" icon inside
    _default_icon = THISDIR.joinpath("urlpreview.default.svg").read_text("utf-8")

    def run(self, parent, blocks: list[str]):
        directive = self.parse_blocks(blocks)
        u_url = directive.arguments[0]
        u_title = directive.options["title"]
        u_image = directive.options["image"]
        u_svg = directive.options["svg"]
        u_svg_size = directive.options["svg-size"]
        u_color = directive.options["color"]

        node_master = ElementTree.SubElement(parent, "div")
        node_master.set("class", f"{self.cssclass_prefix}-box")

        node_url = ElementTree.Element("a")
        node_url.set("href", u_url)

        node_div_image = ElementTree.Element("div")
        node_div_image.set("class", f"{self.cssclass_prefix}-image")

        node_div_details = ElementTree.Element("div")
        node_div_details.set("class", f"{self.cssclass_prefix}-details")

        node_title = ElementTree.Element("div")
        node_title.set("class", f"{self.cssclass_prefix}-title")
        self.parser.parseChunk(node_title, u_title)

        node_div_subtitle = ElementTree.Element("div")
        node_div_subtitle.set("class", f"{self.cssclass_prefix}-subtitle")

        node_subtitle_url = ElementTree.Element("a")
        node_subtitle_url.set("href", u_url)

        node_content = ElementTree.Element("div")
        node_content.set("class", f"{self.cssclass_prefix}-description")
        self.parser.parseChunk(node_content, directive.content)

        # if path to image file is given
        if u_image:
            img_path = u_image
            node_img = ElementTree.SubElement(node_div_image, "img")
            node_img.set("src", img_path)
            # intentionally empty, this is a decorative image with no meaning
            node_img.set("alt", "")

        # if instead we give a svg, read the svg file content
        elif u_svg:
            svg_path = Path(u_svg).resolve()
            try:
                svg_data = svg_path.read_text("utf-8")
            except Exception as error:
                raise Directive.DirectiveOptionError(
                    f"Cannot read SVG file '{svg_path}' provided by the svg option as '{u_svg}': {error}"
                ) from error

            # add color option to stylesheet of the image container
            if u_color:
                node_div_image.set("style", f"color: {u_color};")

            # modify the width/height attribute of the svg if specified
            if u_svg_size:
                # overwrite svg_data with the updated one
                svg_data = set_svg_size(
                    svg_data,
                    width=u_svg_size[0],
                    height=u_svg_size[1],
                )

            node_div_image.text = self.parser.md.htmlStash.store(svg_data)

        # else use default icon whihs is already html formatted
        else:
            node_div_image.text = self.parser.md.htmlStash.store(self._default_icon)

        # layout nodes

        node_master.append(node_url)
        node_master.append(node_div_image)
        node_master.append(node_div_details)
        node_div_details.append(node_title)
        node_div_details.append(node_div_subtitle)
        node_div_details.append(node_content)
        node_div_subtitle.append(node_subtitle_url)
