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
    file_path: Path,
    settings: dict,
) -> Document:
    """
    Parse a rst file as a docutils Publisher

    Args:
        file_path: fileysstem path to an existing rst file.
        settings: docutils settings overrides
    """
    content = file_path.read_text(encoding="utf-8")
    reader = LxmMarkdown(
        paths_root=file_path.parent,
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
        extension_configs=settings,
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

    emojis_dir: Path = settings.get("emojis", {}).get("directory")
    if emojis_dir:
        emoji_processor = EmojiInlineProcessor(emojis_dir=emojis_dir, md=reader)
        emoji_processor.register(52)
    else:
        LOGGER.warning(
            "no emojis/directory specific in settings; disabling emojis extension."
        )

    imagegrid = ImageGridDirective(reader.parser)
    imagegrid.register(55)

    imagegallery = ImageGalleryDirective(reader.parser)
    imagegallery.register(56)

    table_classes: list[str] = settings.get("patcher", {}).get("table_classes", [])
    code_classes: list[str] = settings.get("patcher", {}).get("code_classes", [])
    link_headings: bool = settings.get("patcher", {}).get("link_headings", True)
    patcher_proc = PatcherTreeprocessor(
        md=reader,
        table_classes=table_classes,
        code_classes=code_classes,
        link_headings=link_headings,
    )
    patcher_proc.register(1)

    html = reader.convert(content)

    return Document(
        title=title_extractor.title,
        html=html,
        metadata=meta_extractor.metadata,
    )
