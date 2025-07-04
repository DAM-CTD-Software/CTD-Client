import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "..", "src")))

project = "ctdclient"
copyright = "2024-2025, Emil Michels"
author = "Emil Michels"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx.ext.todo",
    "sphinx.ext.linkcode",
    "myst_parser",
]


def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    return (
        "https://git.io-warnemuende.de/CTD-Software/CTD-Client/src/branch/main/src/%s.py"
        % filename
    )


html_logo = "../../icon/BrnBld_CtdRosette_256.svg"
html_favicon = "../../icon/BrnBld_CtdRosette_256.svg"

autodoc_member_order = "bysource"
templates_path = ["_templates"]
exclude_patterns = []

html_theme = "furo"
html_static_path = ["_static"]
