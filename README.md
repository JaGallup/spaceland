The `spaceland` library is a modern Python library for fast, Pythonic access to [ESRI shapefiles][shp]. It's currently in its early stages and under active development.

[![Build status][tci]][tcl]
[![Code coverage report][cci]][ccl]

The package supports Python 3.3+ and will run quite happily under PyPy3. While it's not yet on PyPI you can install it directly from GitHub:

    pip install -e git+https://github.com/JaGallup/spaceland.git#egg=spaceland

 On Python 3.5+ it has no dependencies; on Python 3.3 and 3.4 it will install the [backport of the standard library's `typing` module][tbp], and on Python 3.3 it will install the [backport of the standard library's `pathlib` module][pbp].


[tci]: https://travis-ci.org/JaGallup/spaceland.svg?branch=master
[tcl]: https://travis-ci.org/JaGallup/spaceland
[cci]: https://codecov.io/gh/JaGallup/spaceland/branch/master/graph/badge.svg
[ccl]: https://codecov.io/gh/JaGallup/spaceland
[shp]: http://www.esri.com/library/whitepapers/pdfs/shapefile.pdf
[tbp]: https://pypi.python.org/pypi/typing
[pbp]: https://pypi.python.org/pypi/pathlib2
