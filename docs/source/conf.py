import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "..", "src")))

autodoc_mock_imports = [
    "tkinter",
    "customtkinter",
    "CTkMessagebox",
]

project = "ctdclient"
copyright = "2024-2026, Emil Michels"
author = "Emil Michels"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx.ext.todo",
    "sphinx.ext.linkcode",
    "myst_parser",
    "click_extra.sphinx",
]

myst_enable_extensions = ["colon_fence"]


def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    return (
        "https://github.com/DAM-CTD-Software/ctd-client/src/branch/main/src/%s.py"
        % filename
    )


html_logo = html_favicon = "../images/ctd_rosette.svg"

autodoc_member_order = "bysource"
templates_path = ["_templates"]
exclude_patterns = []

html_theme = "furo"
html_static_path = ["_static"]
