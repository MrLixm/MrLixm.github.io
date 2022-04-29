import os
import pprint
import re
import sys
from pathlib import Path

import docutils
import docutils.nodes
import docutils.io
from docutils.parsers import rst
from docutils.parsers.rst import directives
from pelican import signals


def set_svg_size(svg, width, height=None):
    """
    Quick & dirty way to modify the width height attribute of an svg.

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

    # update the width attribute
    new_svg = re.sub(
        pattern="""width=["-'](\\d+)["-']""",
        repl=f"""width=\"{width}\"""",
        string=svg,
    )
    # the width attribute was not existing, add it.
    if new_svg == svg:
        new_svg = re.sub(
            pattern="""<svg""",
            repl=f"""<svg width=\"{width}\"""",
            string=new_svg,
        )

    # update the height attribute
    new_svg = re.sub(
        pattern="""height=["-'](\\d+)["-']""",
        repl=f"""height=\"{height}\"""",
        string=new_svg,
    )
    # the height attribute was not existing, add it.
    if new_svg == svg:
        new_svg = re.sub(
            pattern="""<svg""",
            repl=f"""<svg height=\"{height}\"""",
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

    # a circle with a carved "link" icon inside
    __default_icon = """
<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M32 64C49.6731 64 64 49.6731 64 32C64 14.3269 49.6731 0 32 0C14.3269 0 0 14.3269 0 32C0 49.6731 14.3269 64 32 64ZM25.8761 22.825C21.6565 27.0446 21.6565 33.9042 25.8761 38.1239C26.72 38.9678 28.1049 38.9678 28.9489 38.1239C29.8361 37.28 29.8361 35.8951 28.9489 35.0511C26.3955 32.5193 26.3955 28.4079 28.9489 25.8761L36.5875 18.2375C39.1193 15.6841 43.2307 15.6841 45.7625 18.2375C48.3159 20.7693 48.3159 24.8807 45.7625 27.4125L44.7455 28.4512C45.3514 30.139 45.6327 31.9134 45.611 33.6879L48.8353 30.4636C53.0549 26.244 53.0549 19.3844 48.8353 15.1647C44.6156 10.9451 37.756 10.9451 33.5364 15.1647L25.8761 22.825ZM38.1239 25.8761C37.28 25.0322 35.8951 25.0322 35.0511 25.8761C34.1639 26.72 34.1639 28.1049 35.0511 28.9489C37.6045 31.4807 37.6045 35.5921 35.0511 38.1239L27.4125 45.7625C24.8807 48.3159 20.7693 48.3159 18.2375 45.7625C15.6841 43.2307 15.6841 39.1193 18.2375 36.5875L19.2545 35.5705C18.6486 33.861 18.3673 32.0866 18.389 30.3121L15.1647 33.5364C10.9451 37.756 10.9451 44.6156 15.1647 48.8353C19.3844 53.0549 26.244 53.0549 30.4636 48.8353L38.1239 41.175C42.3435 36.9554 42.3435 30.0958 38.1239 25.8761Z" fill="currentColor"/>
</svg>
    """

    # this should be set on registering to allow using pelican setup.
    pelican = None

    def run(self):

        # Process args
        url_txt = directives.uri(self.arguments[0])
        url_txt_p, _ = self.state.inline_text(url_txt, self.lineno)
        title_txt = self.options["title"]
        title_txt, _ = self.state.inline_text(title_txt, self.lineno)

        # Create nodes
        node_master = docutils.nodes.container()
        node_master["classes"] += ["l-url-box"]
        node_url = docutils.nodes.reference(refuri=url_txt)
        node_url["classes"] += ["l-url-a"]
        node_bdetail = docutils.nodes.container()
        node_bdetail["classes"] += ["l-url-box-details"]
        node_bimage = docutils.nodes.container()
        node_bimage["classes"] += ["l-url-box-image"]
        # title is a regular paragraph styled differently
        node_title = docutils.nodes.paragraph("", "", *title_txt)
        node_title["classes"] += ["l-url-title"]
        # sub-title is a regular paragraph styled differently
        node_subtitle = docutils.nodes.container()
        node_subtitle["classes"] += ["l-url-subtitle"]
        # the sub-title is the url
        node_st_url = docutils.nodes.reference(url_txt, url_txt, refuri=url_txt)
        # process the url description(=content)
        node_content = docutils.nodes.paragraph()
        node_content["classes"] += ["l-url-description"]
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
            # build the path as it might use the {static} or {filename} token.
            svg_uri = directives.uri(self.options.get("svg"))
            root = Path().cwd() / Path(self.pelican.settings["PATH"])
            svg_path = root / Path(svg_uri.format(filename=root, static=root))
            # read the svg file
            try:
                svg_file = docutils.io.FileInput(source_path=str(svg_path))
                svg_data = svg_file.read()
            except Exception as excp:
                raise self.severe(f"[{self.name}] Can't read file <{svg_path}>: {excp}")

            # process options :

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
            node_img = docutils.nodes.raw("", self.__default_icon, format="html")

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


def __register(pelican_object):
    """
    Called by Pelican signal
    """
    UrlPreview.pelican = pelican_object
    rst.directives.register_directive("url-preview", UrlPreview)

    return


def register():
    """
    For Pelican
    """
    signals.initialized.connect(__register)

    return
