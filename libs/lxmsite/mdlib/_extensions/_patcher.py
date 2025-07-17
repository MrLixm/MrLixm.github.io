from xml.etree import ElementTree

from lxmsite.mdlib import LxmMarkdown
import markdown.treeprocessors


class PatcherTreeprocessor(markdown.treeprocessors.Treeprocessor):
    """
    Runs recursively on all the tree element to edit them.

    This is run with a low priority before any other processor so you will edit
    only the builtin syntax.
    """

    def __init__(
        self,
        md: LxmMarkdown,
        table_classes: list[str],
        code_classes: list[str],
        link_headings: bool,
    ):
        super().__init__(md)
        self._table_classes: str = " ".join(table_classes)
        self._code_classes: str = " ".join(code_classes)
        self._link_headings: bool = link_headings

    def run(self, root: ElementTree.Element):
        for index, element in enumerate(root):
            if element.tag == "table" and self._table_classes:
                current_class = element.get("class", "")
                new_class = self._table_classes + " " + current_class
                element.set("class", new_class.strip(" "))
                # remove element
                root[:] = [child for i, child in enumerate(root) if i is not index]
                wrapper = ElementTree.Element("div")
                wrapper.set("class", "table-wrapper")
                wrapper.append(element)
                root.insert(index, wrapper)

            elif element.tag == "code" and self._code_classes:
                current_class = element.get("class", "")
                new_class = self._code_classes + " " + current_class
                element.set("class", new_class.strip(" "))

            # we restructure the toc so we can make it floating on the side in css
            # XXX: it seems the same instance cam be inserted multiple times
            elif element.get("class") in ["toc", "toc-list"]:

                is_top_item = element.get("class") == "toc"
                element.set("class", "toc-list")
                root[:] = [child for i, child in enumerate(root) if i is not index]

                new_nav = ElementTree.Element("nav")
                new_nav.set("class", "toc")

                wrapper = ElementTree.Element("aside")
                wrapper.set("class", "toc-wrapper sidebar")

                new_title = ElementTree.Element("p")
                new_title.set("class", "topic-title")
                new_title.text = "Table Of Contents"

                # XXX: only the first instance must be floating on the side
                if is_top_item:
                    wrapper.append(new_nav)
                    new_nav.append(new_title)
                    new_nav.append(element)
                    root.insert(index, wrapper)
                else:
                    new_nav.append(new_title)
                    new_nav.append(element)
                    root.insert(index, new_nav)

            # add a backlink to the header itself
            elif (
                element.tag[0] == "h" and len(element.tag) == 2 and self._link_headings
            ):
                new_link = ElementTree.Element("a")
                new_link.set("href", "#" + element.get("id", ""))
                new_link.text = element.text
                for child in element:
                    element.remove(child)
                    new_link.append(child)
                element.append(new_link)
                element.text = None

            self.run(element)

    def register(self, priority: int):
        self.md.treeprocessors.register(self, "patcher", priority)
