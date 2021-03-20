import os
import pytest
from .common import *
from tmrg.plag import main as plag_main

@pytest.fixture
def plag(monkeypatch):
    return CliArgPatcher(monkeypatch, "plag", main_function=plag_main)

def test_plag_no_arguments(plag, capfd):
    assert plag()
    expect_in_stderr("You have to specify netlist file name", capfd)

def test_plag_missing_file(plag, capfd):
    assert plag(["not_existing.v"])
    expect_in_stderr("File or directory does not exists", capfd)

def test_plag_version(plag, capfd):
    assert not plag(["--version"])
    expect_in_stdout("PLAG", capfd)

def test_plag_help(plag, capfd):
    assert not plag(["--help"])
    expect_in_stdout("Usage: plag", capfd)

def test_plag_invalid_option(plag, capfd):
    assert not plag(["--no-such-option"])
    expect_in_stdout("no such option", capfd)

def test_plag_invalid_option(plag, capfd):
    file_name = os.path.join(os.path.dirname(__file__), "verilog/verilogError.v")
    assert plag([file_name])
    expect_in_stderr("Error during parsing", capfd)

def test_plag_config_does_not_exist(plag, capfd):
    netlist = os.path.join(os.path.dirname(__file__), "netlist/accTMR.v")
    lib = os.path.join(os.path.dirname(__file__), "libs/tcbn65lp.v")
    assert plag([netlist, '-l', lib, '-c', 'do_not_exists'])
    expect_in_stderr("Command line specified config file does not exists", capfd)

def test_plag_working(plag, capfd):
    netlist = os.path.join(os.path.dirname(__file__), "netlist/accTMR.v")
    lib = os.path.join(os.path.dirname(__file__), "libs/tcbn65lp.v")
    cnf_file = os.path.join(os.path.dirname(__file__), "cnf/plag.cfg")
    assert not plag([netlist, '-l', lib, '-c', cnf_file])

def test_plag_working_exclude(plag, capfd):
    netlist = os.path.join(os.path.dirname(__file__), "netlist/accTMR.v")
    lib = os.path.join(os.path.dirname(__file__), "libs/tcbn65lp.v")
    exclude_file = os.path.join(os.path.dirname(__file__), "cnf/exclude.txt")
    assert not plag([netlist, '-l', lib, '--exclude', exclude_file, '--cells=DFCNQD1'])

