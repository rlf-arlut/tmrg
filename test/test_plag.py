import os
import pytest
from .common import *
from tmrg.plag import main as plag_main

@pytest.fixture
def plag(monkeypatch):
    return CliArgPatcher(monkeypatch, "plag", main_function=plag_main)

def test_plag_no_arguments(plag, capfd):
    assert plag()
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["You have to specify netlist file name"])

def test_plag_missing_file(plag, capfd):
    assert plag(["not_existing.v"])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["File or directory does not exists"])

def test_plag_version(plag, capfd):
    assert not plag(["--version"])
    assert_output_streams(capfd, expect_stdout_empty=False, expect_in_stdout=["PLAG"])

def test_plag_help(plag, capfd):
    assert not plag(["--help"])
    assert_output_streams(capfd, expect_stdout_empty=False, expect_in_stdout=["Usage: plag", "Options:", "--verbose"])

def test_plag_invalid_option(plag, capfd):
    assert not plag(["--no-such-option"])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["no such option"])

def test_plag_invalid_option(plag, capfd):
    file_name = os.path.join(os.path.dirname(__file__), "verilog/verilogError.v")
    assert plag([file_name])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Error during parsing"])

def test_plag_config_does_not_exist(plag, capfd):
    assert plag([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '-c', 'do_not_exists'])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Command line specified config file does not exists"])

def test_plag_working(plag, capfd):
    assert not plag([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '-c', file_in_test_dir("cnf/plag.cfg")])
    assert_output_streams(capfd)

def test_plag_working_exclude(plag, capfd):
    assert not plag([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '--exclude', file_in_test_dir("cnf/exclude.txt"), '--cells=DFCNQD1'])
    assert_output_streams(capfd)

def test_plag_missing_library(plag, capfd):
    assert plag([file_in_test_dir("netlist/accTMR.v")])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Command line specified config file does not exists"])

def test_plag_missing_library(plag, capfd):
    assert plag([file_in_test_dir("netlist/accTMR.v")])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Serious error during elaboration"])

def test_plag_working_verbose(plag, capfd):
    assert not plag([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '-v'])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["SEE file is stored to "], forbid_in_stderr=["Instances to be placed : 0"])

def test_plag_working_very_verbose(plag, capfd):
    assert not plag([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '-vv'])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["SEE file is stored to ", "Instances to be placed : 0"])

