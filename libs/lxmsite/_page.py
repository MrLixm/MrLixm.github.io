import dataclasses
import datetime
import enum
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PageMetadata:
    """
    Additional metadata about the page, bringing extra context to its content.

    This is mostly use in the htlm site head. See https://ogp.me/
    """

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name
    authors: list[str] = dataclasses.field(default_factory=list)
    keywords: list[str] = dataclasses.field(default_factory=list)

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang
    # https://www.w3.org/International/articles/language-tags/
    language: str = "en"

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel#icon
    icon: str = ""
    """
    link to an icon file, relative to the page it was extracted from.
    """

    title: str = ""  # https://ogp.me/#metadata
    type: str = ""  # https://ogp.me/#types
    image: str = ""  # https://ogp.me/#metadata
    """
    link to an image file, relative to the page it was extracted from.
    """
    image_alt: str = ""

    description: str = ""  # https://ogp.me/#optional

    # // anything else that is non-standardized

    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#http%3a%2f%2fpurl.org%2fdc%2felements%2f1.1%2fdate
    date_created: datetime.datetime | None = None
    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#http%3a%2f%2fpurl.org%2fdc%2felements%2f1.1%2fdate
    date_modified: datetime.datetime | None = None
    extras: dict[str, str] = dataclasses.field(default_factory=dict)

    def get(self, name: str) -> Any:
        """
        Get a metadata based on its name, no matter if it's a known attribute or an extra.
        """
        if name in vars(self):
            return getattr(self, name)
        if name in self.extras:
            return self.extras[name]

        available = list(vars(self)) + list(self.extras)
        raise ValueError(
            f"No metadata with name '{name}' found; "
            f"must be one of {','.join(available)}"
        )


class PageStatus(enum.Enum):
    published = enum.auto()
    unlisted = enum.auto()
    """
    page is built and published but not listed in shelf
    """


@dataclasses.dataclass
class PageResource:
    """
    A page is a markdown document that will be translated to a single web page.

    A page may be child of zero or one shelf.
    """

    title: str
    metadata: PageMetadata
    url_path: str
    """
    relative to the site root
    """
    html_content: str
    html_template: str | None = None
    """
    path of the template to use relative to the config TEMPLATE_ROOT
    """

    status: PageStatus = PageStatus.published

    stylesheets: list[str] = dataclasses.field(default_factory=list)
    """
    collections of link to stylesheets file, relative to the site root
    """

    def __str__(self):
        return f"<{self.url_path} ({self.title})>"

    @property
    def slug(self) -> str:
        """
        The last part of the url path (the page "url name")
        """
        return self.url_path.split("/")[-1]
