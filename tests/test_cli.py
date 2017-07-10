def test_dbfr_requires_filename(script_runner):
    """Test ``dbfr`` requires a filename argument."""
    ret = script_runner.run("dbfr")
    assert not ret.success


def test_dbfr_requires_valid_filename(script_runner):
    """Test ``dbfr`` requires an extant filename argument."""
    ret = script_runner.run("dbfr", "eggs")
    assert not ret.success


def test_dbfr_requires_valid_codes(script_runner):
    """Test that an invalid codec names raises an error."""
    ret = script_runner.run("dbfr", "--encoding", "eggs")
    assert not ret.success
    assert "unsupported encoding 'eggs'" in ret.stderr


def test_dbfr_output(script_runner):
    """Test default output of ``dbfr`` is as expected."""
    ret = script_runner.run("dbfr", "tests/data/eu1995.dbf")
    assert ret.success
    lines = ret.stdout.splitlines()
    assert lines[0] == "country,since,area,pop_density,founder"
    assert lines[1] == "Austria,1995-01-01,83855,103.76,False"
    assert lines[-2] == "United Kingdom,1973-01-01,243610,268.22,False"
    assert lines[-1] == ",,,,"


def test_dbfr_output_no_header(script_runner):
    """Test ``dbfr --no-header`` doesn't output a CSV header row."""
    ret = script_runner.run("dbfr", "--no-header", "tests/data/eu1995.dbf")
    assert ret.success
    lines = ret.stdout.splitlines()
    assert lines[0] == "Austria,1995-01-01,83855,103.76,False"


def test_dbfr_delimiter_and_escape(script_runner):
    """Test CSV dialect can be set using ``dbfr`` optional arguments."""
    ret = script_runner.run("dbfr", "--no-header", "--delimiter", ".",
                            "--quote", "'", "--quote-always",
                            "tests/data/eu1995.dbf")
    assert ret.success
    lines = ret.stdout.splitlines()
    assert lines[0] == "'Austria'.'1995-01-01'.'83855'.'103.76'.'False'"


def test_quote_argument(script_runner):
    """Test that a multi-character quote argument is invalid."""
    ret = script_runner.run("dbfr", "--quote", "eggs")
    assert not ret.success
    assert "argument --quote/-q: must be a single character" in ret.stderr
