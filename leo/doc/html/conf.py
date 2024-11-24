# flake8: noqa
#@+leo-ver=5-thin
#@+node:ekr.20090428133936.2: * @file html/conf.py
#@@first
#@@language python

# This file must be in the source directory.
# leo/doc/html/conf.py

# https://www.sphinx-doc.org/en/master/usage/configuration.html
# http://docs.readthedocs.io/en/latest/getting_started.html#in-markdown
# https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes

project = 'Leo'
copyright = '1997-2024, Edward K. Ream'
version = '6.8.2'
release = '6.8.2'

use_dark = True
html_theme = 'classic'
pygments_style = 'sphinx'
source_suffix = '.html.txt'
master_doc = 'leo_toc'  # The master toctree document, without suffix.
html_last_updated_fmt = '%B %d, %Y'

# Paths.  All relative to this directory.
extensions = []  # Sphinx extension modules.
templates_path = ['_templates']
exclude_trees = ['_build']  # Don't search for source files.
html_logo = '_static/LeoLogo.svg'
html_static_path = ['_static', 'screen-shots']  # leo/docs/static
html_css_files = ['custom.css',]  # Relative to html_static_path.

# All colors are CSS colors.
if use_dark:
    html_theme_options = {
        'collapsiblesidebar': True,
        'sidebarbgcolor': "black",
        'sidebartextcolor': 'white',
        'sidebarlinkcolor': 'white',
        'bgcolor': "black",
    }
else:
    html_theme_options = {
        'collapsiblesidebar': True,
        'sidebarbgcolor': "#fffdbc",  # Leo yellow.
        'sidebartextcolor': 'black',
        'sidebarlinkcolor': 'black',
        'bgcolor': "#fffbdc",  # Leo yellow.
    }

html_sidebars = {
   '**': [
        'relations.html',  # links to the previous and next documents.
        'searchbox.html',  # “quick search” box.
        # localtoc.html:    # a fine-grained table of contents.
        # globaltoc.html:   # a coarse-grained table of contents.
        # sourcelink.html:  a link to the source of the current document.
    ]
}

html_show_sourcelink = False
html_split_index = False  # True: one page per letter.
html_use_index = True
html_use_modindex = False
html_use_opensearch = ''
html_use_smartypants = True
# htmlhelp_basename = 'Leodoc'    # Output file base name for HTML help builder.
#@-leo
