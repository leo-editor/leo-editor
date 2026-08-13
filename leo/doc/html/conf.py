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
    # Everything in the navbar is already available in the primary sidebar.
    # Leaving all slots empty also lets the theme bind the visible sidebar toggle.
    'navbar_start': [],
    'navbar_center': [],
    'navbar_end': [],
    'navbar_persistent': [],
    'logo': {
        'image_light': '../_static/LeoLogo.svg',
        'image_dark': '../_static/LeoLogo-dark.svg',
    },
}
pygments_style = 'sphinx'
source_suffix = '.html.txt'

html_last_updated_fmt = '%B %d, %Y'
html_title = 'Leo'
html_use_index = False  # Not necessary for glossary.
html_use_smartypants = False
master_doc = 'index'

# These folders are copied to the documentation's HTML output.
html_static_path = ['../_static']  # 'screen-shots' aren't going to change.
html_css_files = ['custom.css']  # Relative to html_static_paths.
