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


class TestTbgOnSingleSystemVerilogFile():
    @pytest.mark.parametrize(
        'verilog_file', [
            "systemverilog/tbg_arrays.sv",
        ]
    )

    def test_tbg_on_file(self, tbg, capfd, verilog_file):
      basefile = file_in_test_dir(verilog_file)
      syntax_check(basefile, cmds=["iverilog -g2012"])
      x = tbg([file_in_test_dir(verilog_file)])
      out, err = capfd.readouterr()
      tb_file = file_in_test_dir(verilog_file).replace(".sv", "_tb.sv")
      assert bool(err)==False, "stderr_lenght:%d stdout_lenght:%d" % (len(err), len(out)) + err
      with open(tb_file, "w") as fout:
          fout.write(out)
      syntax_check(basefile, cmds=["iverilog -g2012 %s" % tb_file])
