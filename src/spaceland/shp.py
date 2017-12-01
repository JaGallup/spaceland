"""
Read non-topological geometric records from the ESRI Shapefile format.

The Shapefile format was documented by ESRI in 1998 and is available in
a document titled `ESRI Shapefile Technical Description
<https://www.esri.com/library/whitepapers/pdfs/shapefile.pdf>`_.
"""
from collections import namedtuple
from struct import Struct, unpack, unpack_from
from typing import Callable, IO, Iterable


#: Named tuple containing metadata parsed from a shapefile header.
ShapefileMeta = namedtuple('ShapefileMeta',
                           ('shape_type', 'x_min', 'y_min', 'x_max', 'y_max',
                            'z_min', 'z_max', 'm_min', 'm_max'))


def parse_null_record(content: bytes) -> tuple:
    """
    Parse a null shape record from a shapefile.

    A null shape is an empty record with no geometric data. It can be
    used as a shape type for a shapefile but it's also valid as a
    placeholder in a shapefile of any other type. That is, a shapefile
    of polygons can also incude null shape records. This is the only
    valid way a shapefile can contain multiple shape types.

    Args:
        content: An empty byte string

    Returns:
        An empty tuple.
    """
    return ()


def parse_point_record(content: bytes) -> tuple:
    """
    Parse a point shape record from a shapefile.

    A point consists of a pair of double-precision coordinates ordered
    x, y.

    Args:
        content:
            16 bytes containing two 64-bit IEEE double-precision
            floating-point numbers, in little-endian byte order.

    Returns:
        An tuple containing a point in x, y order.
    """
    return unpack_from('<2d', content)


class Shapefile:
    """
    Read records from an ESRI shapefile.

    A shapefile is a binary format created by ESRI in the early 1990s
    for storing non-topographical geometries. After a short header
    containing file metadata the geometries are stored in a sequence of
    individual records. The format is compact and fast to read but
    because it can't contain indexes, details of the projection used, or
    metadata on individual shapes, it's commonly accompanied by other
    files (e.g. a dBase III database for geometry metadata).

    Class objects allow for iteration and can be used as context
    managers.
    """

    NULL_SHAPE = 0
    POINT = 1
    POLY_LINE = 3
    POLYGON = 5
    MULTI_POINT = 8
    POINT_Z = 11
    POLY_LINE_Z = 13
    POLYGON_Z = 15
    MULTI_POINT_Z = 18
    POINT_M = 21
    POLY_LINE_M = 23
    POLYGON_M = 25
    MULTI_POINT_M = 28
    MULTI_PATCH = 31

    #: Tuple of all valid shape type values.
    SHAPE_TYPES = (NULL_SHAPE, POINT, POLY_LINE, POLYGON, MULTI_POINT, POINT_Z,
                   POLY_LINE_Z, POLYGON_Z, MULTI_POINT_Z, POINT_M, POLY_LINE_M,
                   POLYGON_M, MULTI_POINT_M, MULTI_PATCH)

    #: Mapping from shape type to record parsing function.
    PARSE_FUNCTIONS = {
        NULL_SHAPE: parse_null_record,
        POINT: parse_point_record,
    }

    def __init__(self, shp: IO[bytes]) -> None:
        """
        Read geometric records from an ESRI Shapefile binary file.

        Args:
            shp: A binary file open for reading.
        """
        # First 100 bytes are the file header containing metadata. But the
        # first 32 bytes aren't useful, so skip them.
        shp.seek(0)
        shp.read(32)
        self.meta = ShapefileMeta(*unpack('<i8d', shp.read(68)))
        self.shp = shp

    def __iter__(self):
        yield from self.records()

    def __enter__(self) -> 'Shapefile':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.shp.close()

    def get_parse_function(self) -> Callable[[bytes], tuple]:
        """
        Return a function capable of parsing a particular type of shape.

        The function returned will be suitable for parsing shapefile
        records of one type (e.g. two-dimensional points). The type is
        defined in the header of the shapefile, and so the returned
        function will handle all non-null records within a single
        shapefile.
        """
        shape_type = self.meta.shape_type
        try:
            return self.PARSE_FUNCTIONS[shape_type]
        except KeyError:
            if shape_type in Shapefile.SHAPE_TYPES:
                raise NotImplementedError(
                    'shape type {!r} not supported'.format(shape_type))
            else:
                raise ValueError('invalid shape type {!r}'.format(shape_type))

    def records(self) -> Iterable[tuple]:
        """
        Yield all geometric records in the shapefile, one-by-one.

        Records are returned in file order. Records are returned as a
        tuple, with the structure of the tuple dependent on the shape
        type. The structure of each shape type's tuple is detailed in
        the shape parsing functions:

        * :func:`parse_null_record` for null shapes
        * :func:`parse_point_record` for two-dimensional points

        The appropriate parsing function for a file can be found using
        :meth:`Shapefile.get_parse_function`.
        """
        self.shp.seek(100)
        parse_record = self.get_parse_function()
        read = self.shp.read
        unpack_content_length = Struct('>4xi').unpack_from
        unpack_shape_type = Struct('<8xi').unpack_from
        while True:
            header = read(12)
            if not header:
                break  # End of the file.
            content_length, = unpack_content_length(header)
            shape_type, = unpack_shape_type(header)
            if shape_type == Shapefile.NULL_SHAPE:
                # Any shapefile, regardless of shape type, can contain null
                # shapes.
                yield parse_null_record(b'')
            else:
                # Content length is measured in 16-bit words and includes the
                # 32 bits used to store the record number and the content
                # length. Those two fields have already been read so to find
                # out how many bytes of this record are left to read, remove
                # the length of the fields already read and then multiply the
                # number of 16-bit words by two.
                record_content = read(2 * (content_length - 2))
                yield parse_record(record_content)
