.. _verification:

Verification
************

Once the design is implemented (you have a verilog netlist) you should verify 
that the design still  does what you want it to do and that the design in immune to SEE. 
The TMRG toolset contains SEEG (Single Event Effect Generator) tool which can
assist you in that process.
The SEEG generates a verilog file, which contains several useful verilog tasks,
which can toggle nets (to simulate SET) or toggle flip-flip flops (to simmulate
SEU).

The SEEG tool operate on a final netlist. An example usage of the tool for the
netlist generated for an example ``fsm02`` can look like:

.. code-block:: bash

   seeg --lib libs/tcbn65lp.v --output fsm02TMR_see.v fsm02_r2g.v

As a result a verilog file ``see.v`` is generated. In the considered example a file will
look like:

.. code-block:: verilog

   // - Single Event Transient - - - - - - - - - - - - - - - - - - - - - - - - - -
   task set_force_net;
     input wireid;
     integer wireid;
     begin
       case (wireid)
          0 : force DUT.stateA_reg.Q = ~DUT.stateA_reg.Q;
          1 : force DUT.stateC_reg.Q = ~DUT.stateC_reg.Q;
          2 : force DUT.stateNextVoterA.Fp9999957A.ZN = ~DUT.stateNextVoterA.Fp9999957A.ZN;
          3 : force DUT.stateNextVoterA.p214748365A.ZN = ~DUT.stateNextVoterA.p214748365A.ZN;
          4 : force DUT.stateNextVoterC.Fp9999957A.ZN = ~DUT.stateNextVoterC.Fp9999957A.ZN;
          5 : force DUT.stateNextVoterC.p214748365A.ZN = ~DUT.stateNextVoterC.p214748365A.ZN;
          6 : force DUT.stateNextVoterB.Fp9999957A.ZN = ~DUT.stateNextVoterB.Fp9999957A.ZN;
          7 : force DUT.stateNextVoterB.p214748365A.ZN = ~DUT.stateNextVoterB.p214748365A.ZN;
          8 : force DUT.stateB_reg.Q = ~DUT.stateB_reg.Q;
          9 : force DUT.p214748365A22.Z = ~DUT.p214748365A22.Z;
         10 : force DUT.p214748365A20.Z = ~DUT.p214748365A20.Z;
         11 : force DUT.p214748365A21.Z = ~DUT.p214748365A21.Z;
       endcase
     end
   endtask
   
   task set_release_net;
     input wireid;
     integer wireid;
     begin
       case (wireid)
          0 : release DUT.stateA_reg.Q;
          1 : release DUT.stateC_reg.Q;
          2 : release DUT.stateNextVoterA.Fp9999957A.ZN;
          3 : release DUT.stateNextVoterA.p214748365A.ZN;
          4 : release DUT.stateNextVoterC.Fp9999957A.ZN;
          5 : release DUT.stateNextVoterC.p214748365A.ZN;
          6 : release DUT.stateNextVoterB.Fp9999957A.ZN;
          7 : release DUT.stateNextVoterB.p214748365A.ZN;
          8 : release DUT.stateB_reg.Q;
          9 : release DUT.p214748365A22.Z;
         10 : release DUT.p214748365A20.Z;
         11 : release DUT.p214748365A21.Z;
       endcase
     end
   endtask
   
   task set_display_net;
     input wireid;
     integer wireid;
     begin
       case (wireid)
         0 : $display("DUT.stateA_reg.Q");
         1 : $display("DUT.stateC_reg.Q");
         2 : $display("DUT.stateNextVoterA.Fp9999957A.ZN");
         3 : $display("DUT.stateNextVoterA.p214748365A.ZN");
         4 : $display("DUT.stateNextVoterC.Fp9999957A.ZN");
         5 : $display("DUT.stateNextVoterC.p214748365A.ZN");
         6 : $display("DUT.stateNextVoterB.Fp9999957A.ZN");
         7 : $display("DUT.stateNextVoterB.p214748365A.ZN");
         8 : $display("DUT.stateB_reg.Q");
         9 : $display("DUT.p214748365A22.Z");
        10 : $display("DUT.p214748365A20.Z");
        11 : $display("DUT.p214748365A21.Z");
       endcase
     end
   endtask
   
   task set_max_net;
     output wireid;
     integer wireid;
     begin
       wireid=12;
     end
   endtask
   
   // - Single Event Upset - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   
   task seu_force_net;
     input wireid;
     integer wireid;
     begin
       case (wireid)
          0 : force DUT.stateA_reg.SDN = ~DUT.stateA_reg.SDN;
          1 : force DUT.stateA_reg.CDN = ~DUT.stateA_reg.CDN;
          2 : force DUT.stateC_reg.SDN = ~DUT.stateC_reg.SDN;
          3 : force DUT.stateC_reg.CDN = ~DUT.stateC_reg.CDN;
          4 : force DUT.stateB_reg.SDN = ~DUT.stateB_reg.SDN;
          5 : force DUT.stateB_reg.CDN = ~DUT.stateB_reg.CDN;
       endcase
     end
   endtask
   
   task seu_release_net;
     input wireid;
     integer wireid;
     begin
       case (wireid)
          0 : release DUT.stateA_reg.SDN;
          1 : release DUT.stateA_reg.CDN;
          2 : release DUT.stateC_reg.SDN;
          3 : release DUT.stateC_reg.CDN;
          4 : release DUT.stateB_reg.SDN;
          5 : release DUT.stateB_reg.CDN;
       endcase
     end
   endtask
   
   task seu_display_net;
     input wireid;
     integer wireid;
     begin
       case (wireid)
         0 : $display("DUT.stateA_reg.SDN");
         1 : $display("DUT.stateA_reg.CDN");
         2 : $display("DUT.stateC_reg.SDN");
         3 : $display("DUT.stateC_reg.CDN");
         4 : $display("DUT.stateB_reg.SDN");
         5 : $display("DUT.stateB_reg.CDN");
       endcase
     end
   endtask
   
   task seu_max_net;
     output wireid;
     integer wireid;
     begin
       wireid=6;
     end
   endtask
   
   // - Single Event Efect - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   
   task see_force_net;
     input wireid;
     integer wireid;
     begin
       if (wireid<12)
         set_force_net(wireid);
       else
         seu_force_net(wireid-12);
     end
   endtask
   
   task see_release_net;
     input wireid;
     integer wireid;
     begin
       if (wireid<12)
         set_release_net(wireid);
       else
         seu_release_net(wireid-12);
     end
   endtask
   
   task see_display_net;
     input wireid;
     integer wireid;
     begin
       if (wireid<12)
         set_display_net(wireid);
       else
         seu_display_net(wireid-12);
     end
   endtask
   
   task see_max_net;
     output wireid;
     integer wireid;
     begin
       wireid=(12 + 6);
     end
   endtask
   
Having these tasks in place, the developer can easily generate SET, SEU, or SEE
upsets in his design. The simpliest implementation may look like:

.. code-block:: verilog

  module stimulus;

    fsm02TMR DUT(...);
   
    [...]

    integer SEEnextTime;
    integer SEEduration;
    integer SEEwireId;
    integer SEEmaxWireId;
    integer MAX_UPSET_TIME=10;
    integer SEEDEL=100;
    inreger SEEEnable=1;

    initial
      see_max_net (SEEmaxWireId);
  
    `include "fsm02TMR_see.v"

    always 
      begin
        if (SEEEnable)
          begin
            // randomize time, duration, and wire of SEE
            SEEnextTime = {$random} % SEEDEL;
            SEEduration = {$random} % MAX_UPSET_TIME + 1;
            SEEwireId   = {$random} % SEEmaxWireId;
  
            // wait for SEU
            #(SEEDEL/2+SEEnextTime);
  
            // toggle wire
            seeCounter=seeCounter+1;
            see_force_net(SEEwireId);
            see_display_net(SEEwireId);
            #(SEEduration);
            see_release_net(SEEwireId);
          end
      end
   endmodule  
  
  
  
