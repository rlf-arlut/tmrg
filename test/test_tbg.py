import os
import pytest
from .common import *
from tmrg.tbg import main as tbg_main

@pytest.fixture
def tbg(monkeypatch):
    return CliExecutor(monkeypatch, "tbg", main_function=tbg_main)

def test_tbg_no_arguments(tbg, capfd):
    assert tbg()
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["You have to specify verilog file name"])


class TestTbgOnSingleVerilogFile():
    @pytest.mark.parametrize(
        'verilog_file', [
            "verilog/tbg_arrays.v",
        ]
    )

    def test_tbg_on_file(self, tbg, capfd, verilog_file):
      syntax_check(file_in_test_dir(verilog_file), cmds=["iverilog"])
      assert not tbg([file_in_test_dir(verilog_file)])
      basename = os.path.basename(verilog_file)
      expected_tmr_file = basename.replace(".v", "TMR.v")
      assert_output_streams(capfd)
      assert os.path.isfile(expected_tmr_file)
      syntax_check(expected_tmr_file, cmds=["iverilog"])
