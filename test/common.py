import os
import pytest

@pytest.fixture(autouse=True)
def tmp_run_dir(monkeypatch, tmp_path):
    """Fixture running each test in an isolated, temporary directory"""
    monkeypatch.chdir(tmp_path)

class CliArgPatcher:
    def __init__(self, monkeypatch, tool_name):
        self._monkeypatch = monkeypatch
        self._args = [tool_name]
        self._monkeypatch.setattr("sys.argv", self._args)
    
    def add_args(self, arg_list):
        self._args += arg_list

#
# Helper functions
#
def expect_in_stderr(string, capture):
    assert string in str(capture.readouterr())

def expect_not_in_stderr(string, capture):
    assert string not in str(capture.readouterr())

