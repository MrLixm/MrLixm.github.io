import dataclasses
from pathlib import Path

import markdown

from ._extensions import ExtractTitleTreeprocessor
from ._extensions import MetadataPreprocessor
from ._extensions import UrlPreviewDirective


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
    reader = markdown.Markdown(
        extension_configs=settings,
        output_format="xhtml",
        tab_length=4,
    )

    title_extractor = ExtractTitleTreeprocessor(reader)
    title_extractor.register(1)

    meta_extractor = MetadataPreprocessor(reader)
    meta_extractor.register(10)

    urlpreview_directive = UrlPreviewDirective(reader.parser)
    urlpreview_directive.register(50)

    html = reader.convert(content)

    return Document(
        title=title_extractor.title,
        html=html,
        metadata=meta_extractor.metadata,
    )
