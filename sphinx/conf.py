# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, os
sys.path.insert(0,os.path.abspath(os.path.pardir))

# sphinx extension module globs
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    ]
autodoc_member_order = 'bysource'

source_suffix = ['.rst',]
master_doc = 'index'
project = 'flaskies'
copyright = '2017, Victor Hui'
author = 'Victor Hui'
version = '?'
release = '?'
add_module_names = False
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
html_theme = 'alabaster'
html_static_path = ['_static']
html_sidebars = {'**':[
    'about.html',
    'searchbox.html',
    'globaltoc.html',
]}
