import os
import pytest

@pytest.fixture(autouse=True)
def tmp_run_dir(monkeypatch, tmp_path):
    """Fixture running each test in an isolated, temporary directory"""
    monkeypatch.chdir(tmp_path)

class CliArgPatcher:
    def __init__(self, monkeypatch, tool_name, main_function):
        self._monkeypatch = monkeypatch
        self._args = [tool_name]
        self._monkeypatch.setattr("sys.argv", self._args)
        self.main_function = main_function

    def __call__(self, arg_list=[]):
        self._args += arg_list
        with pytest.raises(SystemExit) as retval:
            self.main_function()
        return retval.value.code

#
# Helper functions
#

def assert_output_streams(
    capture,
    expect_stdout_empty=True,
    expect_stderr_empty=True,
    expect_in_stdout=[],
    expect_in_stderr=[],
    forbid_in_stdout=[],
    forbid_in_stderr=[]):

    out, err = capture.readouterr()

    assert bool(out) ^ expect_stdout_empty, "expect_stdout_empty: %s stdout_lenght:%d" % (expect_stdout_empty, len(out))

    assert bool(err) ^ expect_stderr_empty, "expect_stderr_empty: %s stderr_lenght:%d" % (expect_stderr_empty, len(err))

    for string in expect_in_stdout:
        assert string in out

    for string in expect_in_stderr:
        assert string in err

    for string in forbid_in_stdout:
        assert string not in out

    for string in forbid_in_stderr:
        assert string not in err

def file_in_test_dir(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)
