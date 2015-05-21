Constrainig the design
**********************

Terminology:
   * SEU - Single Event Upset - change of the value of a memory element (flip-flop)
   * SET - Single Event Transient - temporary (~up to few ns) change of the value of a net 




Triplication
############



Some rules:
  * if non triplicated signal is connected to a triplicated signal a fanout is added
  * if triplicated signal is connected to a non triplicated signal a voter is added


+-----------------------------+----------------------------+----------------------------+
| Signal source / Signal sink | non triplicated            | triplicated                |
+=============================+============================+============================+
| **non triplicated**         | 1 wire connection          | fanout                     |
+-----------------------------+                            +                            +
| **triplicated**             | majority voter             | 3 wires connection         |
+-----------------------------+----------------------------+----------------------------+




Non triplicated module
^^^^^^^^^^^^^^^^^^^^^^

Let us consider simple combinatorial module **comb01**:

.. literalinclude:: ../../examples/comb01.v
   :language: verilog
   :linenos:


comb02 - full triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: comb02.png
   :align: center

.. literalinclude:: ../../examples/comb02.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/comb02TMR.v
   :language: verilog
   :linenos:


.. include:: ../../examples/comb02.rst


comb03 - logic and output triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Chip input signals.
Signals coming from non triplicated analog blocks.

.. image:: comb03.png
   :align: center


.. literalinclude:: ../../examples/comb03.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/comb03TMR.v
   :language: verilog
   :linenos:


.. include:: ../../examples/comb03.rst


comb04 - input and logic triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Chip output signals.
Signals going to non triplicated analog blocks.


.. image:: comb04.png
   :align: center


.. literalinclude:: ../../examples/comb04.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/comb04TMR.v
   :language: verilog
   :linenos:


.. include:: ../../examples/comb04.rst

comb05- logic triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: comb05.png
   :align: center


.. literalinclude:: ../../examples/comb05.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/comb05TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/comb05.rst

comb06- input and output triplication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: comb06.png
   :align: center


.. literalinclude:: ../../examples/comb06.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/comb06TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/comb06.rst


Voting
######

Triplication by itself is not enough to ensure SEU robustness, especially when memory elements (flip-flops) are used.
Add more explanation ...

You can see that for TMR modules additional output, tmrError, is added. It goes high whenever there is a mismatch between input signals. 
Several examples how this feature can be used will be shown later.

vote01
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: vote01.png
   :align: center

.. literalinclude:: ../../examples/vote01.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/vote01TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/vote01.rst


vote02
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. image:: vote02.png
   :align: center

.. literalinclude:: ../../examples/vote02.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/vote02TMR.v
   :language: verilog
   :linenos:


.. include:: ../../examples/vote02.rst

Finite state machine
####################

Understanding how triplication and voting can be done, lets try to protect a state machine.

fsm01 - triplication without voting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Simple case. Everything is triplicated but the errors are not fixed.


.. image:: fsm01.png
   :align: center

.. literalinclude:: ../../examples/fsm01.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/fsm01TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/fsm01.rst


fsm02 - triplication and voting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All elements are protected. 
This type of configuration gives maximum protection.

.. image:: fsm02.png
   :align: center

.. literalinclude:: ../../examples/fsm02.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/fsm02TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/fsm02.rst

fsm03 - triplicating only register
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Only memory elements are protected. 
Single event transient appearing in the voting element of combinatorial block close to the clock edge can break the system (all memory cells are corrupted at the same time).

.. image:: fsm03.png
   :align: center

.. literalinclude:: ../../examples/fsm03.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/fsm03TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/fsm03.rst

Module instantiations
#####################

Until now, we were considering only single modules. In real designs we have 
hierarchy of many modules. Lets try to understand how triplication works in that case.

Only named connections are supported!

All modules must be known at the time of triplication. 
In case of elements from library, one has to load the library (which may not
be that ease) or provide a simple file in which definitions of modules and their
inputs/outputs are provided. In that case, one has to add directive 
''tmrg do_not_touch'' in the module body.

For all other modules (not from library and not having ''do_not_touch'' constrain) 
triplication is always done inside the module. It is NOT possible to have three copies
of the module  inside another module. 

Lets go through some examples.


inst01 - triplicating a fixed macrocell
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this example we have a cell ''logic'' (which presumably comes from the library)
and we dont want to touch internal of the cell. That is why a directive 
''do_not_touch'' is added in the module declaration. 


.. image:: inst01.png
   :align: center

.. literalinclude:: ../../examples/inst01.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/inst01TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/inst01.rst

inst02 - non triplicating a fixed macrocell
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you do not want to triplicate a cell which has ''do_not_touch'' property, you 
have to apply ''do_not_triplicate'' constrain specifying **INSTANCE** (not module), similarly as it was in case of signals.
Voters and fanouts will be added if necessary. 


.. image:: inst02.png
   :align: center

.. literalinclude:: ../../examples/inst02.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/inst02TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/inst02.rst


inst03 - triplicating user's macrocell
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When the module being instantiated is a subject of triplication as well, only connections
are modified and voters and fanouts are added if necessary. An example bellow shows a
situation when two modules (parent and child) are to be fully triplicated.

.. image:: inst03.png
   :align: center

.. literalinclude:: ../../examples/inst03.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/inst03TMR.v
   :language: verilog
   :linenos:

.. include:: ../../examples/inst03.rst


Accessing individual signals from a triplicated bus
###################################################

In some very spetial cases you may want to access signals after the triplication
individually. Lets condider two examples:

powerOnReset
^^^^^^^^^^^^

Imagine that you are designing a reset circuit. You want to have a Power-on
reset (POR) block and an external reset signal. As you do not want that SET in
POR block resets your chip, you may decide to triplicate the block. From the 
practical reasons, you still want to keep only one external reset pin.

.. literalinclude:: ../../examples/resetBlock01.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/resetBlock01TMR.v
   :language: verilog
   :linenos:

There is not magic until now. If you decided that you would like to able to 
check during normal operation what is the status of the POR output, the straight
forward way of doing that would be:


.. literalinclude:: ../../examples/resetBlock02.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/resetBlock02TMR.v
   :language: verilog
   :linenos:


Lets think if this is what you really want. You may see that 'porStatus'' signal got triplicated 
which is of course what we want. If you connect it to some kind of digital bus, 
most likely you will have some voting on the way, so you will not have an information
about individual signals. In order to solve the problem, you have to "code" some triplication
manually. If you declare a wire with a special name and with a special assigment (like bellow) 
you gain access to the signal after triplication

.. code-block:: verilog
   :linenos:

   wire myWire;
   wire myWireA=myWire;
   wire myWireB=myWire;
   wire myWireC=myWire;

This convention ensures that you can still simulate and synthesize you original design.
TMRG will convert this declarations during elaboration process to the desired ones.
Lets see how we can use this in our resetBlock example.

.. literalinclude:: ../../examples/resetBlock03.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/resetBlock03TMR.v
   :language: verilog
   :linenos:

As you can see, we ended up with triplicated bus (9 signals!). To finish 
the considerations about resetBlock, one may want also to make it more robust
by voting porRst signal.

.. literalinclude:: ../../examples/resetBlock04.v
   :language: verilog
   :linenos:

.. literalinclude:: ../../examples/resetBlock04TMR.v
   :language: verilog
   :linenos:


clockGating
^^^^^^^^^^^


Using voting error output
###################################################
