import dataclasses
import logging
from pathlib import Path
from xml.etree import ElementTree

from lxmsite import read_image_meta_file
from . import directive as Directive
from .directive import StrArrayOption

LOGGER = logging.getLogger(__name__)


class StrArrayOption2(StrArrayOption):
    # to preserve backward compatiblity with rst parser I created
    def unserialize(self, value: str) -> list[str]:
        return [v.strip(" ") for v in super().unserialize(value)]


def _read_metadata_option(serialized: str | None) -> dict[str, str]:
    metadata = {}
    if not serialized:
        return metadata

    print(repr(serialized))
    for line in serialized.splitlines():
        if not line.strip(" "):
            continue
        key, value = line.split(":", maxsplit=1)
        metadata[key] = value.strip(" ")

    return metadata


@dataclasses.dataclass
class ParsedImage:
    uri: str
    image_id: str
    label_id: str
    metadata: dict[str, str]
    caption: str


class ImageNode(ElementTree.Element):
    def __init__(
        self,
        image_id: str,
        label_id: str,
        image_node: ElementTree.Element,
        label_node: ElementTree.Element,
        classes: list[str],
    ):
        super().__init__("div")
        self.image_id = image_id
        self.label_id = label_id
        self.image_node = image_node
        self.label_node = label_node
        self.set("class", " ".join(classes))

        self.append(self.image_node)
        self.append(self.label_node)


class ImageGalleryFrameDirective(Directive.BaseDirectiveBlock):
    """
    The internal image part of an ImageGallery.

    We associate an image with its description and some metadata to display.

    Must not be used outside an ImageGallery directive.
    """

    name = "image-frame"
    expected_arguments = 3
    expected_content = False
    options_schema = {
        "classes": StrArrayOption2([]),
        "metadata": Directive.StrOption(""),
    }

    def _parse_image(self, parsed: Directive.ParsedDirective):
        image_id, label_id, image_uri = parsed.arguments

        metadata = {}

        if image_uri.endswith(".meta"):
            image_abs_path = self.md.mk_path_abs(Path(image_uri))
            meta_path = image_abs_path
            image_uri = image_uri.removesuffix(".meta")
            image_abs_path = self.md.mk_path_abs(Path(image_uri))

            if not image_abs_path.exists():
                LOGGER.warning(
                    f"Meta file path refers to a non-existing image path '{image_abs_path}'"
                )
            LOGGER.debug(f"reading meta file '{meta_path}'")
            try:
                metadata = read_image_meta_file(meta_path)
            except Exception:
                LOGGER.error(f"error while reading meta file '{meta_path}'")
                raise

        metadata_option = parsed.options["metadata"].strip("\n")
        metadata_overrides = _read_metadata_option(metadata_option)
        metadata.update(metadata_overrides)

        if parsed.content:
            caption = parsed.content
            for meta_name, meta_value in metadata.items():
                if f"{{{meta_name}}}" in caption:
                    caption = caption.format(**{meta_name: meta_value})
            metadata.pop("caption", None)
        else:
            caption = metadata.pop("caption", "")

        return ParsedImage(
            uri=image_uri,
            image_id=image_id,
            label_id=label_id,
            metadata=metadata,
            caption=caption,
        )

    def run(self, parent, blocks):
        directive = self.parse_blocks(blocks)
        image = self._parse_image(directive)
        option_classes = " ".join(directive.options["classes"])

        labelnode = ElementTree.Element("div")
        labelnode.set("id", image.label_id)
        labelnode.set("class", "caption" + option_classes)
        # caption is markdown formatted so parse it too
        self.parser.parseChunk(labelnode, image.caption)

        imgnode = ElementTree.Element("img")
        imgnode.set("src", image.uri)
        imgnode.set("alt", "")
        imgnode.set("id", image.image_id)

        metadatanode = ElementTree.Element("ul")
        metadatanode.set("class", "metadata")
        for metadata_key, metadata_value in image.metadata.items():
            itemnode = ElementTree.Element("li")
            itemnode.set("title", metadata_key)
            itemnode.set("class", metadata_key)

            valuenode = ElementTree.Element("p")
            valuenode.text = metadata_value

            itemnode.append(valuenode)
            metadatanode.append(itemnode)

        wrap_node = ElementTree.Element("div")
        wrap_node.set("class", "image-wrapper" + option_classes)
        # the link system is made to have fullscreen image on click
        # inspired from https://sylvaindurand.org/overlay-image-in-pure-css/
        link_id = f"{image.image_id}-fullscreen"
        link_node = ElementTree.Element("a")
        link_node.set("href", f"#{link_id}")

        link_overlay_node = ElementTree.Element("a")
        link_overlay_node.set("href", "#_")
        link_overlay_node.set("class", "img-fullscreen")
        link_overlay_node.set("id", link_id)

        img_overlay_node = imgnode

        link_node.append(imgnode)
        link_overlay_node.append(img_overlay_node)
        wrap_node.append(link_node)
        wrap_node.append(link_overlay_node)
        wrap_node.append(metadatanode)

        topnode = ImageNode(
            image_id=image.image_id,
            label_id=image.label_id,
            image_node=wrap_node,
            label_node=labelnode,
            classes=["image-gallery-frame"],
        )
        parent.append(topnode)


class ImageGalleryDirective(Directive.BaseDirectiveBlock):
    """
    A directive to showcase images and their caption with care.

    It's a 2 column layout, refered as "left" and "right".

    Its content may only contain ImageGalleryFrame directives.
    """

    name = "image-gallery"
    expected_arguments = 0
    expected_content = True
    options_schema = {
        "classes": StrArrayOption2([]),
        "left": StrArrayOption2([]),
        "right": StrArrayOption2([]),
        "left-width": Directive.IntOption(50),
        "right-width": Directive.IntOption(50),
    }

    def run(self, parent, blocks):
        directive = self.parse_blocks(blocks)

        u_classes: list[str] = directive.options["classes"]
        u_left: list[str] = directive.options["left"]
        u_right: list[str] = directive.options["right"]
        u_left_width: int = directive.options["left-width"]
        u_right_width: int = directive.options["right-width"]

        topnode_classes = ["image-gallery"] + u_classes
        topnode = ElementTree.Element("div")
        topnode.set("class", " ".join(topnode_classes))

        leftnode = ElementTree.Element("div")
        leftnode.set("class", "column left")
        leftnode.set("style", f"width: {u_left_width}%")

        rightnode = ElementTree.Element("div")
        rightnode.set("class", "column right")
        rightnode.set("style", f"width: {u_right_width}%")

        responsivenode = ElementTree.Element("div")
        responsivenode.set("class", "column responsive")

        # // retrieve the images to layout
        #   which are specified in the content as directives

        content_buf = ElementTree.Element("div")
        self.parser.parseChunk(content_buf, directive.content)
        node_by_id: dict[str, ElementTree.Element] = {}
        image_nodes: list[ImageNode] = []
        for content_child in content_buf:
            if not isinstance(content_child, ImageNode):
                continue
            if content_child.image_id in node_by_id:
                raise ValueError(f"duplicated image id for {content_child.image_id}")
            if content_child.label_id in node_by_id:
                raise ValueError(f"duplicated label id for {content_child.label_id}")
            node_by_id[content_child.image_id] = content_child.image_node
            node_by_id[content_child.label_id] = content_child.label_node
            image_nodes.append(content_child)

        if not node_by_id:
            raise ValueError(f"No image frame found in content '{directive.content}'")

        # // layout images created in content based on their id associated to left or right

        for left_id in u_left:
            matching_node = node_by_id.get(left_id, None)
            if matching_node is None:
                raise ValueError(
                    f"Invalid '{left_id}' id given for :left: option: no image-frame with that id found."
                )
            leftnode.append(matching_node)

        for right_id in u_right:
            matching_node = node_by_id.get(right_id, None)
            if matching_node is None:
                raise ValueError(
                    f"Invalid '{right_id}' id given for :right: option: no image-frame with that id found."
                )
            rightnode.append(matching_node)

        for image_node in image_nodes:
            # we could copy, but instance seems to be able to have multiple parent
            responsivenode.append(image_node.image_node)
            responsivenode.append(image_node.label_node)

        topnode.extend([leftnode, rightnode, responsivenode])
        parent.append(topnode)

    def register(self, priority):
        super().register(priority)
        image_frame_directive = ImageGalleryFrameDirective(self.parser)
        self.parser.blockprocessors.register(
            item=image_frame_directive,
            name=image_frame_directive.name,
            priority=priority + 1,
        )
