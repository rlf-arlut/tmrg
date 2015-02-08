#include <stdio.h>  
#include <stdlib.h>

#include "vcsuser.h"

// SystemC methods 
#include "memory_tb_ports.h"
#include "memory_tb_exports.h"

static int sc_init_done = 0;

//calltf routine: turns on asynchronous callbacks to the misctf
//routine whenever an argument to the system task changes value.
int sc_memory_calltf() {
  if (sc_init_done == 0) {
    // Initialize SystemC Model
    init_sc(); 
    sc_init_done = 1;
  }
  // Turn-On Asynchronous Call-Back
  tf_asynchon();  
  return(0);
}

//misctf routine: Serves as an interface between Verilog simulation
//and the testbench.  Called whenever the testbench inputs change value,
//reads the input values, and passes the values to the SystemC, and
//writes the SystemC outputs into simulation.
int sc_memory_misctf(int user_data, int reason, int paramvc)
{
  #define  SC_IN_CLK     1  /* system task arg 1 clk     input  */
  #define  SC_IN_RDATA   2  /* system task arg 2 rdata   input  */
  #define  SC_OUT_ADDR   3  /* system task arg 3 addr    output */
  #define  SC_OUT_WR     4  /* system task arg 4 wr      output */
  #define  SC_OUT_CS     5  /* system task arg 5 cs      output */
  #define  SC_OUT_WDATA  6  /* system task arg 6 wdata   output */

  static unsigned long SimNow = 0;
  // Testbench ports
  static INVECTOR   invector;
  static OUTVECTOR  outvector;
  // If HDL requested simulation termination
  if (reason == reason_finish) {
    exit_sc();
  }
  // abort if misctf was not called for a task argument value change
  if (reason != REASON_PARAMVC) {
    return(0);
  }
  // abort if task argument that changed was a model output 
  if (paramvc != SC_IN_RDATA && paramvc != SC_IN_CLK)  { 
    return(0);
  }
  // Read current HDL values into systemC testbench 
  invector.rdata  = acc_fetch_value(acc_handle_tfarg(SC_IN_RDATA), "%b", 0);
  invector.clk    = acc_fetch_value(acc_handle_tfarg(SC_IN_CLK), "%b", 0);
  // Execute the systemC testbench with  delta time  
  exec_sc(&invector, &outvector, (tf_gettime()-SimNow));
  SimNow = tf_gettime();
  // Write the systemC Testbench outputs onto the Verilog signals
  tf_putp(SC_OUT_ADDR, outvector.addr);
  tf_putp(SC_OUT_WR, outvector.wr);
  tf_putp(SC_OUT_CS, outvector.cs);
  tf_putp(SC_OUT_WDATA, outvector.wdata);
  // If systemC requests termination, then ask Verilog simulator 
  // to terminate
  if (outvector.done) {
    tf_dofinish();
  }
  return(0);
}
