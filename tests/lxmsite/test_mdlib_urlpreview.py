import markdown

from lxmsite.mdlib._extensions._urlpreview import UrlPreviewDirective


def test__UrlPreviewDirective():
    text1 = """
some heading

.. url-preview:: https://liamcollod.xyz
    :title: check my cool website !
    :image: ./cover.jpg
    
    I spent a lot of time designing it 🥺
    
some paragraph

    """

    reader = markdown.Markdown()
    directive = UrlPreviewDirective(reader.parser)
    reader.parser.blockprocessors.register(directive, "urlpreview", 20)

    result = reader.convert(text1)

    print(result)
    assert result == (
        "<p>some heading</p>\n"
        '<div class="url-preview-box">'
        '<a class="reference" href="https://liamcollod.xyz"></a>'
        '<div class="url-preview-image"><img alt="" src="./cover.jpg" /></div>\n'
        '<div class="url-preview-details">\n'
        '<div class="url-preview-title">\n'
        "<p>check my cool website !</p>\n"
        "</div>\n"
        '<div class="url-preview-subtitle">'
        '<a href="https://liamcollod.xyz">https://liamcollod.xyz</a>'
        "</div>\n"
        '<div class="url-preview-description">\n'
        "<p>I spent a lot of time designing it 🥺</p>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n"
        "<p>some paragraph</p>"
    )
