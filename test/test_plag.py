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
