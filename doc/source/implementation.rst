Physical implementation
***********************

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

