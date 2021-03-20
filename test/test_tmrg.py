import os
import pytest

@pytest.fixture(autouse=True)
def tmp_run_dir(monkeypatch, tmp_path):
    """Fixture running each test in an isolated, temporary directory"""
    monkeypatch.chdir(tmp_path)

class CliArgPatcher:
    def __init__(self, monkeypatch):
        self._monkeypatch = monkeypatch
        self._args = ["tmrg"]
        self._monkeypatch.setattr("sys.argv", self._args)
    
    def add_args(self, arg_list):
        self._args += arg_list

@pytest.fixture
def cli_args(monkeypatch):
    patcher = CliArgPatcher(monkeypatch)
    yield patcher


def expect_in_stderr(string, capture):
    assert string in str(capture.readouterr())

def expect_not_in_stderr(string, capture):
    assert string not in str(capture.readouterr())

def run_tmrg():
    """Execute tmrg main, verify it exists using sys.exit(), return exit code"""
    from tmrg.tmrg import main as tmrg_main
    with pytest.raises(SystemExit) as retval:
        tmrg_main()
    return retval.value.code

def test_no_arguments(capfd):
    """Generate error message and return code without manifest"""
    assert not run_tmrg()  # TODO / BUG: Why does tmake not return 1 when this error is encountered?
    expect_in_stderr("No modules found. Please refer to the documentation", capfd)

