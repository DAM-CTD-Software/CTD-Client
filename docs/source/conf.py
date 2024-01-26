import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    '..', '..', 'src')))

project = 'mig'
copyright = '2024, Emil Michels'
author = 'Emil Michels'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    "sphinx_autodoc_typehints",
    'sphinx.ext.todo',
]

autodoc_member_order = 'bysource'
templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
