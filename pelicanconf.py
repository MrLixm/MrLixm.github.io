#!/usr/bin/env python
# -*- coding: utf-8 -*- #
"""
pelican configuration file
"""

"""___________________________________________________________________________

 Basic config

"""
AUTHOR = 'Liam Collod'
SITENAME = "Liam Collod's Blog"
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

PLUGIN_PATHS = []
PLUGINS = []

"""___________________________________________________________________________

 THEME

"""
# # m.css config
THEME = 'submodule/m.css/pelican-theme'
THEME_STATIC_DIR = 'static'
DIRECT_TEMPLATES = ['index']

M_CSS_FILES = [
    'https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,400i,600,600i%7CSource+Code+Pro:400,400i,600',
    '/static/m-dark.css'
]
M_THEME_COLOR = '#22272e'

PLUGIN_PATHS.append('submodule/m.css/plugins')
PLUGINS.append('m.htmlsanity')

M_FAVICON = ("images/global/logo.mrlixm.png", 'image/x-ico')
M_SITE_LOGO = "images/global/logo.mrlixm.png"
M_SITE_LOGO_TEXT = "Liam Collod's Blog"
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

"""___________________________________________________________________________

 MISC

"""

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = False
