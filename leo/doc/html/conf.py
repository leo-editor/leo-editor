# flake8: noqa
#@+leo-ver=5-thin
#@+node:ekr.20090428133936.2: * @file html/conf.py
#@@first
#@@language python
# leo/doc/html/conf.py

# https://www.sphinx-doc.org/en/master/usage/configuration.html
# http://docs.readthedocs.io/en/latest/getting_started.html#in-markdown

# leo/doc/html is the current directory.
# This file is execfile()d with the current directory set to its containing dir.

# import os
# tag = 'leo/doc/html/conf.py'
# print(f"\n{tag} cwd: {os.getcwd()}")

#@+<< general settings >>
#@+node:ekr.20230121091126.1: ** << general settings >>
# General settings...

# The suffix of source filenames.
try:
    from recommonmark.parser import CommonMarkParser

    source_parsers = {
        '.md': CommonMarkParser,
    }
    source_suffix = ['.html.txt', '.md'] # possible: '.rst',
    print(".md files enabled")
except ImportError:
    source_suffix = '.html.txt'
    print(".md files NOT enabled")
print('')

# Sphinx extension module names, as strings.
# They can be Sphinx extensions (named 'sphinx.ext.*') or your custom ones.
extensions = []

# Add any paths that contain templates here, relative to this directory.

templates_path = ['_templates']  # leo/doc/html/_templates

# The master toctree document.
master_doc = 'leo_toc'  # don't use any suffix.

# General information about the project.
project = 'Leo'
copyright = '1997-2023, Edward K. Ream'

# The version info for this project.
version = '6.7.3'
release = '6.7.3'

# List of directories, relative to source directory,
# that shouldn't be searched for source files.
exclude_trees = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'
#@-<< general settings >>
#@+<< html options >>
#@+node:ekr.20230121091709.1: ** << html options >>
# -- Options for HTML output...

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
#@+<< LaTex options >>
#@+node:ekr.20230121092413.1: ** << LaTex options >>
# -- Options for LaTeX output...

# The paper size ('letter' or 'a4').
latex_paper_size = 'a4'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# tex_documents(source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('leo_toc', 'Leodocumentation.tex', 'Leo', 'Edward K. Ream', 'manual'),
]

# True: generate module index.
latex_use_modindex = False
#@-<< LaTex options >>
#@-leo
