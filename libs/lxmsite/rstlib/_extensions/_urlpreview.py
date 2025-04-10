import os
import re
from pathlib import Path

import docutils
import docutils.nodes
import docutils.io
from docutils.parsers import rst
from docutils.parsers.rst import directives

THISDIR = Path(__file__).parent


def set_svg_size(svg, width, height=None):
    """
    Quick & dirty way to modify the width height attribute of a svg.

    Args:
        svg(str): svg as string.
        width(int or str):
        height(int or str or None):

    Returns:
        str:
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


def size_argument(argument):
    """
    Args:
        argument(str): directive option argument

    Returns:
        tuple:
            tuple of 2 avlue, with width at index 0 and height at 1
    """
    if not argument:
        return argument

    if "px" in argument or "%" in argument:
        raise ValueError(
            "[size_argument] The argument passed should cannot have 'px' or"
            " '%', it should be made of floats or ints."
        )

    size = argument.split(" ", 1)
    if len(size) == 2:
        output = tuple(size)
    else:
        output = (size[0], size[0])

    return output


class UrlPreview(rst.Directive):
    """
    As you can't embed url preview without Js, this will make it looks more
    pretty than a static url.
    ::

        [-------][   Title            ]
        [ Image ][   Url              ]
        [_______][   Description      ]

    * ``Image`` is based on the instance ``__type`` attribute
    * ``Url`` is teh directive argument
    * ``Title`` is a directive :title: option
    * ``Description`` is the directive's content.

    Here is the rst syntax:
    ::

        .. url-preview:: https://mysuperlink.xyz
            :title: Check my super link !
            :image: {static}/img/myimg.jpg

    """

    final_argument_whitespace = True
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "title": directives.unchanged_required,
        "image": directives.uri,
        "svg": directives.uri,
        "color": directives.unchanged,
        "svg-size": size_argument,
    }
    cssclass_prefix = "url-preview"

    # a circle with a carved "link" icon inside
    _default_icon = THISDIR.joinpath("urlpreview.default.svg").read_text("utf-8")

    def run(self):

        # Process args
        url_txt = directives.uri(self.arguments[0])
        url_txt_p, _ = self.state.inline_text(url_txt, self.lineno)
        title_txt = self.options["title"]
        title_txt, _ = self.state.inline_text(title_txt, self.lineno)

        # Create nodes
        node_master = docutils.nodes.container()
        node_master["classes"] += [f"{self.cssclass_prefix}-box"]
        node_url = docutils.nodes.reference(refuri=url_txt)
        node_bdetail = docutils.nodes.container()
        node_bdetail["classes"] += [f"{self.cssclass_prefix}-details"]
        node_bimage = docutils.nodes.container()
        node_bimage["classes"] += [f"{self.cssclass_prefix}-image"]
        # title is a regular paragraph styled differently
        node_title = docutils.nodes.paragraph("", "", *title_txt)
        node_title["classes"] += [f"{self.cssclass_prefix}-title"]
        # sub-title is a regular paragraph styled differently
        node_subtitle = docutils.nodes.container()
        node_subtitle["classes"] += [f"{self.cssclass_prefix}-subtitle"]
        # the sub-title is the url
        node_st_url = docutils.nodes.reference(url_txt, url_txt, refuri=url_txt)
        # process the url description(=content)
        node_content = docutils.nodes.container()
        node_content["classes"] += [f"{self.cssclass_prefix}-description"]
        # content is RST formatting so parse it too.
        self.state.nested_parse(self.content, self.content_offset, node_content)

        # we determine wht's going to be use in the image section
        # if path to image file is given
        if "image" in self.options and self.options.get("image"):
            img_path = self.options.get("image")
            img_path = directives.uri(img_path)
            node_img = docutils.nodes.image()
            node_img["uri"] = img_path

        # if instead we give a svg, read the svg file content
        elif "svg" in self.options and self.options.get("svg"):
            svg_uri = directives.uri(self.options.get("svg"))
            page_dir = os.getcwd()
            svg_path = Path(page_dir, svg_uri)
            try:
                svg_data = svg_path.read_text("utf-8")
            except Exception as error:
                raise self.severe(
                    f"[{self.name}] Can't read file <{svg_path}>: {error}"
                )

            # add color option to stylsheet of the image container
            if "color" in self.options and self.options.get("color"):
                node_bimage["style"] = f"color: {self.options.get('color')};"

            # modify the width/height attribute of the svg if specified
            if "svg-size" in self.options and self.options.get("svg-size"):
                size = self.options.get("svg-size")
                # overwrite svg_data with the updated one
                svg_data = set_svg_size(svg_data, width=size[0], height=size[1])

            node_img = docutils.nodes.raw("", svg_data, format="html")

        # else use default icon wich is a svg representing a link in a circle.
        else:
            node_img = docutils.nodes.raw("", self._default_icon, format="html")

        # build node tree
        node_master += node_url
        node_master += node_bimage
        node_master += node_bdetail
        node_bimage += node_img
        node_bdetail += node_title
        node_bdetail += node_subtitle
        node_subtitle += node_st_url
        node_bdetail += node_content

        return [node_master]
