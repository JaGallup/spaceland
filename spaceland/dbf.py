"""
Reads the subset of the dBase III file format used by ESRI shapefiles.

The dBase III format was never specified publicly but it has been
reverse-engineered. The best documentation on the subject can be found
at http://www.clicketyclick.dk/databases/xbase/format/dbf.html.
"""
from collections import namedtuple
from datetime import date
from struct import Struct
from typing import Optional, IO, Callable, Iterable


def get_parse_str(encoding: str) -> Callable[[bytes], str]:
    """
    Returns a function that decodes bytes to strings.

    The returned function decodes the bytes using the character encoding
    passed to this function.

    >>> utf8 = get_parse_str("UTF-8")
    >>> utf8(b"\xf0\x9f\x91\x8d")
    '👍'

    Args:
        encoding: The name of a character encoding that can be used to
            decode the bytes to a string.

    Returns:
        A function that uses the given character encoding to convert
        bytes to strings.
    """
    def parse_str(value: bytes) -> str:
        """
        Converts bytes to a string using a preset character encoding.

        Args:
            value: A bytes value to be converted to a string.

        Returns:
            A string if the bytes value can be decoded using the preset
            character encoding, but ``None`` otherwise.
        """
        try:
            return value.decode(encoding).strip()
        except UnicodeDecodeError:
            return None
    return parse_str


def parse_float(value: bytes) -> Optional[float]:
    """
    Converts bytes to a float.

    Args:
        value: A bytes value to be converted to a float.

    Returns:
        A float if the bytes value is a valid numeric value, but
        ``None`` otherwise.
    """
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: bytes) -> Optional[int]:
    """
    Converts bytes to an integer.

    Args:
        value: A bytes value to be converted to an integer.

    Returns:
        An integer if the bytes value is a valid numeric value, but
        ``None`` otherwise.
    """
    try:
        return int(value)
    except ValueError:
        return None


def parse_date(value: bytes) -> Optional[date]:
    """
    Converts bytes in the format ``YYYYMMDD`` to a datetime.date object.

    Args:
        value: A bytes value to be converted to a date.

    Returns:
        A datetime.date object if the bytes value is a valid date, but
        ``None`` otherwise.
    """
    try:
        return date(*map(int, (value[:4], value[4:6], value[6:])))
    except ValueError:
        return None


def parse_bool(value: bytes) -> Optional[bool]:
    """
    Converts bytes to a boolean value.

    Args:
        value: A bytes value to be converted to a boolean value.

    Returns:
        ``True`` if the bytes value is ``Y``, ``y``, ``T``, or ``t``;
        ``False`` if the bytes value is ``N``, ``n``, ``F``, or ``f``;
        ``None`` otherwise.
    """
    if value in b"YyTt":
        return True
    elif value in b"NnFf":
        return False
    else:
        return None


class DbaseFile:

    """
    Reads fields and records from a dBase III binary file.

    A dBase III file is a simple tabular data format consisting of a
    header, fields (columns), and records (rows). Fields are typed; as
    used in the ESRI shapefile format, the records in a dBase III file
    must have one of five field types: string, float, integer, date, or
    boolean. All types allow null values.

    Class objects allow for iteration and slicing, and they also work
    as context managers.

    >>> with DbaseFile(open("example.dbf", "rb")) as dbase_file:
    ...     for rec in dbase_file:
    ...         print(rec)
    """

    def __init__(self, dbf: IO[bytes], encoding: str = "ascii") -> None:
        """
        Args:
            dbf: A binary file open for reading.
            encoding: A name of a character encoding.

        Raises:
            TypeError: A field has an unsupported type.
        """
        dbf.seek(0)
        # The first 32 bits of the file contains various metadata but only
        # three of interest: number of records in the file; length of the
        # header structure; and length of each record.
        header = Struct("<4xI2H20x")
        num_records, header_length, record_length = header.unpack(dbf.read(32))
        field = namedtuple("Field", "name type length decimals")
        fields = []
        field_parsers = []
        # Field definitions are 32 bits. Before the definitions the header has
        # 32 bits, afterwards is a single termination bit. Take 33 from the
        # header length to see how many bits there are for the field
        # definitions.
        for _ in range(0, header_length - 33, 32):
            # The 32-bit field descriptor contans four things of interest:
            # field name in ASCII; field type; length of values in bits; and
            # exponent for floating point values.
            field_info = Struct("<11sc4x2B14x").unpack(dbf.read(32))
            field_name = field_info[0].decode().strip("\x00")
            if field_info[1] == b"C":
                # C = character. Its values are strings. The bytes must be
                # decoded (default is ASCII).
                field_type = str
                field_parser = get_parse_str(encoding)
            elif field_info[1] in b"NF":
                # N = number, F = floating point. F is part of dBase IV, not
                # III, but it's still used by shapefiles.
                if field_info[3] > 0:
                    # There's an exponent so it's a floating-point number.
                    field_type = float
                    field_parser = parse_float
                else:
                    field_type = int
                    field_parser = parse_int
            elif field_info[1] == b"D":
                # D = date. Values are formatted YYYYMMDD.
                field_type = date
                field_parser = parse_date
            elif field_info[1] == b"L":
                # L = logical.
                field_type = bool
                field_parser = parse_bool
            else:
                raise TypeError("unknown field type {}".format(field_info[1]))
            fields.append(field(field_name, field_type, *field_info[2:]))
            field_parsers.append(field_parser)

        self.dbf = dbf
        self.encoding = encoding
        self.num_records = num_records
        self.header_length = header_length
        self.record_length = record_length
        self.fields = tuple(fields)
        self.field_parsers = tuple(field_parsers)

    def __len__(self) -> int:
        return self.num_records

    def __getitem__(self, key: int) -> tuple:
        if isinstance(key, int):
            if key >= self.num_records or key < -self.num_records:
                raise IndexError("index out of range")
            return self.record(key)
        raise TypeError("indices must be integers")

    def __iter__(self) -> Iterable[tuple]:
        yield from self.records()

    def __enter__(self) -> "DbaseFile":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.dbf.close()

    def records(self, start: int = 0) -> Iterable[tuple]:
        """
        Yields the records in the file.

        A record is a set of fields and their values. The field names,
        types, and order are consistent across all records in the file.

        It's possible that a field has an invalid value (e.g. a
        non-numeric value in an integer field). When this happens the
        value becomes ``None`` and no error is raised.

        Args:
            start: The record from which to start iteration. By default
                starts with the first record in the file.

        Yields:
            A namedtuple, each item matching one field in the record.
            Item names and order are consistent across records within
            the same file, but will differ between files.
        """
        self.dbf.seek(self.header_length + (self.record_length * start))
        record = namedtuple("Record", (f.name for f in self.fields))
        record_length = self.record_length
        unpack = Struct("<x" + "".join("{}s".format(f.length)
                                       for f in self.fields)).unpack
        read = self.dbf.read
        for _ in range(self.num_records):
            yield record(*(self.field_parsers[i](v)
                           for i, v in enumerate(unpack(read(record_length)))))

    def record(self, index: int) -> tuple:
        """
        Returns the record at the given index.

        Args:
            index: The position of the record relative to the beginning
                of the file.

        Returns:
            A namedtuple, each item matching one field in the record.
        """
        if index < 0:
            index = self.num_records + index
        return next(self.records(index))
