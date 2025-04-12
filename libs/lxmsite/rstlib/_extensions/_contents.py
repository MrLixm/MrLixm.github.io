import docutils.nodes
from docutils.transforms import Transform
import docutils.transforms.parts


class ContentsTransform(Transform):
    """
    Modify the node structure of the table of content so we can make it floating in css.

    This requires to add 2 intermediate nodes:

    - one "aside" that wraps the whole original node
    - one "div" that wraps the original bullet list of contents
    """

    default_priority = docutils.transforms.parts.Contents.default_priority + 10

    def apply(self):

        def _condition(n):
            return isinstance(n, docutils.nodes.topic) and "contents" in n["classes"]

        nodes = list(self.document.findall(condition=_condition, include_self=False))
        node: docutils.nodes.topic
        for node in nodes:

            parent = node.parent
            parent_index = parent.index(node)
            parent.remove(node)
            newnode = docutils.nodes.sidebar(classes=["toc-wrapper"])
            newnode.append(node)
            parent.insert(parent_index, newnode)

            for index, child in enumerate(node.children):
                if isinstance(child, docutils.nodes.bullet_list):
                    newchild = docutils.nodes.container(classes=["toc-list"])
                    newchild.append(child)
                    node.remove(child)
                    node.insert(index, newchild)
