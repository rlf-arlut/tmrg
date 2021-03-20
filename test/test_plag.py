import os
import pytest
from .common import *
from tmrg.plag import main as plag_main

@pytest.fixture
def plag_env(monkeypatch):
    return CliArgPatcher(monkeypatch, "plag")

def plag(plag_env, args=[]):
    """Execute plag main, verify it exists using sys.exit(), return exit code"""
    plag_env.add_args(args)
    with pytest.raises(SystemExit) as retval:
        plag_main()
    return retval.value.code

def test_plag_no_arguments(plag_env, capfd):
    assert plag(plag_env)
    expect_in_stderr("You have to specify netlist file name", capfd)

def test_plag_missing_file(plag_env, capfd):
    assert plag(plag_env, ["not_existing.v"])
    expect_in_stderr("File or directory does not exists", capfd)

