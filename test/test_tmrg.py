import os
import pytest

@pytest.fixture(autouse=True)
def tmp_run_dir(monkeypatch, tmp_path):
    """Fixture running each test in an isolated, temporary directory"""
    monkeypatch.chdir(tmp_path)

class CliArgPatcher:
    def __init__(self, monkeypatch):
        self._monkeypatch = monkeypatch
        self._args = ["tmrg"]
        self._monkeypatch.setattr("sys.argv", self._args)
    
    def add_args(self, arg_list):
        self._args += arg_list

@pytest.fixture
def cli_args(monkeypatch):
    patcher = CliArgPatcher(monkeypatch)
    yield patcher


def expect_in_stderr(string, capture):
    assert string in str(capture.readouterr())

def expect_not_in_stderr(string, capture):
    assert string not in str(capture.readouterr())

def run_tmrg():
    """Execute tmrg main, verify it exists using sys.exit(), return exit code"""
    from tmrg.tmrg import main as tmrg_main
    with pytest.raises(SystemExit) as retval:
        tmrg_main()
    return retval.value.code

def test_no_arguments(capfd):
    """Generate error message and return code without arguments"""
    assert run_tmrg()
    expect_in_stderr("No modules found. Please refer to the documentation", capfd)

def tewst_missing_file(cli_args, capfd):
    """Generate error message and return code without arguments"""
    cli_args.add_args(["not_existing.v"])
    assert not run_tmrg()
    expect_in_stderr("File or directory does not exists", capfd)


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

    def test_tmrg_on_file(self, cli_args, capfd, verilog_file):
      file_name = os.path.join(os.path.dirname(__file__), verilog_file)
      cli_args.add_args([file_name])
      assert not run_tmrg()


