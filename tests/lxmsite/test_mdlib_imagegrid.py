from lxmsite.mdlib import LxmMarkdown
from lxmsite.mdlib._extensions import _image_grid
from lxmsite.mdlib._extensions import ImageGridDirective


class FakeImage:
    width = 1280
    height = 500


def test__ImageGridDirective(monkeypatch, tmp_path):

    def open_image(*args, **kwargs):
        return FakeImage()

    monkeypatch.setattr(_image_grid.PIL.Image, "open", open_image)

    text1 = """
some heading

.. image-grid::
    :link-images: 1

    ../.static/images/cover-social.jpg
    ../.static/images/profile-picture.jpg

    ../.static/images/profile-picture.jpg some caption that will be displayed under
    ../.static/images/cover-social.jpg the caption can span
        multiple lines if it's too long.
    ../.static/images/profile-picture.jpg
    
some paragraph

    """

    reader = LxmMarkdown(paths_root=tmp_path)
    directive = ImageGridDirective(reader.parser)
    directive.register(20)

    result = reader.convert(text1)

    print(result)
    assert result == (
        "<p>some heading</p>\n"
        '<div class="image-grid ">\n'
        # row1
        '<div class="image-grid-row">'
        # row1.item1
        '<a class="image-reference" href="..\\.static\\images\\cover-social.jpg">'
        '<figure style="width: 50.000%;">'
        '<img alt="" src="..\\.static\\images\\cover-social.jpg" />'
        "</figure></a>"
        # row1.item2
        '<a class="image-reference" href="..\\.static\\images\\profile-picture.jpg">'
        '<figure style="width: 50.000%;">'
        '<img alt="" src="..\\.static\\images\\profile-picture.jpg" />'
        "</figure></a>"
        "</div>\n"
        # row2
        '<div class="image-grid-row">'
        # row2.item1
        '<a class="image-reference" href="..\\.static\\images\\profile-picture.jpg">'
        '<figure style="width: 33.333%;">'
        '<img alt="some caption that will be displayed under" src="..\\.static\\images\\profile-picture.jpg" />'
        "<figcaption><p>some caption that will be displayed under</p></figcaption>"
        "</figure></a>"
        # row2.item2
        '<a class="image-reference" href="..\\.static\\images\\cover-social.jpg">'
        '<figure style="width: 33.333%;">'
        '<img alt="the caption can span multiple lines if it\'s too long." src="..\\.static\\images\\cover-social.jpg" />'
        "<figcaption><p>the caption can span multiple lines if it's too long.</p></figcaption>"
        "</figure></a>"
        # row2.item3
        '<a class="image-reference" href="..\\.static\\images\\profile-picture.jpg">'
        '<figure style="width: 33.333%;">'
        '<img alt="" src="..\\.static\\images\\profile-picture.jpg" />'
        "</figure></a></div>\n"
        "</div>\n"
        "<p>some paragraph</p>"
    )
