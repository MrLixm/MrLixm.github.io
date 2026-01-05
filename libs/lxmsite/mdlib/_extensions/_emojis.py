import os
from pathlib import Path
from xml.etree import ElementTree

from markdown.inlinepatterns import InlineProcessor
from .._md import LxmMarkdown


class EmojiInlineProcessor(InlineProcessor):
    """
    Args:
        emojis_dir: filesystem path to an existing directory with emoji image insides.
        md: markdown parser instance
    """

    PATTERN = r":emoji:\(([+\-\w]+)\)"
    md: LxmMarkdown

    def __init__(self, emojis_dir: Path, md: LxmMarkdown):
        super().__init__(self.PATTERN, md=md)
        self._emojis_dir = emojis_dir

    def _get_emoji_path(self, name: str) -> Path:
        if not self._emojis_dir.exists():
            raise FileNotFoundError(
                f"Provided emojis_dir '{self._emojis_dir}' does not exist.'"
            )

        emoji_paths: dict[str, Path] = {
            path.suffix: path for path in self._emojis_dir.glob(f"{name}.*")
        }
        emoji_path: Path = (
            emoji_paths.get(".png")
            or emoji_paths.get(".webp")
            or emoji_paths.get(".jpg")
        )
        if not emoji_path:
            raise ValueError(
                f"No emoji with name '{name}' found in '{self._emojis_dir}'"
            )
        return emoji_path

    def handleMatch(self, m, data):
        emoji_name = m.group(1)
        emoji_path = self._get_emoji_path(emoji_name)

        alt_text_path: Path = emoji_path.with_suffix(".alt.txt")
        alt_text: str = alt_text_path.read_text() if alt_text_path.exists() else ""

        # make path relative
        emoji_path = Path(os.path.relpath(emoji_path, self.md.paths_root))

        node = ElementTree.Element("img")
        node.set("src", emoji_path.as_posix())
        node.set("alt", alt_text)
        node.set("title", emoji_path.stem)
        node.set("class", "emoji-role inline")

        return node, m.start(0), m.end(0)

    def register(self, priority: int):
        self.md.inlinePatterns.register(self, "emoji", priority)
