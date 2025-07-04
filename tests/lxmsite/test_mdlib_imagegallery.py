import shutil

from lxmsite.mdlib import LxmMarkdown

from lxmsite.mdlib._extensions import ImageGalleryDirective


def test__ImageGalleryDirective(tmp_path, resources_dir):

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

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
        :classes: coolpic

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

    src_template = resources_dir / ".image-gallery.html.jinja2"
    dst_template = templates_dir / src_template.name
    shutil.copy(src_template, dst_template)

    reader = LxmMarkdown(paths_root=src_dir)
    directive = ImageGalleryDirective(
        default_class="image-gallery",
        default_template=dst_template.name,
        jinja_templates_root=templates_dir,
        parser=reader.parser,
    )
    directive.register(20)

    result = reader.convert(text1)

    # just a big copy-paste of what pytest display, didnt took time to review it
    assert result == (
        "<p>some heading</p>\n"
        '<div class="image-gallery">\n'
        '  <div class="column left" style="width: 35%">\n'
        '        <div class="image-wrapper coolpic">\n'
        '          <a href="#image1-fullscreen">\n'
        '            <img alt="" id="image1" src="../.static/profile-picture.jpg">\n'
        "          </a>\n"
        '          <a class="img-fullscreen" href="#_" id="image1-fullscreen">\n'
        '            <img alt="" src="../.static/profile-picture.jpg">\n'
        "          </a>\n"
        '          <ul class="metadata">\n'
        '              <li class="date" title="date">\n'
        "                <p>2024-11 early morning</p>\n"
        "              </li>\n"
        '              <li class="location" title="location">\n'
        "                <p>France - Lyon</p>\n"
        "              </li>\n"
        "          </ul>\n"
        "        </div>\n"
        "      \n"
        "  </div>\n"
        '  <div class="column right" style="width: 65%">\n'
        '        <div class="caption" id="label1">\n'
        "            <p><strong>hello</strong> world</p>\n"
        "        </div>\n"
        '        <div class="image-wrapper ">\n'
        '          <a href="#image2-fullscreen">\n'
        '            <img alt="" id="image2" src="../.static/cover-social.jpg">\n'
        "          </a>\n"
        '          <a class="img-fullscreen" href="#_" id="image2-fullscreen">\n'
        '            <img alt="" src="../.static/cover-social.jpg">\n'
        "          </a>\n"
        '          <ul class="metadata">\n'
        '              <li class="date" title="date">\n'
        "                <p>2024-11 early morning</p>\n"
        "              </li>\n"
        '              <li class="location" title="location">\n'
        "                <p>France - Lyon - Parc de la Tete d’Or</p>\n"
        "              </li>\n"
        '              <li class="film" title="film">\n'
        "                <p>35mm Kodak Gold 200</p>\n"
        "              </li>\n"
        '              <li class="lens" title="lens">\n'
        "                <p>Minolta MD 35mm</p>\n"
        "              </li>\n"
        "          </ul>\n"
        "        </div>\n"
        "      \n"
        '        <div class="caption" id="label2">\n'
        "            <p>some of the text descrption of the image\n"
        "that can span multiple lines</p>\n"
        "        </div>\n"
        "  </div>\n"
        '  <div class="column responsive" style="width: 100%">\n'
        '        <div class="image-wrapper coolpic">\n'
        '          <a href="#image1-fullscreen">\n'
        '            <img alt="" id="image1" src="../.static/profile-picture.jpg">\n'
        "          </a>\n"
        '          <a class="img-fullscreen" href="#_" id="image1-fullscreen">\n'
        '            <img alt="" src="../.static/profile-picture.jpg">\n'
        "          </a>\n"
        '          <ul class="metadata">\n'
        '              <li class="date" title="date">\n'
        "                <p>2024-11 early morning</p>\n"
        "              </li>\n"
        '              <li class="location" title="location">\n'
        "                <p>France - Lyon</p>\n"
        "              </li>\n"
        "          </ul>\n"
        "        </div>\n"
        "      \n"
        '        <div class="caption" id="label1">\n'
        "            <p><strong>hello</strong> world</p>\n"
        "        </div>\n"
        '        <div class="image-wrapper ">\n'
        '          <a href="#image2-fullscreen">\n'
        '            <img alt="" id="image2" src="../.static/cover-social.jpg">\n'
        "          </a>\n"
        '          <a class="img-fullscreen" href="#_" id="image2-fullscreen">\n'
        '            <img alt="" src="../.static/cover-social.jpg">\n'
        "          </a>\n"
        '          <ul class="metadata">\n'
        '              <li class="date" title="date">\n'
        "                <p>2024-11 early morning</p>\n"
        "              </li>\n"
        '              <li class="location" title="location">\n'
        "                <p>France - Lyon - Parc de la Tete d’Or</p>\n"
        "              </li>\n"
        '              <li class="film" title="film">\n'
        "                <p>35mm Kodak Gold 200</p>\n"
        "              </li>\n"
        '              <li class="lens" title="lens">\n'
        "                <p>Minolta MD 35mm</p>\n"
        "              </li>\n"
        "          </ul>\n"
        "        </div>\n"
        "      \n"
        '        <div class="caption" id="label2">\n'
        "            <p>some of the text descrption of the image\n"
        "that can span multiple lines</p>\n"
        "        </div>\n"
        "  </div></div>\n"
        "<p>some paragraph</p>"
    )


def test__ImageGalleryDirective__template_option(tmp_path, resources_dir):

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    template_2 = templates_dir / "template2.html"
    template_2.write_text("<p>{{Columns['left']['children'][0]['id']}}</p>")

    text1 = """
some heading

.. image-gallery::
    :left: image1
    :right: label1, image2, label2
    :left-width: 35
    :right-width: 65
    :template: template2.html

    .. image-frame:: image1 label1 ../.static/cover-social.jpg

    .. image-frame:: image2 label2 ../.static/cover-social.jpg
    
        some of the text descrption of the image
        that can span multiple lines

some paragraph

    """

    reader = LxmMarkdown(paths_root=tmp_path)
    directive = ImageGalleryDirective(
        default_class="image-gallery",
        default_template="",
        jinja_templates_root=templates_dir,
        parser=reader.parser,
    )
    directive.register(20)

    result = reader.convert(text1)
    assert result == (
        "<p>some heading</p>\n"
        '<div class="image-gallery"><p>image1</p></div>\n'
        "<p>some paragraph</p>"
    )
