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

