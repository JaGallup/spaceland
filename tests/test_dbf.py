"""Test the promises made by :mod:`spaceland.dbf`."""
import datetime

import pytest

from spaceland.dbf import DbaseFile


@pytest.fixture
def dbase_file_handle():
    """Fixture to provide a file handle to a DBase file."""
    with open("tests/data/eu1995.dbf", "rb") as fh:
        yield fh


@pytest.fixture
def dbase_file(dbase_file_handle):
    """Fixture to provide a :class:`spaceland.dbf.DbaseFile` object."""
    yield DbaseFile(dbase_file_handle)


def test_metadata(dbase_file):
    """Test the metadata in the DBase file header is parsed correctly."""
    assert dbase_file.encoding == "ascii"
    assert dbase_file.num_records == 15
    assert dbase_file.header_length == 193
    assert dbase_file.record_length == 36

    field_names = [f.name for f in dbase_file.fields]
    field_types = [f.type for f in dbase_file.fields]
    field_lengths = [f.length for f in dbase_file.fields]
    field_decimals = [f.decimals for f in dbase_file.fields]
    assert field_names == ["country", "since", "area", "pop_density",
                           "founder"]
    assert field_types == [str, datetime.date, int, float, bool]
    assert field_lengths == [14, 8, 6, 6, 1]
    assert field_decimals == [0, 0, 0, 3, 0]


def test_record(dbase_file):
    """Test that a record in a DBase file is parsed correctly."""
    sweden = dbase_file.record(13)
    assert sweden.country == "Sweden"
    assert sweden.since == datetime.date(1995, 1, 1)
    assert sweden.area == 449964
    assert sweden.pop_density == 21.89
    assert sweden.founder is False
    assert isinstance(sweden.country, str)
    assert isinstance(sweden.since, datetime.date)
    assert isinstance(sweden.area, int)
    assert isinstance(sweden.pop_density, float)
    assert isinstance(sweden.founder, bool)


def test_getitem(dbase_file):
    """Test records can be accessed as keys."""
    assert dbase_file[2].country == "Denmark"
    assert dbase_file[-3].country == "Spain"
    assert dbase_file[-1] == dbase_file[14]
    assert dbase_file[0] == dbase_file[-15]
    with pytest.raises(IndexError):
        dbase_file[15]
    with pytest.raises(IndexError):
        dbase_file[-16]
    with pytest.raises(TypeError):
        dbase_file["0"]


def test_iteration(dbase_file):
    """Test :class:`spaceland.dbf.DbaseFile` is iterable."""
    records = list(dbase_file.records())
    assert len(dbase_file) == len(records)
    assert records == [record for record in dbase_file]


def test_context_management(dbase_file_handle):
    """Test :class:`spaceland.dbf.DbaseFile` is a context manager."""
    with DbaseFile(dbase_file_handle) as dbase_file:
        assert dbase_file[0].country == "Austria"


def test_random_access(dbase_file):
    """Test records in a DBase file can be accessed randomly."""
    assert dbase_file.record(2).country == "Denmark"
    assert dbase_file.record(-3).country == "Spain"
