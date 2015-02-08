#include "systemc.h"

SC_MODULE(dff) {
  sc_in  <bool> din; // Data input of FF
  sc_in  <bool> clk; // Clock input of FF
  sc_out <bool> out; // Q output of FF
  
  void implement();  // Process that implements DFF
  
  SC_CTOR(dff) {
    SC_METHOD(implement); 
    sensitive_pos << clk; // Call implements() at every pos edge of clk 
  }
};
