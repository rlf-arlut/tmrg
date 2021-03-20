import os
import pytest
from .common import *
from tmrg.seeg import main as seeg_main

@pytest.fixture
def seeg(monkeypatch):
    return CliArgPatcher(monkeypatch, "seeg", main_function=seeg_main)

def test_seeg_no_arguments(seeg, capfd):
    assert seeg()
    expect_in_stderr("You have to specify netlist file name", capfd)

def test_seeg_missing_file(seeg, capfd):
    assert seeg(["not_existing.v"])
    expect_in_stderr("File or directory does not exists", capfd)

