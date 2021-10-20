#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
from pelicanconf import *

sys.path.append(os.curdir)

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = ''
RELATIVE_URLS = True

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

DELETE_OUTPUT_DIRECTORY = True

# THEME

_THEME_CSS = '/static/m-dark.css'

# as recommended in the doc we use the compiled version
M_CSS_FILES = [
    'https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,400i,600,600i%7CSource+Code+Pro:400,400i,600',
    _THEME_CSS
]
THEME_STATIC_PATHS = [_THEME_CSS]

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""
