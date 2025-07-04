import copy
import logging
from pathlib import Path
from xml.etree import ElementTree

import jinja2
from markdown.blockparser import BlockParser

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

    for line in serialized.splitlines():
        if not line.strip(" "):
            continue
        key, value = line.split(":", maxsplit=1)
        metadata[key] = value.strip(" ")

    return metadata


class ImageNode(ElementTree.Element):
    def __init__(
        self,
        uri: str,
        image_id: str,
        label_id: str,
        metadata: dict[str, str],
        caption: str,
        classes: list[str],
    ):
        super().__init__("div")
        self.uri = uri
        self.image_id = image_id
        self.label_id = label_id
        self.metadata = metadata
        self.caption = caption
        self.classes = classes


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

        # // parse caption as markdown, to html
        # we need a new md instance as we are currently parsing a document using it
        reader = copy.deepcopy(self.md)
        reader.reset()
        caption = reader.convert(caption)

        classes = parsed.options["classes"]

        return ImageNode(
            uri=image_uri,
            image_id=image_id,
            label_id=label_id,
            metadata=metadata,
            caption=caption,
            classes=classes,
        )

    def run(self, parent, blocks):
        directive = self.parse_blocks(blocks)
        image_node = self._parse_image(directive)
        parent.append(image_node)


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
        "template": Directive.StrOption(""),
    }

    def __init__(
        self,
        default_class: str,
        default_template: str,
        jinja_templates_root: Path,
        parser: BlockParser,
    ):
        super().__init__(parser)
        self._default_class = default_class
        self._default_template = default_template
        self._jinja_templates_root = jinja_templates_root

    @staticmethod
    def convert_image_node_to_dict(current_id: str, image_node: ImageNode):
        node_type = "image" if current_id == image_node.image_id else "label"
        return {
            "type": node_type,
            "id": current_id,
            "uri": image_node.uri,
            "metadata": image_node.metadata,
            "caption": image_node.caption,
            "classes": " ".join(image_node.classes),
        }

    def run(self, parent, blocks):
        directive = self.parse_blocks(blocks)

        u_classes: list[str] = directive.options["classes"]
        u_left: list[str] = directive.options["left"]
        u_right: list[str] = directive.options["right"]
        u_left_width: int = directive.options["left-width"]
        u_right_width: int = directive.options["right-width"]
        u_template: str = directive.options["template"]

        # // retrieve the images to layout
        #   which are specified in the content as directives

        content_buf = ElementTree.Element("div")
        self.parser.parseChunk(content_buf, directive.content)
        node_by_id: dict[str, ImageNode] = {}
        for content_child in content_buf:
            if not isinstance(content_child, ImageNode):
                continue
            if content_child.image_id in node_by_id:
                raise ValueError(f"duplicated image id for {content_child.image_id}")
            if content_child.label_id in node_by_id:
                raise ValueError(f"duplicated label id for {content_child.label_id}")

            node_by_id[content_child.image_id] = content_child
            node_by_id[content_child.label_id] = content_child

        if not node_by_id:
            raise ValueError(f"No image frame found in content '{directive.content}'")

        # // layout images created in content based on their id associated to left or right

        configuration = {
            "left": {
                "width": u_left_width,
                "children": [],
            },
            "right": {
                "width": u_right_width,
                "children": [],
            },
            "responsive": {
                "width": 100,
                "children": [],
            },
        }

        for left_id in u_left:
            matching_node = node_by_id.get(left_id, None)
            if matching_node is None:
                raise ValueError(
                    f"Invalid '{left_id}' id given for :left: option: no image-frame with that id found."
                )
            node_config = self.convert_image_node_to_dict(left_id, matching_node)
            configuration["left"]["children"].append(node_config)

        for right_id in u_right:
            matching_node = node_by_id.get(right_id, None)
            if matching_node is None:
                raise ValueError(
                    f"Invalid '{right_id}' id given for :right: option: no image-frame with that id found."
                )
            node_config = self.convert_image_node_to_dict(right_id, matching_node)
            configuration["right"]["children"].append(node_config)

        for node_id, image_node in node_by_id.items():
            node_config = self.convert_image_node_to_dict(node_id, image_node)
            configuration["responsive"]["children"].append(node_config)

        jinja_env = jinja2.Environment(
            undefined=jinja2.StrictUndefined,
            loader=jinja2.FileSystemLoader(self._jinja_templates_root),
        )
        template_name = u_template or self._default_template
        template = jinja_env.get_template(template_name)

        configuration = {"Columns": configuration}
        output = template.render(**configuration)

        topnode_classes = [self._default_class] + u_classes
        topnode = ElementTree.Element("div")
        topnode.set("class", " ".join(topnode_classes))
        topnode.text = self.parser.md.htmlStash.store(output)
        parent.append(topnode)

    def register(self, priority):
        super().register(priority)
        image_frame_directive = ImageGalleryFrameDirective(self.parser)
        self.parser.blockprocessors.register(
            item=image_frame_directive,
            name=image_frame_directive.name,
            priority=priority + 1,
        )
