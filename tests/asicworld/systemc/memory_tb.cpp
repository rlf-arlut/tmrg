#include "systemc.h"
#include "memory_txGen.h"
#include "memory_tb_ports.h"
#include "memory_tb_exports.h"
#include "strings.h"

// Instantiate Testbench
memory_txGen  u_memory_txGen("u_memory_txGen");
// Declare Signals to connect tb
sc_signal <bool>             clk;
sc_signal <sc_uint<8> >      addr;
sc_signal <bool>             wr;
sc_signal <bool>             cs;
sc_signal <sc_uint<32> >     wdata;
sc_signal <sc_uint<32> >     rdata;
sc_signal <bool>             done;
// Top-Level testbench
void init_sc() {
  // Port mapping
  u_memory_txGen.clk        (clk  );
  u_memory_txGen.addr       (addr );
  u_memory_txGen.wr         (wr   );
  u_memory_txGen.cs         (cs   );
  u_memory_txGen.wdata      (wdata);
  u_memory_txGen.rdata      (rdata);
  u_memory_txGen.done       (done );
  // VCD Tracing:
  //   Trace file creation
  sc_trace_file* tf;
  tf = sc_create_vcd_trace_file("memory_tb");
        ((vcd_trace_file*)tf)->sc_set_vcd_time_unit(-9);
  //   Signals to be traced
  sc_trace(tf, clk, "clk");
  sc_trace(tf, addr, "addr");
  sc_trace(tf, wr, "wr");
  sc_trace(tf, cs, "cs");
  sc_trace(tf, wdata, "wdata");
  sc_trace(tf, rdata, "rdata");
  // Initialize SC
  sc_start(0);
  cout<<"@"<<sc_time_stamp()<<" Started SystemC Schedular"<<endl;
}
// Convert Char to sc_unit
// This is required if more then 64 bits are
// required for port width
sc_uint<32> str2scuint(char *data) {
  sc_uint<32>  udata;
  for (int i = 31; i >= 0; i--) {
    if (*(data+i) == 49) {
      udata[31-i] = 1;
    } else {
      udata[31-i] = 0;
    }
  }
  return(udata);
}
// String to bool conversion
bool str2bool(char *data) {
  bool  udata;
  udata = (*data == 49) ? true:false;
  return(udata);
}
// Sample the HDL signals and driver systemC data types
void sample_hdl(void *Invector) {
  INVECTOR *pInvector = (INVECTOR *)Invector;
  clk    = str2bool(pInvector->clk);
  rdata  = str2scuint(pInvector->rdata);
}
// Drive systemC signals to HDL
void drive_hdl(void *Outvector) {
  OUTVECTOR *pOutvector = (OUTVECTOR *)Outvector;
  pOutvector->wr = wr.read();
  pOutvector->cs = cs.read();
  pOutvector->addr = addr.read();
  pOutvector->done =  done;
  pOutvector->wdata = wdata.read();
}
// Advance SystemC Simulation time
void advance_sim(unsigned long simtime) {
  sc_start(simtime);
}
// Top level testbench controller
void exec_sc(void *invector, void *outvector, 
 unsigned long simtime) {
  sample_hdl(invector);  // Input-Stimuli
  advance_sim(simtime);  // Advance Simulator
  drive_hdl(outvector);  // Output Vectors
}
// Terminate SystemC schedular
void exit_sc() {
  cout<<"@"<<sc_time_stamp()<<" Stopping SystemC Schedular"<<endl;
  sc_stop();
}
