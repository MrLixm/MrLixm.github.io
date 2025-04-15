import docutils.nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive


class ImageGalleryFrameNode(docutils.nodes.container):
    """
    Dataclass for transfer of objects between directives.
    """

    def __init__(
        self,
        img_id: str,
        label_id: str,
        img_node: docutils.nodes.Element,
        label_node: docutils.nodes.Element,
        *children,
        **attributes,
    ):
        super().__init__(*children, **attributes)
        self.img_id = img_id
        self.label_id = label_id
        self.img_node = img_node
        self.label_node = label_node


def read_metadata_option(serialized: str | None) -> dict[str, str]:
    metadata = {}
    if not serialized:
        return metadata

    for line in serialized.splitlines():
        if not line.strip(" "):
            continue
        key, value = line.split(":", maxsplit=1)
        metadata[key] = value.strip(" ")

    return metadata


class ImageGalleryFrame(Directive):
    """
    The internal image part of an ImageGallery.

    We associate an image with its description and some metadata to display.

    Must not used outside an ImageGallery directive.
    """

    required_arguments = 3
    final_argument_whitespace = False
    has_content = True

    option_spec = {
        "classes": directives.unchanged,
        "metadata": directives.unchanged,
    }

    def run(self):
        self.assert_has_content()

        option_classes = (
            self.options["classes"].split(" ") if "classes" in self.options else []
        )

        image_id, label_id, image_path = self.arguments

        labeloptions = {"ids": [label_id], "for": image_id}
        labelnode = docutils.nodes.caption(**labeloptions)
        # content is RST formatted so parse it too.
        self.state.nested_parse(self.content, self.content_offset, labelnode)

        imgnode = docutils.nodes.image(uri=image_path, alt="", ids=[image_id])

        metadatanode = docutils.nodes.bullet_list(classes=["metadata"])
        metadata_option = (
            self.options["metadata"] if "metadata" in self.options else None
        )
        metadata = read_metadata_option(metadata_option)
        for metadata_key, metadata_value in metadata.items():
            valuenode = docutils.nodes.paragraph(metadata_value, metadata_value)
            itemnode = docutils.nodes.list_item(
                "",
                valuenode,
                title=metadata_key,
                classes=[metadata_key],
            )
            metadatanode.append(itemnode)

        wrap_node = docutils.nodes.container(classes=["image-wrapper"])
        # the link system is to have fullscreen image on click
        # inspired from https://sylvaindurand.org/overlay-image-in-pure-css/
        link_id = f"{image_id}-fullscreen"
        link_node = docutils.nodes.reference(
            refuri=f"#{link_id}",
        )
        link_overlay_node = docutils.nodes.reference(
            refuri=f"#_",
            classes=["img-fullscreen"],
            ids=[link_id],
        )
        img_overlay_node = imgnode.copy()

        link_node.append(imgnode)
        link_overlay_node.append(img_overlay_node)
        wrap_node.append(link_node)
        wrap_node.append(link_overlay_node)
        wrap_node.append(metadatanode)

        topnode = ImageGalleryFrameNode(
            img_id=image_id,
            label_id=label_id,
            img_node=wrap_node,
            label_node=labelnode,
            classes=["image-gallery-frame"] + option_classes,
        )
        return [topnode]


def option_id_list(argument: str | None):
    if not argument:
        raise ValueError("argument required but none supplied")
    return [i.strip(" ") for i in argument.split(",") if i.strip(" ")]


class ImageGallery(Directive):
    """
    A directive to showcase images and their caption with care.

    It's a 2 column layout, refered as "left" and "right".

    Its content may only contain ImageGalleryFrame directives.
    """

    required_arguments = 0
    final_argument_whitespace = False
    has_content = True

    option_spec = {
        "classes": directives.unchanged,
        "left": option_id_list,
        "right": option_id_list,
        "left-width": directives.nonnegative_int,
        "right-width": directives.nonnegative_int,
    }

    def run(self):
        self.assert_has_content()

        option_classes = (
            self.options["classes"].split(" ") if "classes" in self.options else []
        )

        option_left: list[str] = self.options["left"]
        option_right: list[str] = self.options["right"]
        option_left_width: int = self.options["left-width"]
        option_right_width: int = self.options["right-width"]

        topnode = docutils.nodes.container(
            classes=["image-gallery"] + option_classes,
        )
        leftnode = docutils.nodes.container(
            classes=["column", "left"],
            style=f"width: {option_left_width}%",
        )
        rightnode = docutils.nodes.container(
            classes=["column", "right"],
            style=f"width: {option_right_width}%",
        )
        responsivenode = docutils.nodes.container(
            classes=["column", "responsive"],
        )

        # // retrieve the images to layout

        content_buf = docutils.nodes.Element()
        # content is RST formatting so parse it too.
        self.state.nested_parse(self.content, self.content_offset, content_buf)
        node_by_id: dict[str, docutils.nodes.Element] = {}
        frame_nodes: list[ImageGalleryFrameNode] = []
        for content_child in content_buf.children:
            if isinstance(content_child, ImageGalleryFrameNode):
                if content_child.img_id in node_by_id:
                    raise ValueError(
                        f"duplicated image id for {content_child.img_node}"
                    )
                if content_child.label_id in node_by_id:
                    raise ValueError(
                        f"duplicated label id for {content_child.label_id}"
                    )
                node_by_id[content_child.img_id] = content_child.img_node
                node_by_id[content_child.label_id] = content_child.label_node
                frame_nodes.append(content_child)

        if not node_by_id:
            raise ValueError(f"No image frame found in content '{self.content}'")

        # // layout images created in content based on their id associated to left or right

        for left_id in option_left:
            matching_node = node_by_id.get(left_id, None)
            if not matching_node:
                raise ValueError(
                    f"Invalid '{left_id}' id given for :left: option: no image-frame with that id found."
                )
            leftnode.append(matching_node)

        for right_id in option_right:
            matching_node = node_by_id.get(right_id, None)
            if not matching_node:
                raise ValueError(
                    f"Invalid '{right_id}' id given for :right: option: no image-frame with that id found."
                )
            rightnode.append(matching_node)

        for frame_node in frame_nodes:
            # need copy because already parent to leftnode and rightnode
            responsivenode.append(frame_node.img_node.deepcopy())
            responsivenode.append(frame_node.label_node.deepcopy())

        topnode.extend([leftnode, rightnode, responsivenode])

        return [topnode]
