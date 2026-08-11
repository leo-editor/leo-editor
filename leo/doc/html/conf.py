# flake8: noqa
"""leo/doc/html/conf.py"""
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes

project = 'Leo'
author = 'Edward K. Ream and contributors'
copyright = '1997-2026, Edward K. Ream'
version = '6.8.9'
release = '6.8.9'

html_theme = 'sphinx_book_theme'
html_theme_options = {
    'repository_url': 'https://github.com/leo-editor/leo-editor',
    'use_issues_button': True,
    'use_repository_button': True,
    'home_page_in_toc': True,
    'show_navbar_depth': 2,
}
pygments_style = 'sphinx'
source_suffix = '.html.txt'

html_last_updated_fmt = '%B %d, %Y'
html_logo = '../_static/LeoLogo.svg'
html_title = 'Leo'
html_use_index = False  # Not necessary for glossary.
html_use_smartypants = False
master_doc = 'index'

# These folders are copied to the documentation's HTML output.
html_static_path = ['../_static']  # 'screen-shots' aren't going to change.
html_css_files = ['custom.css']  # Relative to html_static_paths.

# Options...
# extensions = []
# templates_path = []
# exclude_trees = []              # Don't search these for source files.
