#include "systemc.h"

SC_MODULE (counter) {
  sc_signal <bool>        reset ;      
  sc_signal <bool>        enable;      
  sc_signal <sc_uint<4> > counter_out; 

  // Rest of body
}
