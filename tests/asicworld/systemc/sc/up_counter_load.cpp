//-----------------------------------------------------
// Design Name : up_counter_load
// File Name   : up_counter_load.cpp
// Function    : Up counter with load
// Coder       : Deepak Kumar Tala
//-----------------------------------------------------
#include "systemc.h"

SC_MODULE (up_counter_load) {
  //-----------Input Ports---------------
  sc_in    <sc_uint<8> > data;
  sc_in    <bool> load, enable, clk, reset;
  //-----------Output Ports---------------
  sc_out   <sc_uint<8> > out;
  //------------Internal Variables--------
  sc_uint<8>  count;

  void counter () {
    if (reset.read()) { 
      count = 0 ;
    } else if (enable.read()) {
      if (load.read()) {
        count = data.read();
      } else {
        count = count + 1;
      }
    }
    out.write(count);
  }

  SC_CTOR(up_counter_load) {
    SC_METHOD (counter);
      sensitive << clk.pos();
  }
};
