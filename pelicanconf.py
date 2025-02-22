#!/usr/bin/env python
# -*- coding: utf-8 -*- #
"""
pelican configuration file

# Conventions

## Prefixes

none: no prefix means pelican native content
_ : only used to build another object, not directly
M_ : m.css content
L_ : liam customized content, added myself to extend m.css

"""

CACHE_CONTENT = False
LOAD_CONTENT_CACHE = False

"""___________________________________________________________________________

 Basic config

"""
AUTHOR = "Liam Collod"
SITENAME = "Liam Collod Website"
SITEURL = ""

TIMEZONE = "Europe/Paris"
DEFAULT_DATE_FORMAT = "%d %B %Y"
DEFAULT_LANG = "en"

PATH = "content"
PLUGIN_PATHS = []  # empty for init
PLUGINS = []  # empty for init

READERS = {"html": None}  # avoid processing .html files

L_PROJECTS_PATH = "pages/work/projects"

IGNORE_FILES = [
    ".#*",  # ignore emack lock files (default)
    "__*",  # ignore dir/files starting with __
]

# -- PAGE (relative to PATH)
PAGE_PATHS = ["pages"]
PAGE_URL = "{proot}/{slug}"  # proot is only defined in EXTRA_PATH_METADATA
PAGE_SAVE_AS = "{proot}/{slug}/index.html"
# this fucker doesn't work ???, instead I'm using IGNORE_FILES
PAGE_EXCLUDES = ["pages/work/projects/_template"]

# -- Archives (blog post listing)(relative to PATH)
ARCHIVES_URL = "blog/"
ARCHIVES_SAVE_AS = "blog/index.html"

# -- ARTICLE (relative to PATH)
ARTICLE_PATHS = ["blog"]
ARTICLE_URL = "blog/{slug}/"  # category/ is part of the slug
ARTICLE_SAVE_AS = "blog/{slug}/index.html"
# this fucker doesn't work ???, instead I'm using IGNORE_FILES
ARTICLE_EXCLUDES = ["blog/_template"]

# -- STATIC (relative to PATH)
STATIC_PATHS = ["images", "styles"]
STATIC_URL = "static/{path}"
STATIC_SAVE_AS = "static/{path}"

# # regular expression that only get the parent dir path
# PATH_METADATA = r'(?P<proot>.*)/(\w|-)+\..+$'

# we repath the work related pages
EXTRA_PATH_METADATA = {
    r"pages/work.rst": {"proot": "work", "slug": ""},
    r"pages": {"proot": "pages"},
    r"pages/work": {"proot": "work"},
    f"{L_PROJECTS_PATH}": {"proot": "work/projects"},
    r"pages/assets": {"proot": "assets"},
}

TEMPLATE_PAGES = None
TEMPLATE_EXTENSIONS = [".html"]
DIRECT_TEMPLATES = [
    "archives",
]

DEFAULT_PAGINATION = 10
# if value set to None, use the above
PAGINATED_TEMPLATES = {
    "archives": None,
    "tag": None,
    "category": None,
    "author": None,
}


# PATH_METADATA = '(blog/)?(?P<slug>.+).rst'
SLUGIFY_SOURCE = "basename"  # the {slug} is generated from the file name instead of the file title tag
# SLUG_REGEX_SUBSTITUTIONS = [
#         (r'[^\w\s-]', ''),  # remove non-alphabetical/whitespace/'-' chars
#         (r'(?u)\A\s*', ''),  # strip leading whitespace
#         (r'(?u)\s*\Z', ''),  # strip trailing whitespace
#         (r'[-\s]+', '-'),  # reduce multiple whitespace or '-' to single '-'
#         (r'C\+\+', 'cpp'),
# ]

"""___________________________________________________________________________

 THEME

"""

THEME = "theme"
THEME_STATIC_DIR = "static"
THEME_TEMPLATES_OVERRIDES = []

_EXTENSIONS = "extensions"
_EXTENSION_MCSS = f"{_EXTENSIONS}/m.css"

PLUGIN_PATHS.append(f"{_EXTENSION_MCSS}/plugins")
PLUGINS.extend(
    [
        "m.abbr",
        "m.code",
        "m.alias",
        "m.components",
        "m.dox",
        "m.filesize",
        "m.gh",
        "m.gl",
        "m.htmlsanity",
        "m.images",
        "m.link",
        "m.metadata",
        "m.sphinx",
        "m.vk",
        "lxm.rst_content",
    ]
)

# PLUGIN_PATHS.append("extensions/plugins")
# PLUGINS.append("jinja2content")

FORMATTED_FIELDS = [
    "summary",
    "description",
    "landing",
    "badge",
    "header",
    "size",
    "footer",
    "thumbnail",
    "cover_size",
    "title_disable",
]

# theme related configuration
M_CSS_FILES = [
    "https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,400i,600,600i,700%7CSource+Code+Pro:400,400i,600",
    "https://fonts.googleapis.com/css2?family=Georama:wght@400;500;600;700",
    "https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;700;900",
    "/static/m-dark.css",
]
CSS_FILE = "/static/m-dark.css"

M_BLOG_NAME = "Liam Collod's Blog"
M_BLOG_URL = "/blog"

M_THEME_COLOR = "#20FC8F"
M_FAVICON = ("static/images/global/icons/lixm.svg", "image/x-ico")
# M_BLOG_FAVICON = ('favicon-blog.png', 'image/png')
M_SITE_LOGO = "static/images/global/icons/lixm-outline.svg"
M_SITE_LOGO_TEXT = "Liam Collod"

# SOCIAL
M_SOCIAL_TWITTER_SITE = "@MrLixm"
M_SOCIAL_TWITTER_SITE_ID = 713068621203914752
M_SOCIAL_BLOG_SUMMARY = "Personal website & blog for Liam Collod (MrLixm)"
M_SOCIAL_IMAGE = "/static/images/global/cover_social.jpg"

# Index page
M_NEWS_ON_INDEX = ("Latest posts", 5)
M_COLLAPSE_FIRST_ARTICLE = True
M_HTMLSANITY_HYPHENATION = True
M_HTMLSANITY_SMART_QUOTES = True
M_HTMLSANITY_FORMATTED_FIELDS = ["thumbnail"]

# M_HTML_HEADER = ""
M_LINKS_NAVBAR1 = [
    ("Work", "work", "work", []),
    ("Blog", "blog", "[blog]", []),
    ("Contact", "pages/contact", "contact", []),
]

# M_LINKS_FOOTER1 = [
#     ('Contact', ''),
#     ('e-mail', 'mailto:lcollod@gmail.com'),
#     ('twitter', 'https://twitter.com/MrLixm')
# ]

M_FINE_PRINT = """
Copyright © `Liam Collod <mailto:lcollod@gmail.com>`_ 2021 - 2025. All rights
reserved. Made with `Pelican <https://blog.getpelican.com/>`_ and
`m.css <https://mcss.mosra.cz/>`_ .
"""

# DATA ORGANISATION
M_METADATA_AUTHOR_PATH = "metadata/authors"
M_METADATA_CATEGORY_PATH = "metadata/categories"
M_METADATA_TAG_PATH = "metadata/tags"

"""___________________________________________________________________________

 MISC

"""

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
