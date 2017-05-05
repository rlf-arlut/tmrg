Frequently Asked Questions (FAQ)
********************************************************************************


How to report bugs and request support?
################################################################################

It is recomended to report issues using GITLAB issue tracking system which can be found here: https://gitlab.cern.ch/skulis/tmrg/issues.

A good bug report contains a minimal, complete, and verifiable code example that demonstrates the problem you are running into. Complete means not just a code snippet, but an entire top verilog module that can be synthesized. Also include all the parameters and/or configuration files. It should be possible to reproduce the problem you are seeing within seconds using the information you provided! Every file of line of code someone trying to reproduce your problem has to write themselves will increase the effort someone has to put into reproducing your problem and at the same time will decrease the chances of your problem being reproduced correctly!

You may also use build in report generator:

.. code-block:: bash
   :linenos:

   # tmrg --generate-report [other options]


Always consider that someone reading your bug report only has the information you provided. Before clicking the send button on your bug report and/or support request, double check that you have provided all the information necessary to easily and quickly reproduce the problem you are seeing.



TMRG does not create nice parsing errors 
################################################################################

That is right, the parser used for the TMRG tool can report errors which are not really meaning full and can point to the wrong location in the source code. The focus so far for development of the TMRG was on triplication features and processing valid input, not good error reporting for invalid code. It can happen, that in some cases it will even accept invalid code! You are advised to make sure that the code which you input to the tmrg tool is valid verilog code. Please use your simulator and/or synthesis tool first (iverilog, irun, rc, gennus, ...).

You should always simulate your designs first before going to triplication!



Is System verilog supported?
################################################################################

Short answer is **NO**, and there is no short feature plan to add it. 
However, some of the language features are recognized and processed properly. 

How do I input multiple files to tmrg?
################################################################################

Using command line arguments you can use:

.. code-block:: bash
   :linenos:

   # tmrg file1.v file2.v file3.v

If you are using configuration file (an example can be found in ``tmrg/etc/tmrg.cfg``), 
you should add your files to the variable ``files`` in section ``tmrg``:

.. code-block:: ini
   :linenos:

   [tmrg]
   files = file1.v file2.v file3.v


How do I redirect output from the tmrg to another directory?
################################################################################

Using command line arguments you can use:

.. code-block:: bash
   :linenos:

   # tmrg --tmr-dir "output" [other options]

If you are using configuration file (an example can be found in ``tmrg/etc/tmrg.cfg``), 
you should define your output directory using the variable ``tmr_dir`` in section ``tmrg``:

.. code-block:: ini
   :linenos:

   [tmrg]
   tmr_dir = output



How do I increase verbosity level of the tmrg?
################################################################################

Please use ``-v`` option (or multiplicity of it):

.. code-block:: bash
   :linenos:

   # tmrg -v [other options]
   # tmrg -vv [other options]
   # tmrg -vvv [other options]

