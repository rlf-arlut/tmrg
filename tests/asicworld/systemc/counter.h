#ifndef COUNTER_H
#define COUNTER_H

#include "systemc.h"

SC_MODULE (counter) {
  sc_in<bool>          clk;   // clock input
  sc_out<bool>         rst;   // reset ouput
  sc_in<sc_uint<32> >  d_out; // data input
  sc_out<int>          done;  // Terminate sim       

  void cnt_model ();
  void monitor   ();
  void test      ();

  sc_uint<32>  cnt; // counter model
  int error; // Error status

  SC_CTOR(counter) {
    SC_CTHREAD(monitor,clk.pos());
    SC_CTHREAD(cnt_model,clk.pos());
    SC_CTHREAD(test,clk.pos());
  }
};

#endif
