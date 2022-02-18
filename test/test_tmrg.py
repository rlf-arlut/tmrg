import os
import pytest
from .common import *
from tmrg.tmrg import main as tmrg_main

@pytest.fixture
def tmrg(monkeypatch):
    return CliExecutor(monkeypatch, "tmrg", main_function=tmrg_main)

def test_tmrg_no_arguments(tmrg, capfd):
    assert tmrg()
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["No modules found. Please refer to the documentation"])

def test_tmrg_missing_file(tmrg, capfd):
    assert tmrg(["not_existing.v"])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["File or directory does not exists"])

def test_tmrg_simple_verilog(tmrg, capsys):
    assert not tmrg([file_in_test_dir("verilog/always.v")])
    assert_output_streams(capsys)

def test_tmrg_multiple_top_files(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/topModule.v")])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["The design has multiple top cells"])

def test_tmrg_multiple_top_modules_specify(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/topModule.v"), "--top-module=m1"])
    assert_output_streams(capfd)

def test_tmrg_include(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/include.v"), "--include", "--inc-dir", file_in_test_dir("verilog")])
    assert_output_streams(capfd)

def test_tmrg_include_lib(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/libtest.v"), "--lib", file_in_test_dir("verilog/lib.v")])
    assert_output_streams(capfd)

def test_tmrg_stats(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/fsm01.v"), "--stats"])
    assert_output_streams(capfd, expect_stdout_empty=False, expect_in_stdout=["Total number of files parsed:", "Total number of lines parsed"])

def test_tmrg_warning_left_hand_side_concatenation(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/leftSideConcatenation.v")])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Unsupported syntax : concatenation on left hand side of the assignment", "Output may be incorrect."])

def test_tmrg_hierahical(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/hier/m1.v"), file_in_test_dir("verilog/hier/m2.v"), file_in_test_dir("verilog/hier/m3.v"), file_in_test_dir("verilog/hier/m4.v"), file_in_test_dir("verilog/hier/m5.v"), file_in_test_dir("verilog/hier/top.v")])
    assert_output_streams(capfd)

def test_tmrg_output_log(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/fsm01.v"), "--log", "fsm01.log", "-v" ])
    assert_output_streams(capfd, expect_stderr_empty=False)
    assert os.path.isfile("fsm01.log")

def test_tmrg_generate_bug_report(tmrg, capfd):
    assert not tmrg([file_in_test_dir("verilog/fsm01.v"), "--generate-report"])
    assert_output_streams(capfd, expect_stderr_empty=False, expect_in_stderr=["Creating zip archive with bug report"])
    # FIXME: check if archive exists

class TestTmrgOnSingleVerilogFile():
    @pytest.mark.parametrize(
        'verilog_file', [
            "verilog/always.v",
            "verilog/alwaysComma.v",
            "verilog/case01.v",
            "verilog/dreg.v",
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
            "verilog/port_names.v",
            "verilog/tmr2.v",
            "verilog/assigment.v",
            "verilog/compDirectives.v",
            "verilog/fsm01.v",
            "verilog/hier03.v",
            "verilog/instTmrError.v",
            "verilog/notxor.v",
            "verilog/slice01.v",
            "verilog/noports.v",
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
            "verilog/casez01.v",
            "verilog/casez02.v",
            "verilog/casex01.v",
            "verilog/casex02.v",
            "verilog/multidimentionalarray.v",
            "../examples/slice.v",
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
        ]
    )

    def test_tmrg_on_file(self, tmrg, capfd, verilog_file):
      syntax_check(file_in_test_dir(verilog_file), cmds=["iverilog"])
      assert not tmrg([file_in_test_dir(verilog_file)])
      basename = os.path.basename(verilog_file)
      expected_tmr_file = basename.replace(".v", "TMR.v")
      assert_output_streams(capfd)
      assert os.path.isfile(expected_tmr_file)
      syntax_check(expected_tmr_file, cmds=["iverilog"])


class TestTmrgOnSingleSystemVerilogFile():
    @pytest.mark.parametrize(
        'verilog_file', [
            "systemverilog/endmodule_label_dff.sv",
            "systemverilog/real_signals.sv",
            "systemverilog/dff_logic.sv",
            "systemverilog/dff_logic_port.sv",
            "systemverilog/dff_always_ff.sv",
            "systemverilog/dff_always_ff01.sv",
            "systemverilog/dff_always_ff02.sv",
            "systemverilog/dff_always_ff03.sv",
            "systemverilog/dff_always_ff04.sv",
            "systemverilog/decoder_using_unique_case.sv",
            "systemverilog/decoder_using_unique_casex.sv",
            "systemverilog/decoder_using_unique_casez.sv",
            "systemverilog/always_comb_01.sv",
            "systemverilog/always_comb_02.sv",
            "systemverilog/always_comb_03.sv",
            "systemverilog/always_comb_04.sv",
            "systemverilog/package_import.sv",
            "systemverilog/always_comb_import.sv",
            #"systemverilog/always_comb_import_unused_function.sv",
            "systemverilog/always_comb_importstar.sv",
            "systemverilog/always_latch_01.sv",
            "systemverilog/always_latch_02.sv",
            "systemverilog/always_latch_03.sv",
            "systemverilog/always_latch_04.sv",
            "systemverilog/for_loops.sv",
            "systemverilog/always_comb_import_for.sv",
            "systemverilog/always_ff_import_for_01.sv",
            "systemverilog/assignment_operators.sv",
            "systemverilog/forloop_generate01.sv",
            "systemverilog/forloop_generate02.sv",
            "systemverilog/rhs_assign.sv",
            "systemverilog/forinalways.sv",
            "systemverilog/forinalwaysff.sv",
            "systemverilog/forinalwayscomb.sv",
            "systemverilog/ifndef.sv",
            "systemverilog/unpacked_array_ranges.sv",
            "systemverilog/unpacked_array_sizes.sv",
            "systemverilog/forloopcast.sv",
            "systemverilog/unpacked_array_ranges_port.sv",
            "systemverilog/unpacked_array_sizes_port.sv",
            "systemverilog/multidimentionalarray_port_ranges.sv",
            "systemverilog/multidimentionalarray_port_sizes.sv",
            "systemverilog/localparam.sv",
            "systemverilog/package_import_width.sv",
            "systemverilog/rhs_trucation.sv",
        ]
    )

    def test_tmrg_on_file(self, tmrg, capfd, verilog_file):
      syntax_check(file_in_test_dir(verilog_file), cmds=["iverilog -g2012","verible-verilog-syntax"])
      assert not tmrg([file_in_test_dir(verilog_file)])
      basename = os.path.basename(verilog_file)
      expected_tmr_file = basename.replace(".sv", "TMR.sv")
      assert_output_streams(capfd)
      assert os.path.isfile(expected_tmr_file)
      syntax_check(expected_tmr_file, cmds=["iverilog -g2012","verible-verilog-syntax"])


class TestTmrgOnSingleSystemVerilogFileOnlyIverilog():
    """This class is to test a SystemVerilog file only using iverilog.
    Verible can be too permissive then testing the output of TMRG, leading to bugs
    splipping throught the CI. If this happens, add the files for this list instead
    of using TestTmrgOnSingleSystemVerilogFile"""
    @pytest.mark.parametrize(
        'verilog_file', [
            #"systemverilog/issue_53.sv",
        ]
    )

    def test_tmrg_on_file(self, tmrg, capfd, verilog_file):
      syntax_check(file_in_test_dir(verilog_file), cmds=["iverilog -g2012"])
      assert not tmrg([file_in_test_dir(verilog_file)])
      basename = os.path.basename(verilog_file)
      expected_tmr_file = basename.replace(".sv", "TMR.sv")
      assert_output_streams(capfd)
      assert os.path.isfile(expected_tmr_file)
      syntax_check(expected_tmr_file, cmds=["iverilog -g2012"])
