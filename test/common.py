import os
import pytest
import subprocess

@pytest.fixture(autouse=True)
def tmp_run_dir(monkeypatch, tmp_path):
    """Fixture running each test in an isolated, temporary directory"""
    monkeypatch.chdir(tmp_path)

class CliExecutor:
    def __init__(self, monkeypatch, tool_name, main_function):
        self._monkeypatch = monkeypatch
        self._tool_name = tool_name
        self.main_function = main_function

    def __call__(self, arg_list=[]):
        self._args = [self._tool_name] + arg_list
        self._monkeypatch.setattr("sys.argv", self._args)
        with pytest.raises(SystemExit) as retval:
            self.main_function()
        return retval.value.code

def syntax_check(file_name, flags=[]):
    p = subprocess.Popen(["iverilog",] + flags + [file_name,] , stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    assert not int(p.returncode)
    assert not stdout.decode('utf8')

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

    assert bool(out) ^ expect_stdout_empty, "stderr_lenght:%d stdout_lenght:%d" % (len(err), len(out))

    assert bool(err) ^ expect_stderr_empty, "stderr_lenght:%d stdout_lenght:%d" % (len(err), len(out)) + err

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
