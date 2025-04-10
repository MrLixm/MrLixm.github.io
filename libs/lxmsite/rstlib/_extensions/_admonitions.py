import docutils.nodes
import docutils.parsers.rst.roles
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from docutils.transforms import Transform


class BaseAdmonition(Directive):
    """
    Copied from the docutils api, just simplified the code.
    """

    final_argument_whitespace = True
    option_spec = {
        "class": directives.class_option,
        "name": directives.unchanged,
    }
    has_content = True

    node_class = NotImplemented

    def run(self):
        self.assert_has_content()
        self.options = docutils.parsers.rst.roles.normalized_role_options(self.options)

        text = "\n".join(self.content)
        admonition_node = self.node_class(text, **self.options)
        admonition_type = self.node_class.__name__
        title = self.arguments[0] if self.arguments else admonition_type

        title_node = docutils.nodes.title("", title)
        admonition_node.insert(0, title_node)
        admonition_node["classes"].append(admonition_type)

        self.add_name(admonition_node)

        self.state.nested_parse(self.content, self.content_offset, admonition_node)
        return [admonition_node]


class Admonition(BaseAdmonition):

    required_arguments = 1
    node_class = docutils.nodes.admonition


class Attention(BaseAdmonition):

    node_class = docutils.nodes.attention


class Caution(BaseAdmonition):

    node_class = docutils.nodes.caution


class Danger(BaseAdmonition):

    node_class = docutils.nodes.danger


class Error(BaseAdmonition):

    node_class = docutils.nodes.error


class Hint(BaseAdmonition):

    node_class = docutils.nodes.hint


class Important(BaseAdmonition):

    node_class = docutils.nodes.important


class Note(BaseAdmonition):

    node_class = docutils.nodes.note


class Tip(BaseAdmonition):

    node_class = docutils.nodes.tip


class Warning(BaseAdmonition):

    node_class = docutils.nodes.warning


class AdmonitionsTransform(Transform):
    """
    This is mostly a copy of the builtin docutils admonition transform, but simplified (remove title localisation).

    This transform will convert admonition with specific classes to "generic" admonition class.
    """

    default_priority = 920

    def apply(self):
        for node in self.document.findall(docutils.nodes.Admonition):
            if isinstance(node, docutils.nodes.admonition):
                # ignore already generic-admonition
                continue
            # transform specific admonition into a generic one.
            admonition = docutils.nodes.admonition(
                node.rawsource,
                *node.children,
                **node.attributes,
            )
            node.replace_self(admonition)
