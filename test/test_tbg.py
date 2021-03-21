import os
import pytest
from .common import *
from tmrg.tbg import main as tbg_main

@pytest.fixture
def tbg(monkeypatch):
    return CliArgPatcher(monkeypatch, "tbg", main_function=tbg_main)

def test_tbg_no_arguments(tbg, capfd):
    assert tbg()
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["You have to specify verilog file name"])

