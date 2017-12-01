"""Test the promises made by :mod:`spaceland.shp`."""
import pytest

from spaceland.shp import Shapefile


@pytest.fixture
def shp_file_handle():
    """Fixture to provide a file handle to a shapefile."""
    with open("tests/data/points.shp", "rb") as fh:
        yield fh


@pytest.fixture
def shp_file(shp_file_handle):
    """Fixture to provide a :class:`spaceland.shp.Shapefile` object."""
    yield Shapefile(shp_file_handle)


def test_metadata(shp_file):
    """Test the metadata in the shapefile header is parsed correctly."""
    assert shp_file.meta.shape_type == Shapefile.POINT


def test_iteration(shp_file):
    """Test :class:`spaceland.shp.Shapefile` is iterable."""
    records = [record for record in shp_file]
    assert len(records) == 28
    assert type(records[0]) == tuple


def test_context_management(shp_file_handle):
    """Test :class:`spaceland.shp.Shapefile` is a context manager."""
    with Shapefile(shp_file_handle) as shapefile:
        assert list(shapefile)[0] == (16.37, 48.20)


def test_invalid_type():
    with open("tests/data/invalid_type.shp", "rb") as fh:
        with pytest.raises(ValueError):
            list(Shapefile(fh))


def test_null_records():
    with open("tests/data/null.shp", "rb") as fh:
        s = Shapefile(fh)
        assert len(list(s)) == 100
        for null_shape in s:
            assert null_shape == ()
