#include "systemc.h"

SC_MODULE(dff) {
  sc_in  <bool> din; // Data input of FF
  sc_in  <bool> clk; // Clock input of FF
  sc_out <bool> dout;// Q output of FF
  
  void implement() {  // Process that implements DFF
    dout = din;
  }
  
  SC_CTOR(dff) {
    SC_METHOD(implement); // Contains a process named implement
    sensitive_pos << clk; // Execute implements() at every posedge of clk 
  }
};
