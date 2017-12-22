Command-line interface
======================

.. highlight:: bash

The ``dbfr`` command allows you to read records from a dBASE III file::


    usage: dbfr [-h] [--encoding ENCODING] [--delimiter DELIMITER] [--quote QUOTE]
                [--quote-always] [--escape ESCAPE] [--no-header] [--crlf]
                filename

    Convert a dBase III file to CSV.

    positional arguments:
      filename

    optional arguments:
      -h, --help            show this help message and exit
      --encoding ENCODING, -e ENCODING
                            set encoding used to decode the DBF input
      --delimiter DELIMITER, -d DELIMITER
                            set field separator for CSV output
      --quote QUOTE, -q QUOTE
                            set quote character for CSV output
      --quote-always        quote all fields in output
      --escape ESCAPE       set character used to escape a quote character
      --no-header, -n       don't output column names in the first row
      --crlf                use '\r\n' line endings in the output
