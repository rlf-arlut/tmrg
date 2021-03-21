import os
import pytest
from .common import *
from tmrg.tmrg import main as tmrg_main
import filecmp

@pytest.fixture
def tmrg(monkeypatch):
    return CliArgPatcher(monkeypatch, "tmrg", main_function=tmrg_main)

import logging
def test_tmrg_configuration(tmrg, capfd):
    errors=0
    test = {
        "name":"First test",
        "verilog":""" module comb( input [7:0]  in, output [7:0] out );
                  assign out=~in;
                  endmodule
                  """,
        "configurations":(
            {"file":"[comb]\ndefault : triplicate",
             "comment":"// tmrg default triplicate",
             "cmd_line_args":['-w', 'default triplicate']},

            {"file":"[comb]\ndefault : do_not_triplicate",
             "comment":"// tmrg default do_not_triplicate",
             "cmd_line_args":['-w', 'default do_not_triplicate comb']},

            {"file":"[comb]\ndefault : do_not_triplicate\nin:triplicate",
             "comment":"// tmrg default do_not_triplicate\n //tmrg triplicate in",
             "cmd_line_args":['-w', 'default do_not_triplicate comb', '-w', 'triplicate comb.in"']},

            {"file":"[comb]\ndefault : triplicate\nout:do_not_triplicate",
             "comment":"// tmrg default triplicate\n //tmrg do_not_triplicate out",
             "cmd_line_args":['-w', 'default triplicate comb', '-w', 'do_not_triplicate comb.out']},

            {"file":"[comb]\ndo_not_touch : true",
             "comment":"// tmrg do_not_touch",
             "cmd_line_args":['-w', 'do_not_touch comb']},
         )}
    verilog_source = test["verilog"]
    for j, conf in enumerate(test["configurations"]):
        coreName="m%03d"%(j)

        verilog_file_name = "%s_file.v"%coreName
        confi_file_name = "%s_file.cnf"%coreName
        with open(verilog_file_name, "w") as verilog_file:
            verilog_file.write(verilog_source+"\n")
        with open(confi_file_name, "w") as config_file:
            config_file.write(test["configurations"][j]["file"]+"\n")
        assert not tmrg(['--no-header', verilog_file_name,'--config=%s' % confi_file_name])
        assert_output_streams(capfd)

        verilog_with_comments_file_name = "%s_comment.v"%coreName
        with open(verilog_with_comments_file_name, "w") as verilog_file:
            verilog_lines = verilog_source.split("\n")
            verilog_file.write(verilog_lines[0]+"\n")
            verilog_file.write(test["configurations"][j]["comment"]+"\n")
            verilog_file.write("\n".join(verilog_lines[1:]))
        assert not tmrg(['--no-header', verilog_with_comments_file_name])
        assert_output_streams(capfd)

        verilog_cmdline_file_name = "%s_cmdline.v"%coreName
        with open(verilog_cmdline_file_name, "w") as verilog_file:
            verilog_file.write(verilog_source+"\n")
        assert not tmrg(['--no-header', verilog_cmdline_file_name] + test["configurations"][j]["cmd_line_args"])
        assert_output_streams(capfd)

        verilog_file_tmr_name = verilog_file_name.replace(".v", "TMR.v")
        verilog_with_comments_file_tmr_name = verilog_with_comments_file_name.replace(".v", "TMR.v")
        verilog_cmdline_file_tmr_name = verilog_cmdline_file_name.replace(".v", "TMR.v")

        assert filecmp.cmp(verilog_file_tmr_name, verilog_with_comments_file_tmr_name)
        assert filecmp.cmp(verilog_file_tmr_name, verilog_cmdline_file_tmr_name)
        assert filecmp.cmp(verilog_with_comments_file_tmr_name, verilog_cmdline_file_tmr_name)
