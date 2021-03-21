import os
import pytest
from .common import *
from tmrg.tmrg import main as tmrg_main

@pytest.fixture
def tmrg(monkeypatch):
    return CliArgPatcher(monkeypatch, "tmrg", main_function=tmrg_main)

def test_tmrg_no_arguments(tmrg, capfd):
    assert tmrg()
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["No modules found. Please refer to the documentation"])

def test_tmrg_missing_file(tmrg, capfd):
    assert tmrg(["not_existing.v"])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["File or directory does not exists"])

class TestTmrgOnFile():
    @pytest.mark.parametrize(
        'verilog_file', [
            "verilog/always.v",
            "verilog/alwaysComma.v",
            "verilog/case01.v",
            "verilog/function.v",
            "verilog/index.v",
            "verilog/lib.v",
            "verilog/params3.v",
            "verilog/test03.v",
            "verilog/translate.v",
            "verilog/always.v",
            "verilog/case02.v",
            "verilog/generate01.v",
            "verilog/assigment03.v",
            "verilog/generate04.v",
            "verilog/initial01.v",
            "verilog/logic.v",
            "verilog/params4.v",
            "verilog/params5.v",
            "verilog/testsRadu.v",
            "verilog/var.v",
            "verilog/instanceInOut.v",
            "verilog/ansiPorts.v",
            "verilog/comb00.v",
            "verilog/defines.v",
            "verilog/hier01.v",
            "verilog/sysCall.v",
            "verilog/inlineif01.v",
            "verilog/mux.v",
            "verilog/params.v",
            "verilog/tmr1.v",
            "verilog/wire.v",
            "verilog/arrays.v",
            "verilog/comb02.v",
            "verilog/forLoop.v",
            "verilog/for.v",
            "verilog/hier02.v",
            "verilog/instantiation.v",
            "verilog/netdeclaration.v",
            "verilog/portDeclaration.v",
            "verilog/tmr2.v",
            "verilog/assigment.v",
            "verilog/compDirectives.v",
            "verilog/fsm01.v",
            "verilog/hier03.v",
            "verilog/instTmrError.v",
            "verilog/notxor.v",
            "verilog/slice01.v",
            "verilog/noports.v",
            "../examples/slice.v",
            "verilog/tmr3.v",
            "verilog/ifdef.v",
            "verilog/underscore.v",
            "verilog/begin.v",
            "verilog/complexInst.v",
            "verilog/function2.v",
            "verilog/params2.v",
            "verilog/test02.v",
            "verilog/tmrError01.v",
            "verilog/tmrError04.v",
            "verilog/tmrError05.v",
            "verilog/tmrError06.v",
            "../examples/clockGating01.v",
            "../examples/comb02.v",
            "../examples/comb05.v",
            "../examples/dff.v",
            "../examples/fsm03.v",
            "../examples/inst02.v",
            "../examples/resetBlock02.v",
            "../examples/tmrOut01.v",
            "../examples/clockGating02.v",
            "../examples/clockGating02.v",
            "../examples/configcell.v",
            "../examples/comb03.v",
            "../examples/comb06.v",
            "../examples/fsm01.v",
            "../examples/fsm04.v",
            "../examples/inst03.v",
            "../examples/resetBlock03.v",
            "../examples/vote01.v",
            "../examples/comb01.v",
            "../examples/comb04.v",
            "../examples/comb07.v",
            "../examples/fsm02.v",
            "../examples/inst01.v",
            "../examples/resetBlock01.v",
            "../examples/resetBlock04.v",
            "../examples/vote02.v",
            "../examples/pipelineWithSeuCoutner.v",
            "verilog/tmrErrorExclude.v",
            "verilog/vectorRange.v",
            "verilog/generate05.v",
            "verilog/generate06.v",
            "verilog/wor01.v",
            "verilog/wor02.v",
            "verilog/generate_if.v",
            "verilog/force_release.v",
            "verilog/default_nettype.v",
            "verilog/compDirectivesComment.v",
        ]
    )

    def test_tmrg_on_file(self, tmrg, capfd, verilog_file):
      assert not tmrg([file_in_test_dir(verilog_file)])
      assert_output_streams(capfd)


