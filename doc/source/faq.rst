Frequently Asked Questions (FAQ)
********************************************************************************


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

