#!/usr/bin/env python
# -*- coding: utf-8 -*- #
"""
pelican configuration file
"""

CACHE_CONTENT = True
LOAD_CONTENT_CACHE = True

"""___________________________________________________________________________

 Basic config

"""
AUTHOR = 'Liam Collod'
SITENAME = "Liam Collod Website"
SITEURL = ''

TIMEZONE = 'Europe/Paris'
DEFAULT_DATE_FORMAT = "%d %B %Y"
DEFAULT_LANG = 'en'

PATH = 'content'
PLUGIN_PATHS = []  # empty for init
PLUGINS = []  # empty for init

READERS = {'html': None}  # avoid processing .html files

# -- PAGE
PAGE_PATHS = ['pages']
# PAGE_EXCLUDES = []
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'
# -- Archives (blog postr listing)
ARCHIVES_URL = 'blog/'
ARCHIVES_SAVE_AS = 'blog/index.html'
# -- ARTICLE
ARTICLE_PATHS = ['blog']
ARTICLE_URL = 'blog/{slug}/'  # category/ is part of the slug
ARTICLE_SAVE_AS = 'blog/{slug}/index.html'
ARTICLE_EXCLUDES = ["blog/_template"]
# -- STATIC
STATIC_PATHS = ['images']
STATIC_URL = 'static/{path}'
STATIC_SAVE_AS = 'static/{path}'
# EXTRA_PATH_METADATA = {}

DIRECT_TEMPLATES = ['archives']
PAGINATED_TEMPLATES = {
    'archives': None,
    'tag': None,
    'category': None,
    'author': None
}

DEFAULT_PAGINATION = 10

# PATH_METADATA = '(blog/)?(?P<slug>.+).rst'
SLUGIFY_SOURCE = 'basename'  # the {slug} is generated from the file name instead of the file title tag
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

_THEME_ROOT = "extensions/m.css"

# m.css config
THEME = f'{_THEME_ROOT}/pelican-theme'
THEME_STATIC_DIR = 'static'

# M_HTML_HEADER = ""
M_LINKS_NAVBAR1 = [
    ('Work', "pages/work", "work", []),
    ('Blog', "/blog/", '[blog]', []),
    ('Contact', 'pages/contact', 'contact', []),
]


PLUGIN_PATHS.append(f'{_THEME_ROOT}/plugins')
PLUGINS.extend(
    [
        'm.abbr',
        'm.code',
        'm.alias',
        'm.components',
        'm.dox',
        'm.filesize',
        'm.gh',
        'm.gl',
        'm.htmlsanity',
        'm.images',
        'm.link',
        'm.metadata',
        'm.sphinx',
        'm.vk'
    ]
)

# PLUGIN_PATHS.append("extensions/plugins")
# PLUGINS.append("jinja2content")

FORMATTED_FIELDS = [
    'summary',
    'description',
    'landing',
    'badge',
    'header',
    'size',
    'footer',
    'thumbnail',
    'cover_size',
    'title_disable'
]

# theme related configuration
M_CSS_FILES = [
    'https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,400i,600,600i,700%7CSource+Code+Pro:400,400i,600',
    "https://fonts.googleapis.com/css2?family=Georama:wght@400;600;700",
    "https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;700;900",
    '/static/m-dark.css'
]
CSS_FILE = "/static/m-dark.css"

M_BLOG_NAME = "Liam Collod's Blog"
M_BLOG_URL = '/blog'

M_THEME_COLOR = '#20FC8F'
M_FAVICON = ("static/images/global/icons/lixm.svg", 'image/x-ico')
# M_BLOG_FAVICON = ('favicon-blog.png', 'image/png')
M_SITE_LOGO = "static/images/global/icons/lixm.svg"
M_SITE_LOGO_TEXT = "Liam Collod"

# SOCIAL
M_SOCIAL_TWITTER_SITE = '@MrLixm'
M_SOCIAL_TWITTER_SITE_ID = 713068621203914752
M_SOCIAL_BLOG_SUMMARY = "Personal website & blog for Liam Collod (MrLixm)"
M_SOCIAL_IMAGE = "/static/images/global/cover_social.jpg"

# Index page
M_NEWS_ON_INDEX = ("Latest posts", 5)
M_COLLAPSE_FIRST_ARTICLE = True
M_HTMLSANITY_HYPHENATION = True
M_HTMLSANITY_SMART_QUOTES = True
M_HTMLSANITY_FORMATTED_FIELDS = ["thumbnail"]

# M_LINKS_FOOTER1 = [
#     ('Contact', ''),
#     ('e-mail', 'mailto:lcollod@gmail.com'),
#     ('twitter', 'https://twitter.com/MrLixm')
# ]

M_FINE_PRINT = """
Copyright © `Liam Collod <mailto:lcollod@gmail.com>`_ - 2021. All rights
reserved. Made with `Pelican <https://blog.getpelican.com/>`_ and
`m.css <https://mcss.mosra.cz/>`_ .
"""

# DATA ORGANISATION
M_METADATA_AUTHOR_PATH = 'metadata/authors'
M_METADATA_CATEGORY_PATH = 'metadata/categories'
M_METADATA_TAG_PATH = 'metadata/tags'

"""___________________________________________________________________________

 MISC

"""

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
