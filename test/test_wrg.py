import os
import pytest
from .common import *
from tmrg.wrg import main as wrg_main

@pytest.fixture
def wrg(monkeypatch):
    return CliArgPatcher(monkeypatch, "wrg", main_function=wrg_main)

def test_wrg_no_arguments(wrg, capfd):
    assert wrg()
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["You have to specify netlist file name"])

