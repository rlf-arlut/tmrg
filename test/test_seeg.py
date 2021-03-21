import os
import pytest
from .common import *
from tmrg.seeg import main as seeg_main

@pytest.fixture
def seeg(monkeypatch):
    return CliArgPatcher(monkeypatch, "seeg", main_function=seeg_main)

def test_seeg_no_arguments(seeg, capfd):
    assert seeg()
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["You have to specify netlist file name"])

def test_seeg_missing_file(seeg, capfd):
    assert seeg(["not_existing.v"])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["File or directory does not exists"])

def test_seeg_version(seeg, capfd):
    assert not seeg(["--version"])
    assert_output_streams(capfd, expect_stdout_empty=False, expect_in_stdout=["SEEG"])

def test_seeg_help(seeg, capfd):
    assert not seeg(["--help"])
    assert_output_streams(capfd, expect_stdout_empty=False, expect_in_stdout=["Usage: seeg", "Options:", "--verbose"])

def test_seeg_invalid_option(seeg, capfd):
    assert seeg(["--no-such-option"])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["no such option"])

def test_seeg_working(seeg, capfd):
    assert not seeg([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '--exclude', file_in_test_dir("cnf/exclude.txt")])
    assert_output_streams(capfd)
    assert os.path.isfile("see.v")

def test_seeg_error_in_verilog(seeg, capfd):
    file_name = os.path.join(os.path.dirname(__file__), "verilog/verilogError.v")
    assert seeg([file_name])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Error during parsing"])

def test_seeg_missing_library(seeg, capfd):
    assert seeg([file_in_test_dir("netlist/accTMR.v")])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Serious error during elaboration", "Unknown module instantiation"])

def test_seeg_working_verbose(seeg, capfd):
    assert not seeg([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '-v'])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["SEE file is stored to ", "SET nets in the design"], forbid_in_stderr=["DUT.doutNextVoterA.Fp8068A.ZN"])
    assert os.path.isfile("see.v")

def test_seeg_working_very_verbose(seeg, capfd):
    assert not seeg([file_in_test_dir("netlist/accTMR.v"), '-l', file_in_test_dir("libs/tcbn65lp.v"), '-vv'])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["SEE file is stored to ", "SET nets in the design", "DUT.doutNextVoterA.Fp8068A.ZN"])
    assert os.path.isfile("see.v")

