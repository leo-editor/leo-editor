# flake8: noqa
"""leo/doc/html/conf.py"""
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes

project = 'Leo'
copyright = '1997-2025, Edward K. Ream'
version = '6.8.6'
release = '6.8.6'

html_theme = 'classic'
pygments_style = 'sphinx'
source_suffix = '.html.txt'

html_last_updated_fmt = '%B %d, %Y'
html_logo = '../_static/LeoLogo.svg'
html_use_index = False  # Not necessary for glossary.
html_use_smartypants = False
master_doc = 'leo_toc'

# These folders are copied to the documentation's HTML output.
html_static_path = ['../_static']  # 'screen-shots' aren't going to change.
html_css_files = ['custom.css']  # Relative to html_static_paths.

# Options...
html_sidebars = {
   '**': [
        'relations.html',  # Enable links to the previous and next documents.
        'searchbox.html',  # Enable “quick search” box.
        # 'localtoc.html',  # Use a fine-grained table of contents.
        # 'globaltoc.html,  # Use a coarse-grained table of contents.
    ]
}

# extensions = []
# templates_path = []
# exclude_trees = []              # Don't search these for source files.
