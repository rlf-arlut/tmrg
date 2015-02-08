#include "systemc.h"

SC_MODULE (local_variable) {
  sc_in_clk     clock ;      // Clock input of the design
  sc_in<bool>   reset ;      // active high, synchronous Reset input
  sc_in<bool>   enable;      // Active high enable signal for counter
  sc_out<sc_uint<4> > counter_out; // 4 bit vector output of the counter

  //------------Local Variables Here---------------------
  sc_uint<4>	count;

  //------------Code Starts Here-------------------------
  // Below function implements actual counter logic
  void incr_count () {
    // Body of the function
  } // End of function incr_count

  // Constructor for the counter
  SC_CTOR(local_variable) {
    cout<<"Executing new"<<endl;
    SC_METHOD(incr_count);
    sensitive << reset;
    sensitive << clock.pos();
  } // End of Constructor

}; // End of Module counter
