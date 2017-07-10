"""
Command-line interface to the library's functionality.

This module provides the following functions that are registered as
'console script' entry points in ``setup.py``:

* :func:`dbf_to_csv`: convert dBase III files to CSVs (as command
  ``dbfr``)

When the package is installed via setuptools (e.g. using
``pip install``) the commands are immediately available to the user.
"""
from argparse import ArgumentParser, ArgumentTypeError
import codecs
import csv
import pathlib
import sys

from spaceland.dbf import DbaseFile


def extant_file(arg: str) -> pathlib.Path:
    """Type-check an argument to ensure it names an existing file."""
    filename = pathlib.Path(arg)
    if filename.exists() and filename.is_file():
        return filename
    raise ArgumentTypeError('file {!r} does not exist'.format(arg))


def valid_codec(arg: str) -> str:
    """Type-check an argument to ensure it names an known codec."""
    try:
        codecs.lookup(arg)
    except LookupError:
        raise ArgumentTypeError('unsupported encoding {!r}'.format(arg))


def single_char(arg: str) -> str:
    """Type-check an argument to ensure it's a string of length one."""
    if len(arg) != 1:
        msg = 'must be a single character (not {!r})'.format(arg)
        raise ArgumentTypeError(msg)
    return arg


def dbf_to_csv() -> None:
    """
    Read a dBase III file and convert it to a CSV.

    Used as a 'console script' entry point in ``setup.py`` and available
    on the command-line as ``dbfr``. The dBase III file named as an
    argument is parsed and converted to CSV, and output to ``stdout``.
    The CSV dialect used can be configured using command-line options,
    as can the character-encoding used when reading the dBase file.
    """
    # Ensure ``SIGPIPE`` doesn't throw an exception. This prevents the
    # ``[Errno 32] Broken pipe`` error you see when, e.g., piping to ``head``.
    # For details see http://bugs.python.org/issue1652.
    try:
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (ValueError, AttributeError):
        # Do nothing on platforms without signals or ``SIGPIPE``.
        pass

    parser = ArgumentParser(description='Convert a dBase III file to CSV.',
                            allow_abbrev=False)
    parser.add_argument('filename', type=extant_file)
    parser.add_argument('--encoding', '-e', type=valid_codec,
                        help='set encoding used to decode the DBF input')
    parser.add_argument('--delimiter', '-d', default=',', type=single_char,
                        help='set field separator for CSV output')
    parser.add_argument('--quote', '-q', default='"', type=single_char,
                        help='set quote character for CSV output')
    parser.add_argument('--quote-always', action='store_true',
                        help='quote all fields in output')
    parser.add_argument('--escape', type=single_char,
                        help='set character used to escape a quote character')
    parser.add_argument('--no-header', '-n', action='store_true',
                        help="don't output column names in the first row")
    parser.add_argument('--crlf', dest='line_end', action='store_const',
                        const='\r\n', default='\n',
                        help=r"use '\r\n' line endings in the output")
    args = parser.parse_args()

    # If the user didn't set an encoding using the ``--encoding`` argument,
    # attempt to read it from the .cpg file that often accompanies the .dbf
    # file. This must be a file with single line of ascii text that provides
    # the name of the character-encoding.
    if args.encoding is None:
        try:
            with args.filename.with_suffix('.cpg').open() as cpg:
                encoding = cpg.readline().strip()
            codecs.lookup(encoding)
        except (FileNotFoundError, LookupError):
            # Use dBase III's default encoding if there is no .cpg file, or it
            # doesn't name a supported character-encoding.
            encoding = 'ascii'
    else:
        encoding = args.encoding

    # Set the CSV dialect to use in the output. Based upon the arguments
    # provided by the user. If the user doesn't specify anything, the defaults
    # defined in the :mod:`csv` module are used.
    dialect = dict(delimiter=args.delimiter, quotechar=args.quote,
                   lineterminator=args.line_end)
    if args.escape is not None:
        dialect['doublequote'] = False
        dialect['escapechar'] = args.escape
    if args.quote_always:
        dialect['quoting'] = csv.QUOTE_ALL

    rows = csv.writer(sys.stdout, **dialect)
    with args.filename.open('rb') as fh:
        dbf = DbaseFile(fh, encoding)
        if not args.no_header:
            rows.writerow(field.name for field in dbf.fields)
        rows.writerows(dbf)


if __name__ == '__main__':
    dbf_to_csv()
