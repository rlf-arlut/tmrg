Verification
************

Once the design is implemented (you have a verilog netlist) you should verify 
that the design still  does what you want it to do and that the design in immune to SEU. 
The TMRG tool set can generate a verilog file which will simplify that task.
The file contains several useful verilog tasks, which can toggle nets (to simulate SET) or toggle flip-flip flops (to simmulate SEU).

.. code-block:: verilog

  task seu_max_net;
    output wireid;
    integer wireid;
    begin
      wireid=7493;
    end
  endtask
  
  task seu_force_net;
    input wireid;
    integer wireid;
    begin
    case (wireid)
        1 : force DUT.GBLDDIGITALTMR.I2C.I2CC.iVoterA.out[0] = ~DUT.GBLDDIGITALTMR.I2C.I2CC.iVoterA.out[0]; 
        2 : force DUT.GBLDDIGITALTMR.MB.MC2.memVoterA.inC[4] = ~DUT.GBLDDIGITALTMR.MB.MC2.memVoterA.inC[4]; 
        3 : force DUT.GBLDDIGITALTMR.I2C.I2CC.SCLin_lateVoterB.inB[0] = ~DUT.GBLDDIGITALTMR.I2C.I2CC.SCLin_lateVoterB.inB[0]; 
        4 : force DUT.GBLDDIGITALTMR.porVoterC.tmrErr = ~DUT.GBLDDIGITALTMR.porVoterC.tmrErr; 
        5 : force DUT.GBLDDIGITALTMR.MB.MC1.memVoterA.inA[6] = ~DUT.GBLDDIGITALTMR.MB.MC1.memVoterA.inA[6]; 
        6 : force DUT.GBLDDIGITALTMR.MB.MEC.n_12 = ~DUT.GBLDDIGITALTMR.MB.MEC.n_12; 
        7 : force DUT.GBLDDIGITALTMR.MB.MC2.dataInB[3] = ~DUT.GBLDDIGITALTMR.MB.MC2.dataInB[3]; 
        8 : force DUT.GBLDDIGITALTMR.I2C.I2CC.wbAdrC[2] = ~DUT.GBLDDIGITALTMR.I2C.I2CC.wbAdrC[2]; 
        9 : force DUT.GBLDDIGITALTMR.ADC.address[0] = ~DUT.GBLDDIGITALTMR.ADC.address[0]; 
        ...
    endcase
  end
  endtask
  
  task seu_release_net;
    input wireid;
    integer wireid;
    begin
    case (wireid)
        1 : release DUT.GBLDDIGITALTMR.I2C.I2CC.iVoterA.out[0]; 
        2 : release DUT.GBLDDIGITALTMR.MB.MC2.memVoterA.inC[4]; 
        3 : release DUT.GBLDDIGITALTMR.I2C.I2CC.SCLin_lateVoterB.inB[0]; 
        4 : release DUT.GBLDDIGITALTMR.porVoterC.tmrErr; 
        5 : release DUT.GBLDDIGITALTMR.MB.MC1.memVoterA.inA[6]; 
        6 : release DUT.GBLDDIGITALTMR.MB.MEC.n_12; 
        7 : release DUT.GBLDDIGITALTMR.MB.MC2.dataInB[3]; 
        8 : release DUT.GBLDDIGITALTMR.I2C.I2CC.wbAdrC[2]; 
        9 : release DUT.GBLDDIGITALTMR.ADC.address[0]; 
        ...
    endcase
  end
  endtask
  
  task seu_display_net;
    input wireid;
    integer wireid;
    begin
    case (wireid)
        1 : $display("DUT.GBLDDIGITALTMR.I2C.I2CC.iVoterA.out[0]"); 
        2 : $display("DUT.GBLDDIGITALTMR.MB.MC2.memVoterA.inC[4]"); 
        3 : $display("DUT.GBLDDIGITALTMR.I2C.I2CC.SCLin_lateVoterB.inB[0]"); 
        4 : $display("DUT.GBLDDIGITALTMR.porVoterC.tmrErr"); 
        5 : $display("DUT.GBLDDIGITALTMR.MB.MC1.memVoterA.inA[6]"); 
        6 : $display("DUT.GBLDDIGITALTMR.MB.MEC.n_12"); 
        7 : $display("DUT.GBLDDIGITALTMR.MB.MC2.dataInB[3]"); 
        8 : $display("DUT.GBLDDIGITALTMR.I2C.I2CC.wbAdrC[2]"); 
        9 : $display("DUT.GBLDDIGITALTMR.ADC.address[0]"); 
    endcase
  end
  endtask
  
Having this tasks in place, the developer can easily generate upsets in his
design. The easies implementation may look like:

.. code-block:: verilog

  always 
    begin
      if (SEUEnable)
        begin
          // randomize time, duration, and wire
          SEUnextTime = {$random} % SEUDEL;
          SEUduration = 1+ {$random} % MAX_UPSET_TIME;
          SEUwireId   =  {$random} % SEUmaxWireId;

          // wait for SEU
          #(SEUDEL/2+SEUnextTime);

          // toggle wire
          seu=1;
          seuCounter=seuCounter+1;
          seu_force_net(SEUwireId);
          #(SEUduration);
          seu_release_net(SEUwireId);
          seu=0;
        end
    end


