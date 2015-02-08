//-----------------------------------------------------
// Design Name : tff_async_reset
// File Name   : tff_async_reset.cpp
// Function    : T flip-flop async reset
// Coder       : Deepak Kumar Tala
//-----------------------------------------------------
#include "systemc.h"

SC_MODULE (tff_async_reset) {
  sc_in    <bool> data, clk, reset  ;
  sc_out   <bool> q;

  bool q_l ;

  void tff () {
    if (~reset.read()) {
      q_l = 0;
    } else if (data.read()) {
      q_l = !q_l;
    }
    q.write(q_l);
  }

  SC_CTOR(tff_async_reset) {
    SC_METHOD (tff);
      sensitive << reset;
      sensitive << clk.pos();
  }

};
