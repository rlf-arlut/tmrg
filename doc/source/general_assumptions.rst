General Assumptions
*******************

.. warning:: Before you start reading further, you should understand the purpose of the tool. 
   The TMRG tool **is not** a single button solution which will make you CHIP / FPGA design SEU proof.
   You, as a designer, have to know which parts of your circuits should (have to) be protected. 
   The TMRG tool will save you some time needed for copy-pasting your code and will minimize probability that you will forget to change some postfix in your triplicated variable names. 
   It will also simplify verification process by providing some routines. 



Specification
-------------

  1) tool should be able to transform the whole project (e.g. macro cell like i2cSlave) (Not single modules only). 
     The input project files should be normal verilog which can be simulated and synthesized.
  2) triplication should be done on RTL level
  3) tool should generate one output module for each input module. This requirement has some consequences: imagine that you have a module, like a simple added, which you are using in various places across your design. If you want to obtain various levels of protection in various places (e.g. full triplication in FSM, no protection on a data path) you have to create two identical modules (with different names) in the source project.
  4) triplication should be possible only for given signals/instances (while leaving others not touched)
      - specification of these should be done via pragmas in the source code or in the configuration file (similarly to RTL compiler)
      - "conversion" between triplicated and non triplicated signals should be handled automatically by means of fanout and voters
      - it should be possible to add voter anywhere (also on combinatorial signals)
      - designer should be able to access individual signals of the triplicated net (power on reset, clock gating)
  4) error output from majority voters should be available for the designer. This output can be used for a clock gating, error counting, or others.

..  4) (too some extend) understand the circuit (detect whether logic is combinatorial or sequential)
..      - the goal is not to write synthesizer which understand all possible cases
..      - simple approach: use blocking assignments for combinatorial logic and non blocking assignments for sequential logic
..      - defining common coding standard for FSM is not strictly necessary, but function to recognize and transform each type of coding has to be added and tested. 

Using this approach is more power full that triplicating the output netlist. 
It is much easier to guide the tool which wires/instances should be triplicated and which should be not. More over this approach allows to access to error output and to modify the circuit operation accordingly (which is very difficult at the nestlist level). 

.. FSM implementation
.. ^^^^^^^^^^^^^^^^^^

.. As it has been disused in section :ref:`sec-fsm-triplication`, triplication at
.. the output and triplication at the output of the register is possible. 
.. To keep implementation similar for FSM and data path, the triplication at 
.. the register input is chosen. 

.. Recommendation for FSM coding style:

.. .. code-block:: verilog
.. 
..    module fsm(in1, in2, out1, clk, rst);
..      input in1,in2,clk,rst;
..      output out1;
..      reg out1,out1next;
..      
..      always 
..        if (in1)
..          out1next= ~in2;
..        else
..          out1next=in1 ^ out1;
..      
..      always @(posedge clk or posedge rst)
..      begin
..        if (rst)
..          out1<=1'b0;
..        else
..          out1<= out1next;
..      end
..    endmodule

.. Other remarks
.. ^^^^^^^^^^^^^

..   1) keep verilog code clean and simple. e.g. DO NOT introduce unnecessary temporary variables, like::

..        module moduleOut(in1, in2, out1);
..          input in1,in2;
..          output out1;
..          reg out1,out1next;
..          wire tmp;
..          assign tmp=in1;
..          moduleIn instIn( .in1(tmp), .in2(in2), .out1(out));
..        endmodule
   
..      Tool will not crash because of that, however propagation of properties (like do not triplicate) may not work properly (as stated above, the goal of the project is not writing full blown synthesizer). 
   
Proposed approach
-----------------
The process of triplicating verilog code can be divided in following steps:
  1) parsing input files
       **input:** verilog code

       **output:** list of tokens
  2) analysis of the tokens (within the proper context)
       **input:** tokens

       **output:** list of module inputs, outputs, registers, instances, always blocks, ...
  3) application of constrains from the verilog code and configuration file (like do_not_triplicate directive)
  4) triplication
       **input:** tokens

       **output:** tokens
  5) generation verilog code
       **input:** tokens

       **output:** verilog code

Advantages of proposed approach
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  1) at the each processing step we have information about the context of the expression. 

     For example, expression ``input [7:0] bus;`` can be used in module declaration as well as in the task header. In the second case, it should not be triplicated.
  2) indication of invalid/confusing syntax which may lead to undesired results
  3) not sensitive to variable names, any name convention can be applied without risk of misunderstanding the design

.. How triplication is implemented
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. For each functional block we have a callback. 
.. The naive implementation of triplication may look like:

.. .. code-block:: verilog

..    def tmrModule(tokens):         <- tokens from the source code
..      return tokens+tokens+tokens  <- tokens for output code

Side benefits
^^^^^^^^^^^^^

By implementing this strategy, one can (relatively easy) get two other tools:
  1) executing steps 1) and 5) one can obtain "formatter" of the verilog code (uniformity of the code across the project). See :ref:`exaple_verilog_formatting`.
  2) easy to generate HTML documentation (with clickable references to modules and variables). 


Coding
------

Non triplicated module
^^^^^^^^^^^^^^^^^^^^^^

Let us consider simple combinatorial module **comb01**:

.. code-block:: verilog

  module comb01 (in1,in2,out1,out2);
    input in1,in2;
    output out1,out2;
    assign out1 = in1&in2;
    reg out2;
    always @(in1 or in2)
      out2 = in1 | in2;
  endmodule






comb02 - full triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: comb02.png
   :align: center

.. code-block:: verilog

  module comb02 (in1,in2,out1,out2);
    // trmg default triplicate
    input in1,in2;
    output out1,out2;
    assign out1 = in1&in2;
    reg out2;
    always @(in1 or in2)
      out2 = in1 | in2;
  endmodule

.. code-block:: verilog

  module comb02TMR(
    in1A, in1B, in1C,
    in2A, in2B, in2C,
    out1A, out1B, out1C,
    out2A, out2B, out2C
  );
  input in1A;
  input in1B;
  input in1C;
  input in2A;
  input in2B;
  input in2C;
  output out1A;
  output out1B;
  output out1C;
  output out2A;
  output out2B;
  output out2C;
  assign out1A =  in1A&in2A;
  assign out1B =  in1B&in2B;
  assign out1C =  in1C&in2C;
  reg out2A;
  reg out2B;
  reg out2C;

  always @(in1A or in2A)
    out2A =  in1A|in2A;

  always @(in1B or in2B)
    out2B =  in1B|in2B;

  always @(in1C or in2C)
    out2C =  in1C|in2C;
  endmodule


comb03 - logic and output triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. image:: comb03.png
   :align: center



.. code-block:: verilog

  module comb03 (in1,in2,out1,out2);
    // trmg default triplicate
    // trmg do_not_triplicate in1
    // trmg do_not_triplicate in2
    input in1,in2;
    output out1,out2;
    assign out1 = in1&in2;
    reg out2;
    always @(in1 or in2)
      out2 = in1 | in2;
  endmodule

.. code-block:: verilog

  module comb02TMR(
    in1,
    in2,
    out1A, out1B, out1C,
    out2A, out2B, out2C
  );
  input in1;
  input in2;
  output out1A;
  output out1B;
  output out1C;
  output out2A;
  output out2B;
  output out2C;
  assign out1A =  in1&in2;
  assign out1B =  in1&in2;
  assign out1C =  in1&in2;
  reg out2A;
  reg out2B;
  reg out2C;

  always @(in1 or in2)
    out2A =  in1|in2;

  always @(in1 or in2)
    out2B =  in1|in2;

  always @(in1 or in2)
    out2C =  in1|in2;
  endmodule


comb04 - input and logic triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: comb04.png
   :align: center


.. code-block:: verilog

  module comb04 (in1,in2,out1,out2);
    // trmg default triplicate
    // trmg do_not_triplicate out1
    // trmg do_not_triplicate out2
    input in1,in2;
    output out1,out2;

    wire out1t;
    reg out2t;

    assign out1 = in1&in2;
    always @(in1 or in2)
      out2 = in1 | in2;

    assign out1=out1t;
    assign out2=out2t;
  endmodule

.. code-block:: verilog

  module comb04TMR(
    in1A, in1B, in1C,
    in2A, in2B, in2C,
    out1,
    out2
  );
  input in1A;
  input in1B;
  input in1C;
  input in2A;
  input in2B;
  input in2C;
  output out1;
  output out2;

  wire out1tA;
  wire out1tB;
  wire out1tC;

  reg out2tA;
  reg out2tB;
  reg out2tC;

  assign out1tA =  in1A&in2A;
  assign out1tB =  in1B&in2B;
  assign out1tC =  in1C&in2C;

  always @(in1A or in2A)
    out2tA =  in1A|in2A;

  always @(in1B or in2B)
    out2B =  in1B|in2B;

  always @(in1C or in2C)
    out2C =  in1C|in2C;

  majorityVoter out1Voter (.A(out1tA),.B(out1tB),.C(out1tC), .Z(out1));
  majorityVoter out2Voter (.A(out2tA),.B(out2tB),.C(out2tC), .Z(out2));
  endmodule

comb05- others
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: comb05.png
   :align: center


Verification
------------

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

Physical implementation
-----------------------
To ensure that triplication effort makes sens, one has to ensure that
the triplicated instances of the same element are not placed to close to each other.
Such a physical proximity may lead to situation, where one particle traversing the ASIC is
able to deposit energy along several logic cells at the same time causing multiple bit SEU. Such an error can not be detected and then leads to malfunctioning of the design. 

In the real design, there are majority voters before(or after) flip-flops. 
From the P&R optimization point of view, in order to keep routing short, the triplicated flip-flops should be placed relatively close together. 

If designer creates several specific regions where to put various groups of flip-flops:

.. code-block:: tcl

  createInstGroup tmrGroupA -region 0 0 10 10
  createInstGroup tmrGroupB -region 10 0 20 10
  createInstGroup tmrGroupB -region 20 0 30 10

the TMRG tool can generate a file which will assign flip-flops to proper groups:

.. code-block:: tcl

  addInstToInstGroup tmrGroupA {GBLDDIGITALTMR/MB/MC1/memA_reg[0]}
  addInstToInstGroup tmrGroupB {GBLDDIGITALTMR/MB/MC1/memB_reg[0]}
  addInstToInstGroup tmrGroupC {GBLDDIGITALTMR/MB/MC1/memC_reg[0]}

  addInstToInstGroup tmrGroupA {GBLDDIGITALTMR/MB/MC1/memA_reg[1]}
  addInstToInstGroup tmrGroupB {GBLDDIGITALTMR/MB/MC1/memB_reg[1]}
  addInstToInstGroup tmrGroupC {GBLDDIGITALTMR/MB/MC1/memC_reg[1]}

Moreover, the tool is capable of calculating distances between triplicated flip-flops and making histogram of these.

