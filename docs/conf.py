import pkg_resources
import sphinx_rtd_theme


project = 'Spaceland'
copyright = '2017 Já hf'
version = release = pkg_resources.require('spaceland')[0].version

master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
default_role = 'py:obj'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]
intersphinx_mapping = {'https://docs.python.org/3': None}

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'navigation_depth': 4,
}
html_last_updated_fmt = '%d %B %Y'
html_use_index = False
html_domain_indices = False
html_copy_source = False
html_show_sphinx = False
