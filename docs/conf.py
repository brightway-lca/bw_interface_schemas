# conf.py
# Sphinx configuration file
# https://www.sphinx-doc.org/en/master/usage/configuration.html

### import setup ##################################################################################

import datetime

### project information ###########################################################################

project = "bw_interface_schemas"
author = "Brightway Developers"
copyright = datetime.date.today().strftime("%Y") + " Brightway Developers"

### project configuration #########################################################################

extensions = [
    # native extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    # theme
    "sphinx_rtd_theme",
    # Markdown support
    "myst_parser",
    # responsive web component support
    "sphinx_design",
    # copy button on code blocks
    "sphinx_copybutton",
    # support for pydantic models
    "sphinxcontrib.autodoc_pydantic",
]

exclude_patterns = ["_build"]

# The master toctree document.
master_doc = "index"

### intersphinx configuration ######################################################################

intersphinx_mapping = {
    "bw": ("https://docs.brightway.dev/en/latest/", None),
}

### theme configuration ############################################################################

html_theme = "sphinx_rtd_theme"
html_title = "bw_interface_schemas"
html_show_sphinx = False

html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_logo = "https://raw.githubusercontent.com/brightway-lca/brightway-documentation/main/source/_static/logo/BW_all_white_transparent_landscape_wide.svg"
html_favicon = "https://github.com/brightway-lca/brightway-documentation/blob/main/source/_static/logo/BW_favicon_500x500.png"

### extension configuration ########################################################################

## myst_parser configuration ############################################
## https://myst-parser.readthedocs.io/en/latest/configuration.html

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]
