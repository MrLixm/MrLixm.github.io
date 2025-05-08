from . import _abbreviation
from . import _pygments
from ._pygments import parse_code_to_node
from . import _admonitions
from ._admonitions import AdmonitionsTransform
from . import _urlpreview
from ._links import LinksTransform
from . import _include
from . import _image_grid
from ._contents import ContentsTransform
from . import _image_gallery
from . import _emojis


def register_extensions():

    from docutils.parsers.rst.roles import register_local_role

    register_local_role("abbr", _abbreviation.abbr_role)
    register_local_role("emoji", _emojis.docutils_emoji_role)

    from docutils.parsers.rst.directives import register_directive

    register_directive("code", _pygments.PygmentsCode)
    register_directive("code-block", _pygments.PygmentsCode)

    register_directive("attention", _admonitions.Attention)
    register_directive("caution", _admonitions.Caution)
    register_directive("danger", _admonitions.Danger)
    register_directive("error", _admonitions.Error)
    register_directive("hint", _admonitions.Hint)
    register_directive("important", _admonitions.Important)
    register_directive("note", _admonitions.Note)
    register_directive("tip", _admonitions.Tip)
    register_directive("warning", _admonitions.Warning)
    register_directive("admonition", _admonitions.Admonition)

    register_directive("highlight", _admonitions.HighlightBlock)

    register_directive("url-preview", _urlpreview.UrlPreview)

    register_directive("include", _include.Include)
    register_directive("image-grid", _image_grid.ImageGrid)
    register_directive("image-gallery", _image_gallery.ImageGallery)
    register_directive("image-frame", _image_gallery.ImageGalleryFrame)
