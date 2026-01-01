import dataclasses
import logging
from pathlib import Path


from ._md import LxmMarkdown
from ._extensions import ExtractTitleTreeprocessor
from ._extensions import MetadataPreprocessor
from ._extensions import UrlPreviewDirective
from ._extensions import EmojiInlineProcessor
from ._extensions import IncludeDirectivePreprocessor
from ._extensions import PatcherTreeprocessor
from ._extensions import ImageGridDirective
from ._extensions import ImageGalleryDirective

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Document:
    title: str
    metadata: dict[str, str]
    html: str


def read_markdown(
    source: str,
    paths_root: Path,
    extension_settings: dict,
) -> Document:
    """
    Parse a Markdown document and return it as a html document.

    Args:
        source: a text document in Markdown format
        paths_root: a directory to use for resolving relative paths found in document
        extension_settings: optional configuration settings for the markdown extensions
    """
    reader = LxmMarkdown(
        paths_root=paths_root,
        extensions=[
            # builtins.extra
            "abbr",
            "attr_list",
            "def_list",
            "fenced_code",
            "footnotes",
            "md_in_html",
            "tables",
            # builtins
            "admonition",
            "toc",
            # external
            "pymdownx.superfences",
            "pymdownx.highlight",
        ],
        extension_configs=extension_settings,
        output_format="xhtml",
        tab_length=4,
    )

    title_extractor = ExtractTitleTreeprocessor(reader)
    title_extractor.register(1)

    meta_extractor = MetadataPreprocessor(reader)
    meta_extractor.register(10)

    include_directive = IncludeDirectivePreprocessor(reader)
    # really need to be executed before all others
    include_directive.register(900)

    urlpreview_directive = UrlPreviewDirective(reader.parser)
    urlpreview_directive.register(50)

    emojis_dir: Path = extension_settings.get("emojis", {}).get("directory")
    if emojis_dir:
        emoji_processor = EmojiInlineProcessor(emojis_dir=emojis_dir, md=reader)
        emoji_processor.register(52)
    else:
        LOGGER.warning(
            "no emojis/directory specific in settings; disabling emojis extension."
        )

    imagegrid = ImageGridDirective(reader.parser)
    imagegrid.register(55)

    default_template = extension_settings.get("image_gallery", {}).get(
        "default_template"
    )
    imagegallery = ImageGalleryDirective(
        default_class="image-gallery",
        default_template=default_template,
        parser=reader.parser,
    )
    imagegallery.register(56)

    table_classes: list[str] = extension_settings.get("patcher", {}).get(
        "table_classes", []
    )
    code_classes: list[str] = extension_settings.get("patcher", {}).get(
        "code_classes", []
    )
    link_headings: bool = extension_settings.get("patcher", {}).get(
        "link_headings", True
    )
    patcher_proc = PatcherTreeprocessor(
        md=reader,
        table_classes=table_classes,
        code_classes=code_classes,
        link_headings=link_headings,
    )
    patcher_proc.register(1)

    html = reader.convert(source)

    return Document(
        title=title_extractor.title,
        html=html,
        metadata=meta_extractor.metadata,
    )
