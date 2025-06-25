from xml.etree import ElementTree

import markdown.treeprocessors


def aggregate_children_text(element: ElementTree.Element, parent: str = "") -> str:
    """
    Recursively parse the given element to return a concatenated string of its self+children text.
    """
    parent += element.text or ""
    for child in element:
        parent = aggregate_children_text(child, parent)
    parent += element.tail or ""
    return parent.rstrip("\n")


class ExtractTitleTreeprocessor(markdown.treeprocessors.Treeprocessor):
    title: str | None = None

    def run(self, root: ElementTree.Element) -> ElementTree.Element:
        for element in root:
            if element.tag == "h1":
                self.title = aggregate_children_text(element)
            break
        return root

    def register(self) -> None:
        self.md.treeprocessors.register(self, "extract_title", priority=1)
