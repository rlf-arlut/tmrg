//-----------------------------------------------------
// Design Name : up_counter
// File Name   : up_counter.cpp
// Function    : Up counter
// Coder       : Deepak Kumar Tala
//-----------------------------------------------------
#include "systemc.h"

SC_MODULE (up_down_counter) {
  //-----------Input Ports---------------
  sc_in    <bool> enable, clk, reset;
  //-----------Output Ports---------------
  sc_out   <sc_uint<8> > out;
  //------------Internal Variables--------
  sc_uint<8>  count;

  //-------------Code Starts Here---------
  void counter () {
    if (reset.read()) { 
      count = 0 ;
    } else if (enable.read()) {
      count = count + 1;
    }
    out.write(count);
  }

  SC_CTOR(up_down_counter) {
    SC_METHOD (counter);
      sensitive << clk.pos();
  }

};
