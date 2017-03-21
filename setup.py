from setuptools import setup


setup(name="Spaceland",
      version="0.1.0-dev",
      description="Python 3 library for fast, Pythonic access to shapefiles",
      author="Matt Riggott",
      author_email="matt@ja.is",
      url="https://github.com/JaGallup/spaceland",
      license="MIT",
      packages=["spaceland"],
      install_requires=["typing;python_version<'3.5'"],
      extras_require={
          "test": ["tox", "pytest>=3.0.0", "pytest-pep8", "pytest-cov"]
      })
