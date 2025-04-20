Site Developer Documentation
############################

:description: The developer documentation for building this html site.

.. container:: nav-button

    `\< previous page <test.html>`_ `next page \> <test.html>`_

.. contents:: Table Of Contents

This is a static website, meaning all its content is generated before being
published online and every page correspond to a single html file.

The published website is just HTML and CSS, that are generated using a custom
workflow based on Python, rst and Jinja.

Basics
------

The philoshophy for this website is that the source file structure represents
the published site structure. It tries to be as explicit as possible.

So let's say your website is published at ``https://mywebsite.com``, then
``https://mywebsite.com/blog/index.html`` implies there must be a
``/blog/index.rst`` file. Same for ``https://mywebsite.com/images/art.jpg`` which
implies ``images/art.jpg`` must exist in the source file structure.

.. hint::

    A common convention for the web is that ``https://mywebsite.com/blog`` will redirect
    to ``https://mywebsite.com/blog/index.html`` which is why you will usually
    create an ``index.rst`` file in every directory.

    (this convention depends on the web server serving your files).


It is possible to exclude some file in the source hierarchy to be collected.
This is achieved using the ``.siteignore`` mechanism.

Another feature which affect the file structure is *shelves*. A shelf will
allow to group and browse multiple pages.

.. caution::

    All paths/urls are assumed to be made without whitespace. Adding whitespace
    may have unexpected consequences when being parsed.


.siteignore files
=================

A .siteignore is a file that indicate which path must not be collected to build
the site. It can be fond at root but also in any directory.

It's file format is as follow:

- each line defines a "path expression" which resolves to multiple paths to ignore.
- a line can be empty
- *path expression* follow the python `glob <https://docs.python.org/3/library/glob.html>`_ syntax
- *path expression* MUST be relative to the .siteignore file directory
- *path expression* may resolve to non-existing paths

.siteignore files are cumulative, this means that their paths are made absolute
then grouped together and its this list which is used to ignore paths.

Example::

   .siteignore
      **/.*.html
      *.txt
   index.html
   somestuff.txt
   blog/
      .siteignore
         **/*.cpp
      index.html
      .template.html
      snippet.cpp
      resource.txt

In the above we have an expression at root that will ignore all html files
that starts with a dot, the ``**`` is a glob pattern which express recursion,
meaning that ``blog/.template.html`` will be ignored. We will also ignore
``somestuff.txt`` but NOT ``resource.txt``.

We then ignore ``blog/snippet.cpp``.

shelf feature
=============

TBD


build process
=============

This is how the source file structure is parsed the site final file structure:

- collect all file paths in the source directory and ignore some paths using the .siteignore files.
- read and convert rst file as pages
- collect shelves
- render pages with their template and write to disk
- write shelves pages to disk
- copy static resources

See ``lxmsite._build`` for the code implementation.


Creating a page
---------------

All pages MUST have an .rst file, even if it just have a title. You are then
free to define its content using the standard rst syntax or to manually
create the html with a template.

writing rst content
===================

See https://docutils.sourceforge.io/docs/user/rst/quickref.html.

page metadata
=============

This are the fields that are understood as page metadata:

=================  ===========
name               description
=================  ===========
``authors``        Comma separated list of person who authored the page. See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name
``tags``           List of tags matching the page topics
``language``       Language of the page. As standardized by https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang and https://www.w3.org/International/articles/language-tags/
``title``          Additional override if the rst file title is not desired. See https://ogp.me/#metadata
``type``           Caracterize the kind of content of the page. As standardized by https://ogp.me/#types
``image``          Relative file path to the image to use as cover for the page. See https://ogp.me/#metadata
``image-alt``      Alt text to describe the content of the ``image`` field.
``description``    Short, human-readable summary of the page content. See https://ogp.me/#optional
``date-created``   Date at which the page was created. Format is ``YYYY-MM-DDThh:mm``. See https://en.wikipedia.org/wiki/ISO_8601
``date-modified``  Date at which the page was last modified. Format is ``YYYY-MM-DDThh:mm``. See https://en.wikipedia.org/wiki/ISO_8601
``template``       Relative file path to the html template to use for rendering the page.
``stylesheets``    Comma separated list of stylesheet path relative to the page. Prefix with a + to inherit the parent stylesheets.
``status``         either ``published`` (no effect) or ``unlisted`` (will be excluded from being listed in its parent shelf)
=================  ===========

Some extra fields may be used depending on the context:

blog context:
    =============  ===========
    name           description
    =============  ===========
    ``category``   (optional) which type of content is the page
    ``cover``      (optional) path to an image to display on top of the blog post.
    ``cover-alt``  (optional) the alt text for the cover image.
    =============  ===========

resources context:
    =============  ===========
    name           description
    =============  ===========
    ``category``   (optional) which type of content is the page
    =============  ===========

A field is specified under the page title as ``:field-name: value``. Example:

.. code:: rst

   my page
   =======

   :description: this is quite a long summary that would be
      cool to wrap on 2 lines.

.. note::

   - All file paths must be relative to the parent directory of the rst file.
   - All file paths use posix-like forward slashes, like ``my/path/to/file``.
   - All file paths refer to the built site, not files in the source directory.

See ``lxmsite._page`` for the code implementation.


rst directives
==============

In extent to the builtin rst directives ( https://docutils.sourceforge.io/docs/ref/rst/directives.html ), we provides
additional directives, or edit the existing ones.

Here is a quick directive's glossary as reminder:

.. code-block:: rst

    .. directivename:: argument1 argument2
        :option1:
        :option2:

        content


code, code-block
________________

You can embed code snippets with the ``code`` and ``code-block`` directives. They use `pygments <https://pygments.org/>`_
to provide syntax highlighting.

- The list of supported languages: https://pygments.org/languages/
- The list of supported options: https://pygments.org/docs/formatters/#HtmlFormatter

Example:

.. code:: rst

    .. code:: languageName
        :option1: optionValue

        your code
        in multiple lines


admonitions
___________

Admonitions are builtin to rst and there is no changes to them.

    | admonition, attention, caution, danger, error, hint, important, note, tip, warning
    | -- https://docutils.sourceforge.io/docs/ref/rst/directives.html#admonitions

If you want to render a specific admonition type with a custom title you can use the generic ``.. admonition::`` and
add the class option with the type. Example:

.. code-block:: rst

    .. admonition:: 🍕 About pizza
        :class: warning

        Pineapple do belongs on them.

Will render:

.. admonition:: 🍕 About pizza
    :class: warning

    Pineapple do belongs on them.

highlight
+++++++++

It is however possible to have an admonition without a title using the custom directive ``.. highlight::``:

.. code-block:: rst

    .. highlight::
        :class: tip

        Look ma', no hands !

Will render:

.. highlight::
    :class: tip

    Look ma', no hands !


url-preview
___________

This is a customd directive which allow you to share links as "static embeds", meaning they have the box with rich
content that is prettier than just a link, but you actually have to write all the rich content yourself instead of
having fetch using javascript.

It required one mandatory argument which is the url to "prettify".

The directive have 4 options:

- ``title``: title to use for the preview
- ``image``: url to an image file (relative or absolute).
- ``svg``: relative url to a local svg file (relative to the page directory).
- ``color``: the css color of the svg.
- ``svg-size``: 1 or 2 number indicating the size of the svg. ex: '64' will set the svg to 64x64 px

The content of the directive will be used as description.

Example:

.. code-block:: rst

    .. url-preview:: https://mrlixm.github.io/
        :title: Website - Liam Collod
        :image: ../.static/images/cover-social.jpg

        Check my website & blog. VFX, imaging and software development.

.. url-preview:: https://mrlixm.github.io/
    :title: Website - Liam Collod
    :image: ../.static/images/cover-social.jpg

    Check my website & blog. VFX, imaging and software development.


image-grid
__________

When needing to display a lot of image in a non-sequential layout (so as a grid), you
can use the ``.. image-grid::`` directive.

It accept no argument, neither options and all works based on its content.

Each line of the content is treated as an image. You group images into one row
by separating them by a blank line. The line must start by the image uri, relative
to the page its in and is optionally followed by the image caption.

.. warning::

    The image path cannot contains whitespaces

It is possible the image caption span multiple line; in that case the following lines
must start with a 2+ spaced indent.

Example:

.. code-block:: rst

    .. image-grid::

        path/to/image1.jpg
        path/to/image2.jpg

        path/to/image3.jpg some caption that will be displayed under
        path/to/image4.jpg the caption can span
            multiple lines if it's too long.
        path/to/image5.jpg


image-gallery
_____________


The ``.. image-gallery::`` is a more advanced directive to showcase images,
their metdata and their caption.

It's build upon a 2-column layout in which you choose to add images or their caption
independently.

The directive have no arguments and expect 4 mandatory options:

- ``:left:`` comma separated list of items id to add to the left column (in order).
- ``:right:`` comma separated list of items id to add to the right column (in order).
- ``:left-width:`` a single float, the width in percent of the left column
- ``:right-width:`` a single float, the width in percent of the right column

The content will allow to specify which image to display and configure their caption
and metadata. This is achieved by using another directive ``.. image-frame::``.

You add as much ``image-frame`` directive as there is image to showcase.

image-frame
+++++++++++

This other directive expects 3 mandatory arguments and 1 optional option.

The 3 arguments are in order: "image id", "label id", "image uri"

The 1 options is ``:metadata:`` which expect to define a mapping of "metadata name": "value",
formalized as a list of line where each line is a pair.

.. tip::

    Each pair will correspond to a list item that will receive the metadata name as
    css-class which allow indifidual styling based on the metadata.


Example:

.. code-block:: rst

    .. image-gallery::
        :left: image1
        :right: label1, image2, label2
        :left-width: 35
        :right-width: 65

        .. image-frame:: image1 label1 photo1.jpg
            :metadata:
                date: 2024-11 early morning
                location: France - Lyon - Parc de la Tete d’Or
                film: 35mm Kodak Gold 200
                lens: Minolta MD 35mm

            some of the text descrption of the image
            that can span multiple lines

        .. image-frame:: image2 label2 photo2.jpg
            :metadata:
                date: 2024-11 early morning
                location: France - Lyon - Parc de la Tete d’Or
                film: 35mm Kodak Gold 200
                lens: Minolta MD 35mm

           some of the text descrption of the image
           that can span multiple lines


.meta.json files
----------------

We see previously that each rst page can define some metadata at its top. However
specifying everytime some of those fields is a repetitive task. To adress this issue
you can use meta files.

Meta files are json files whose content specify default metadata value to use for all
files that are next or children in the hierarchy of the meta file. The meta file hierachy
is recursively merged so the meta file "closest" to your page will get priority.

Example:

.. code:: text

    .meta.json
    index.rst
    blog/
        .meta.json
        index.rst
        post1.rst
        post2.rst

..

    In the above example ``.meta.json`` at root will affect ``index.rst`` but also all
    files in the ``blog/`` directory. However the content of ``blog/.meta.json`` will take
    priority over the root one.

Meta file use standard JSON syntax, where a non-nested dict is expected. Each root key
defines the name of the metadata to set, which is the same as you would use in the rst
page. The value can either be a string or list of string.

List of strings are handled differently but allow merging, this mean that the child
meta file will ``extend()`` the parent meta file list if it exists. When resolved
in the rst file, lists are converted back to string by joining its items with a ``,``.

It's also totally possibel that for the same metadata key, switch between a list type
or a str type. A str type will override any list value defined before, and a list value
when the previous value was a string, will cast the previous value to a list automatically.

*The code logic can be found in* ``lmxsite._browse``.

Writing page html templates
---------------------------

All html templates are processed with `Jinja <https://jinja.palletsprojects.com/en/stable/>`_.

.. highlight::
    :class: warning

    TBD

cross-referrencing
==================

How to link to other html pages or static content ?

First, reminder that all relative urls are relative to the page they are on.
This mean that if you want to link to a resources based on its site root location,
like ``.static/icon/icon.svg`` you will need to make it relative to the page
instead. This is easily done using the custom jinja filter ``mkpagerel``.

Example:

.. code:: html+jinja

   <img src="{{ ".static/icons/icon.svg"|mkpagerel }}">

If you need the opposite you can also use ``mksiterel`` to make an page-relative
url; relative to the site root instead.

And if you ever need an absolute url you can use ``mksiteabs`` that will prepend
the site url but only on publish.

Then when linking pages or content, you must link a file, never a directory.
While once published ``work/myproject/`` might resolve fine by the server,
locally it will not and you will need to link ``work/myproject/index.html``
instead. However just because this make links uglier you can use ``prettylink``
that will shorten the links on publish; best of both worlds !