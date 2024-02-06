#@+leo-ver=5-thin
#@+node:maphew.20180224170853.1: * @file ../../setup.py
"""
setup.py for a dummy distribution at PyPi.

Run with `python -m build` from the leo-editor directory.
"""
import setuptools
#@+<< define classifiers >>
#@+node:maphew.20141126230535.4: ** << define classifiers >>
classifiers = [
    'Development Status :: 6 - Mature',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Software Development',
    'Topic :: Text Editors',
    'Topic :: Text Processing',
]
#@-<< define classifiers >>
version = '6.7.7.1'  # Dashes are not allowed.
description = (
    'An IDE, PIM and Outliner\n'
    'Distributed only at GitHub: https://github.com/leo-editor/leo-editor/releases'
)
setuptools.setup(
    name='leo',
    version=version,
    author='Edward K. Ream',
    author_email='edreamleo@gmail.com',
    url='https://leo-editor.github.io/leo-editor',
    license='MIT License',
    project_url='https://leo-editor.github.io/leo-editor/',
    description=description,  # becomes 'Summary' in pkg-info
    long_description=description,
    long_description_content_type="text/plain",
    platforms=['Linux', 'Windows', 'MacOS'],
    download_url='https://github.com/leo-editor/leo-editor/releases',
    classifiers=classifiers,
    packages=[],
    include_package_data=False,
    setup_requires=[],
    install_requires=[],
    entry_points = {},
    python_requires='>=3.9',
)
print('setup.py: done')
#@@language python
#@@tabwidth -4
#@-leo
