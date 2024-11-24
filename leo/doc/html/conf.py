# flake8: noqa
#@+leo-ver=5-thin
#@+node:ekr.20090428133936.2: * @file html/conf.py
#@@first

"""
leo/doc/html/conf.py

This file must be in the source directory.
"""

# https://www.sphinx-doc.org/en/master/usage/configuration.html
# http://docs.readthedocs.io/en/latest/getting_started.html#in-markdown
# https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes

project = 'Leo'
copyright = '1997-2024, Edward K. Ream'
version = '6.8.2'
release = '6.8.2'

html_theme = 'classic'
pygments_style = 'sphinx'
source_suffix = '.html.txt'

html_last_updated_fmt = '%B %d, %Y'
html_logo = '_static/LeoLogo.svg'
html_use_index = True
html_use_smartypants = True
master_doc = 'leo_toc'  # The master toctree document, without suffix.

# These folders are copied to the documentation's HTML output.
html_static_path = ['_static']  # 'screen-shots' aren't going to change.
html_css_files = ['custom.css',]  # Relative to html_static_paths.

# Options...
html_sidebars = {
   '**': [
        'relations.html',  # Enable links to the previous and next documents.
        'searchbox.html',  # Enable “quick search” box.
        # localtoc.html:        # Use a fine-grained table of contents.
        # globaltoc.html:       # Use a coarse-grained table of contents.
        # sourcelink.html:      # Add links to the source of the current document.
    ]
}

# extensions = []
# templates_path = []
# exclude_trees = []              # Don't search these for source files.
# html_split_index = False        # True: one page per letter.
# html_use_modindex = False
# html_use_opensearch = ''
#

#@@nobeautify
#@@language python
#@-leo
