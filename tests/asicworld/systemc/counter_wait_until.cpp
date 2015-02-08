//-----------------------------------------------------
// This is my second Systemc Example
// Design Name : first_counter
// File Name : first_counter.cpp
// Function : This is a 4 bit up-counter with
// Synchronous active high reset and
// with active high enable signal
//-----------------------------------------------------
#include "systemc.h"

SC_MODULE (first_counter) {
  sc_in_clk     clock ;      // Clock input of the design
  sc_in<bool>   reset ;      // active high, synchronous Reset input
  sc_in<bool>   enable;      // Active high enable signal for counter
  sc_out<sc_uint<4> > counter_out; // 4 bit vector output of the counter

  //------------Local Variables Here---------------------
  sc_uint<4>	count;

  //------------Code Starts Here-------------------------
  // Below function implements actual counter logic
  void incr_count () {
    // For threads, we need to have while true loop
    while (true) { 
      // Wait until rest is true or enable is true
      // Every wait_until delays execution by one clock.pos()
      wait_until(reset.delayed() == true || enable.delayed() == true);
      if (reset.read() == 1) {
        count =  0;
        counter_out.write(count);
      // If enable is active, then we increment the counter
      } else if (enable.read() == 1) {
        count = count + 1;
        counter_out.write(count);
      }
    }
  } // End of function incr_count

  // Below functions prints value of count when ever it changes
  void print_count () {
    while (true) {
      wait();
      cout<<"@" << sc_time_stamp() <<
        " :: Counter Value "<<counter_out.read()<<endl;
    }
  }

  // Constructor for the counter
  // Since this counter is a positive edge trigged one,
  // We trigger the below block with respect to positive
  // edge of the clock
  SC_CTOR(first_counter) {
    // Edge sensitive to clock
    SC_CTHREAD(incr_count, clock.pos());
    // Level Sensitive to change in counter output
    SC_THREAD(print_count);
    sensitive << counter_out;
  } // End of Constructor

}; // End of Module counter
