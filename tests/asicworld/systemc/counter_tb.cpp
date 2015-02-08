#include "systemc.h"
#include "counter.h"

#include "counter_tb_ports.h"
#include "counter_tb_exports.h"
#include "strings.h"

// Instantiate Top-Level DUT
counter  u_counter("u_counter");

// Declare Signals
sc_signal<bool>      clk;
sc_signal<bool>      rst;
sc_signal<sc_uint<32> >    d_out;
sc_signal<int>      done;
  
// Top-Level testbench
void init_sc() {
  // Port mapping
  u_counter.clk(clk);
  u_counter.rst(rst);
  u_counter.d_out(d_out);
  u_counter.done(done);
  // VCD Tracing:
  sc_trace_file* tf;
  tf = sc_create_vcd_trace_file("sc_counter");
        ((vcd_trace_file*)tf)->sc_set_vcd_time_unit(-9);
  //   Signals to be traced
  sc_trace(tf, clk, "clk");
  sc_trace(tf, rst, "rst");
  sc_trace(tf, d_out, "d_out");
  // Initialize SC
  sc_start(0);
  cout<<"@"<<sc_time_stamp()<<" Started SystemC Schedular"<<endl;
}

void sample_hdl(void *Invector) {
  INVECTOR *pInvector = (INVECTOR *)Invector;
  clk.write(pInvector->clk);
  d_out.write(pInvector->d_out);
}

void drive_hdl(void *Outvector) {
  OUTVECTOR *pOutvector = (OUTVECTOR *)Outvector;
  pOutvector->rst  =  rst.read()? 1 : 0;
  pOutvector->done =  done;
}

void advance_sim(unsigned long simtime) {
  sc_start(simtime);
}

void exec_sc(void *invector, void *outvector, unsigned long simtime) {
  sample_hdl(invector);    // Input-Stimuli
  advance_sim(simtime);   // Advance Simulator
  drive_hdl(outvector);  // Output Vectors
}

void exit_sc() {
  cout<<"@"<<sc_time_stamp()<<" Stopping SystemC Schedular"<<endl;
  sc_stop();
}
