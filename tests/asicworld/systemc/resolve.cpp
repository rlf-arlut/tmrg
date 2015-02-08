#include <systemc.h>

SC_MODULE(module_A) {
  sc_in_rv<1>  in;
  sc_out_rv<1> out;
  sc_inout_rv<4> inout;

  void body () {
    out.write(in);
    if (in.read() == 1) {
      out.write(1);
      inout.write(rand());
    } else {
      out.write('z');
      inout.write('zzzz');
    }
  }
 
  SC_CTOR(module_A) {
    SC_METHOD(body);
      sensitive << in;
  }
};
