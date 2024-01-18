# flake8: noqa
#@+leo-ver=5-thin
#@+node:ekr.20090428133936.2: * @file html/conf.py
#@@first
#@@language python

# leo/doc/html/conf.py

# This file must be in the source directory.

# https://www.sphinx-doc.org/en/master/usage/configuration.html
# http://docs.readthedocs.io/en/latest/getting_started.html#in-markdown

source_suffix = '.html.txt'

#@+<< general settings >>
#@+node:ekr.20230121091126.1: ** << general settings >>
project = 'Leo'
copyright = '1997-2024, Edward K. Ream'
version = '6.7.7'
release = '6.7.7'

# The master toctree document, without suffix.
master_doc = 'leo_toc'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Paths.  All relative to this directory.
extensions = []  # Sphinx extension modules.
templates_path = ['_templates']
exclude_trees = ['_build']  # Don't search for source files.
#@-<< general settings >>
#@+<< html options >>
#@+node:ekr.20230121091709.1: ** << html options >>
# https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes

# Paths containing custom static files (such as style sheets),
# relative to this directory.
# They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', 'screen-shots']  # leo/docs/static

# The theme to use for HTML and HTML Help pages.
html_theme = 'classic'  # 'default', 'sphinxdoc'.

# These paths are either relative to html_static_path or fully qualified paths.
html_css_files = [
    'custom.css',
]

# Theme options. All colors are CSS colors.
html_theme_options = {
    'collapsiblesidebar': True,
    'sidebarbgcolor': "#fffdbc", # Leo yellow.
    'sidebartextcolor': 'black',  # Text color for the sidebar.
    'sidebarlinkcolor': 'black',
    'bgcolor': "#fffbdc", # Body background color.
}

# The name of an image file (relative to this directory) at the top of the sidebar.
html_logo = '_static/LeoLogo.svg'

# If not '', insert 'Last updated on:' at the bottom of every pages.
# using the given strftime format.
html_last_updated_fmt = '%B %d, %Y'

# If true, use SmartyPants to convert quotes and dashes.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.

# localtoc.html:    a fine-grained table of contents.
# globaltoc.html:   a coarse-grained table of contents
#                   for the whole documentation set, collapsed.
# relations.html:   links to the previous and next documents.
# sourcelink.html:  a link to the source of the current document,
#                   if enabled in html_show_sourcelink.
# * searchbox.html: Add the “quick search” box.

html_sidebars = {
   '**': ['relations.html', 'searchbox.html',]
}

# True: generate module index.
html_use_modindex = False

# True: generate index.
html_use_index = True

# True: split the index--one page per letter.
html_split_index = False

# True: Add links to the reST sources.
html_show_sourcelink = False

# If true, output an OpenSearch description file.
# All pages will contain a <link> tag referring to it.
# The value of this option must be the base URL from which the finished HTML is served.
html_use_opensearch = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'Leodoc'
#@-<< html options >>
#@-leo
