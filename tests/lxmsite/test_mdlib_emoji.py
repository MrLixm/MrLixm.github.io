import markdown

from lxmsite.mdlib._extensions import EmojiInlineProcessor


def test__EmojiInlineProcessor(tmp_path):

    emoji_dir = tmp_path / "emojis"
    emoji_dir.mkdir()

    emoji_dir.joinpath("cat-tired.png").write_text("")
    emoji_dir.joinpath("explosion.png").write_text("")

    text1 = (
        "this is :anti:-capitalist, anti-bigotry software, made by people who are "
        "tired :emoji:(cat-tired) of ill-intended organisations and individuals, and would "
        "rather not have those around their creations :emoji:(explosion)\n"
    )

    reader = markdown.Markdown()
    directive = EmojiInlineProcessor(emoji_dir, relative_root=tmp_path, md=reader)
    directive.register(1)

    result = reader.convert(text1)

    print(result)
    assert result == (
        "<p>this is :anti:-capitalist, anti-bigotry software, made by people who are tired "
        '<img alt="" class="emoji-role inline" src="emojis/cat-tired.png" title="cat-tired" /> '
        "of ill-intended organisations and individuals, and "
        "would rather not have those around their creations "
        '<img alt="" class="emoji-role inline" src="emojis/explosion.png" title="explosion" />'
        "</p>"
    )
