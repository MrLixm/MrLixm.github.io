from lxmsite.mdlib import LxmMarkdown

from lxmsite.mdlib._extensions import ImageGalleryDirective


def test__ImageGalleryDirective(tmp_path):

    src_dir = tmp_path / "src"
    src_dir.mkdir()

    static_dir = tmp_path / ".static"
    static_dir.mkdir()

    pp_meta_path = static_dir / "profile-picture.jpg.meta"
    pp_meta_path.write_text(
        "__format__: 1\n"
        "date: 2024-11 early morning\n"
        "location: France - Lyon\n"
        "caption: **hello** world"
    )

    text1 = """
some heading

.. image-gallery::
    :left: image1
    :right: label1, image2, label2
    :left-width: 35
    :right-width: 65

    .. image-frame:: image1 label1 ../.static/profile-picture.jpg.meta

    .. image-frame:: image2 label2 ../.static/cover-social.jpg
        :metadata:
             date: 2024-11 early morning
             location: France - Lyon - Parc de la Tete d’Or
             film: 35mm Kodak Gold 200
             lens: Minolta MD 35mm
 
        some of the text descrption of the image
        that can span multiple lines
    
some paragraph

    """

    reader = LxmMarkdown(paths_root=src_dir)
    directive = ImageGalleryDirective(reader.parser)
    directive.register(20)

    result = reader.convert(text1)

    print(result)
    # just a big copy-paste of what pytest display, didnt took time to review it
    assert result == (
        "<p>some heading</p>\n"
        '<div class="image-gallery">\n'
        '<div class="column left" style="width: 35%">\n'
        '<div class="image-wrapper"><a href="#image1-fullscreen"><img alt="" '
        'id="image1" src="../.static/profile-picture.jpg.meta" /></a><a '
        'class="img-fullscreen" href="#_" id="image1-fullscreen"><img alt="" '
        'id="image1" src="../.static/profile-picture.jpg.meta" /></a><ul '
        'class="metadata">\n'
        '<li class="date" title="date">\n'
        "<p>2024-11 early morning</p>\n"
        "</li>\n"
        '<li class="location" title="location">\n'
        "<p>France - Lyon</p>\n"
        "</li>\n"
        "</ul>\n"
        "</div>\n"
        "</div>\n"
        '<div class="column right" style="width: 65%">\n'
        '<div class="caption" id="label1">\n'
        "<p><strong>hello</strong> world</p>\n"
        "</div>\n"
        '<div class="image-wrapper"><a href="#image2-fullscreen"><img alt="" '
        'id="image2" src="../.static/cover-social.jpg" /></a><a '
        'class="img-fullscreen" href="#_" id="image2-fullscreen"><img alt="" '
        'id="image2" src="../.static/cover-social.jpg" /></a><ul class="metadata">\n'
        '<li class="date" title="date">\n'
        "<p>2024-11 early morning</p>\n"
        "</li>\n"
        '<li class="location" title="location">\n'
        "<p>France - Lyon - Parc de la Tete d’Or</p>\n"
        "</li>\n"
        '<li class="film" title="film">\n'
        "<p>35mm Kodak Gold 200</p>\n"
        "</li>\n"
        '<li class="lens" title="lens">\n'
        "<p>Minolta MD 35mm</p>\n"
        "</li>\n"
        "</ul>\n"
        "</div>\n"
        '<div class="caption" id="label2">\n'
        "<p>some of the text descrption of the image\n"
        "that can span multiple lines</p>\n"
        "</div>\n"
        "</div>\n"
        '<div class="column responsive">\n'
        '<div class="image-wrapper"><a href="#image1-fullscreen"><img alt="" '
        'id="image1" src="../.static/profile-picture.jpg.meta" /></a><a '
        'class="img-fullscreen" href="#_" id="image1-fullscreen"><img alt="" '
        'id="image1" src="../.static/profile-picture.jpg.meta" /></a><ul '
        'class="metadata">\n'
        '<li class="date" title="date">\n'
        "<p>2024-11 early morning</p>\n"
        "</li>\n"
        '<li class="location" title="location">\n'
        "<p>France - Lyon</p>\n"
        "</li>\n"
        "</ul>\n"
        "</div>\n"
        '<div class="caption" id="label1">\n'
        "<p><strong>hello</strong> world</p>\n"
        "</div>\n"
        '<div class="image-wrapper"><a href="#image2-fullscreen"><img alt="" '
        'id="image2" src="../.static/cover-social.jpg" /></a><a '
        'class="img-fullscreen" href="#_" id="image2-fullscreen"><img alt="" '
        'id="image2" src="../.static/cover-social.jpg" /></a><ul class="metadata">\n'
        '<li class="date" title="date">\n'
        "<p>2024-11 early morning</p>\n"
        "</li>\n"
        '<li class="location" title="location">\n'
        "<p>France - Lyon - Parc de la Tete d’Or</p>\n"
        "</li>\n"
        '<li class="film" title="film">\n'
        "<p>35mm Kodak Gold 200</p>\n"
        "</li>\n"
        '<li class="lens" title="lens">\n'
        "<p>Minolta MD 35mm</p>\n"
        "</li>\n"
        "</ul>\n"
        "</div>\n"
        '<div class="caption" id="label2">\n'
        "<p>some of the text descrption of the image\n"
        "that can span multiple lines</p>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n"
        "<p>some paragraph</p>"
    )
