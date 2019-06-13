#!/usr/bin/env python3

from .tmrg import VerilogFormater,readFile,resultLine,TMR
from .verilogElaborator import *
from .toolset import *
import logging
import traceback
import pprint
import os
import glob
import logging
import random
import re
from optparse import *

class TBG(TMR):
    def __init__(self,options, args):
        TMR.__init__(self,options, args)

    def loadVoterDefinition(self,voterName="majorityVoterTB"):
            vfile=os.path.join( self.scriptDir,  self.config.get("tmrg","voter_definition"))
            self.logger.info("Taking voter declaration from %s"%vfile)
            return readFile(vfile).replace("majorityVoter",voterName)

    def generate(self):
        logging.debug("")
        oStr="`timescale 1 ps / 1 ps\n"
        voterCell="majorityVoterTB"
        oStr+=self.loadVoterDefinition(voterCell)+"\n"
        for module in self.modules:
            clocks=[]
            resets=[]
            oStr+="module %s_test;\n"%module

            oStr+="\n// - - - - - - - - - - - - - - Parameters section  - - - - - - - - - - - - - - \n"

            parameters=""
            psep="\n    "
            for k in self.modules[module]["params"]:
                if self.modules[module]["params"][k]['type'] == 'localparam':continue
                oStr+="  parameter %s = %s;\n"%(k,self.modules[module]["params"][k]["value"])
                parameters+="%s.%s(%s)"%(psep,k,k)
                psep=",\n    "

            if len(parameters): parameters="\n`ifndef NETLIST\n  #("+parameters+"\n  )\n`endif\n "

            oStr+="\n// - - - - - - - - - - - - - - Input/Output section  - - - - - - - - - - - - - \n"
            #initial declaration
            for ioName in sorted(self.modules[module]["io"]):
                io=self.modules[module]["io"][ioName]
                if io["type"]=="input":
                    oStr+="  reg %s %s;\n"%(io["range"], ioName)
                    if ioName.lower().find("clk")>=0 or ioName.lower().find("clock")>=0:
                        clocks.append(ioName)
                    if ioName.lower().find("rst")>=0 or ioName.lower().find("reset")>=0:
                        resets.append(ioName)
                elif io["type"]=="output":
                    oStr+="  wire %s %s;\n"%(io["range"], ioName)
                else:
                    self.logger.warning("Unsuported IO type: %s"%io["type"])

            oStr+="\n// - - - - - - - - - - - - - Device Under Test section - - - - - - - - - - - -\n"
            oStr+="\n`ifdef TMR\n"
            #initial declaration
            for ioName in sorted(self.modules[module]["io"]):
                if self.modules[module]["nets"][ioName]["tmr"]:
                    io=self.modules[module]["io"][ioName]
                    if io["type"]=="input":
                        oStr+="  // fanout for %s\n"%(ioName)
                        for ext in self.EXT:
                            oStr+="  wire %s %s%s=%s;\n"%(io["range"], ioName,ext,ioName)
                    elif io["type"]=="output":
                        oStr+="  // voter for %s\n"%(ioName)
                        for ext in self.EXT:
                            oStr+="  wire %s %s%s;\n"%(io["range"], ioName,ext)
#                        oStr+="  assign %s = (%sA & %sB) | (%sB & %sC) | (%sA & %sC);\n"%(ioName,ioName,ioName,ioName,ioName,ioName,ioName)
                        oStr+="  wire %stmrErr;\n"%(ioName)

                        _len=self.modules[module]["nets"][ioName]["len"]
                        width=""
                        if _len!="1":
                            width+="#(.WIDTH(%s)) "%_len

                        oStr+="  %s %s%s (\n"%(voterCell,width,ioName+"Voter")
                        oStr+="    .inA(%sA),\n"%(ioName)
                        oStr+="    .inB(%sB),\n"%(ioName)
                        oStr+="    .inC(%sC),\n"%(ioName)
                        oStr+="    .out(%s),\n"%(ioName)
                        oStr+="    .tmrErr(%stmrErr)\n"%(ioName)
                        oStr+="  );\n"

                    else:
                        self.logger.warning("Unsuported IO type: %s"%io["type"])


            #dut tmr instantiation
            oStr+="  %sTMR%s DUT (\n"%(module,parameters)
            sep="    "
            #initial declaration
            for ioName in sorted(self.modules[module]["io"]):
                if self.modules[module]["nets"][ioName]["tmr"]:
                    for ext in self.EXT:
                        oStr+="%s.%s%s(%s%s)"%(sep,ioName,ext, ioName,ext)
                        sep=",\n    "
                else:
                        oStr+="%s.%s(%s)"%(sep,ioName, ioName)
                        sep=",\n    "
            oStr+="\n  );\n"
            oStr+="`else\n"
            #dut instantiation
            oStr+="  %s%s DUT (\n"%(module,parameters)
            sep="    "
            #initial declaration
            for ioName in sorted(self.modules[module]["io"]):
                oStr+="%s.%s(%s)"%(sep,ioName, ioName)
                sep=",\n    "
            oStr+="\n  );\n"
            oStr+="`endif\n"


            oStr+="\n// - - - - - - - - - - - - Timing annotation section - - - - - - - - - - - - - \n"
            oStr+="""`ifdef SDF
  initial
    $sdf_annotate("r2g.sdf", DUT, ,"sdf.log");
`endif
"""

            oStr+="\n// - - - - - - - - - - - - Single Event Effect section - - - - - - - - - - - -\n"
            oStr+="""`ifdef SEE

  reg     SEEEnable=0;          // enables SEE generator
  reg     SEEActive=0;          // high during any SEE event
  integer SEEnextTime=0;        // time until the next SEE event
  integer SEEduration=0;        // duration of the next SEE event
  integer SEEwireId=0;          // wire to be affected by the next SEE event
  integer SEEmaxWireId=0;       // number of wires in the design which can be affected by SEE event
  integer SEEmaxUpaseTime=1000; // 1 ns  (change if you are using different timescale)
  integer SEEDel=100_000;       // 100 ns (change if you are using different timescale)
  integer SEECounter=0;         // number of simulated SEE events

  `include "see.v"

  // get number of wires which can be affected by see
  initial
    see_max_net (SEEmaxWireId);


  always
    begin
      if (SEEEnable)
        begin
          // randomize time, duration, and wire of the next SEE
          SEEnextTime = #(SEEDel/2) {$random} % SEEDel;
          SEEduration = {$random} % (SEEmaxUpaseTime-1) + 1;  // SEE time is from 1 - MAX_UPSET_TIME ns
          SEEwireId   = {$random} % SEEmaxWireId;

          // wait for SEE
          #(SEEnextTime);

          // SEE happens here! Toggle the selected wire.
          SEECounter=SEECounter+1;
          SEEActive=1;
          see_force_net(SEEwireId);
          see_display_net(SEEwireId); // probably you want to comment this line ?
          #(SEEduration);
          see_release_net(SEEwireId);
          SEEActive=0;
        end
      else
        #10;
    end

`endif
"""

            #initial
            oStr+="\n// - - - - - - - - - - - - - Actual testbench section  - - - - - - - - - - - -\n"
            oStr+="  initial\n"
            oStr+="    begin\n"
            resetsRelease=""
            for ioName in sorted(self.modules[module]["io"]):
                io=self.modules[module]["io"][ioName]
                if io["type"]=="input":
                    if ioName in resets:
                        if ioName.find("n")>=0 or ioName.find("b")>=0:
                            oStr+="      %s=0;\n"%(ioName)
                            resetsRelease="      %s=1;\n"%(ioName)
                        else:
                            oStr+="      %s=1;\n"%(ioName)
                            resetsRelease="      %s=0;\n"%(ioName)
                    else:
                        oStr+="      %s=0;\n"%(ioName)
            if len(resetsRelease):
                oStr+="      #10_000\n"+resetsRelease
            oStr+="`ifdef SEE\n"
            oStr+="      // enable SEE after 1ms\n"
            oStr+="      #1000_000 SEEEnable=1;\n"
            oStr+="      $display(\"Enabling SEE generation\");\n"
            oStr+="`endif\n"
            oStr+="      // finish simulation after 1ms\n"
            oStr+="      #1000_000 $finish;\n"
            oStr+="    end\n"

            oStr+="\n"
            for clock in clocks:
                def guessClkFreq(clkName):
                    try:
                        return int(1e6/float(re.search(r'\d+', clock).group()))
                    except:
                        return 1e5
                oStr+="  localparam %s_PERIOD = %d;\n"%(clock.upper(),guessClkFreq(clock))
                oStr+="  initial\n"
                oStr+="    begin\n"
                oStr+="      #1000;\n"
                oStr+="      forever\n"
                oStr+="        begin\n"
                oStr+="          %s = !%s;\n"%(clock,clock)
                oStr+="          #(%s_PERIOD/2);\n"%(clock.upper())
                oStr+="        end\n"
                oStr+="    end\n"

            oStr+="endmodule\n"
        if self.options.outputFname!="":
            self.logger.info("Writing testbench to %s"%self.options.outputFname)
            f=open(self.options.outputFname,"w")
            f.write(oStr)
            f.close()
        else:
            print(oStr)

        #generateFromTemplate(fname,tfile, values)


def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="TBG %s"%tmrg_version(), usage="%prog [options] fileName", epilog=epilog)
    parser.add_option("-v", "--verbose",       dest="verbose",   action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("",   "--doc",           dest="doc",       action="store_true",   default=False, help="Open documentation in web browser")
    parser.add_option("-l", "--lib",           dest="libs",      action="append",   default=[], help="Library")
    parser.add_option("-c",  "--config",           dest="config",       action="append",   default=[], help="Load config file")
    parser.add_option("-w",  "--constrain",        dest="constrain",    action="append",   default=[], help="Load config file")
    parser.add_option("-o",  "--output-file",      dest="outputFname",    default="", help="Output file name")
    parser.add_option("",  "--generate-report",    dest="generateBugReport", action="store_true",   default=False, help="Generate bug report")
    parser.add_option("", "--stats", dest="stats", action="store_true", help="Print statistics")
    parser.add_option("", "--include", dest="include", action="store_true", default="false",
                      help="Include include files")
    parser.add_option("",   "--inc-dir",           dest="inc_dir",      action="append", default=[], help="Include directories")

    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()

        if options.verbose==0:
            logging.getLogger().setLevel(logging.WARNING)
        if options.verbose==1:
            logging.getLogger().setLevel(logging.INFO)
        elif options.verbose==2:
            logging.getLogger().setLevel(logging.DEBUG)

        if options.doc:
            startDocumentation()
            return

        if len(args)!=1:
            raise OptParseError("You have to specify verilog file name. ")

        tbg=TBG(options, args)
        tbg.parse()
        tbg.elaborate(allowMissingModules=True)
        tbg.generate()
    except ErrorMessage as er:
        logging.error(er)
        os._exit(1)
    except OptParseError as er:
        logging.error(er)
        os._exit(2)

if __name__=="__main__":
    main()
