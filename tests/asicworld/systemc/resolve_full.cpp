#include <systemc.h>

SC_MODULE(resolve) {
  sc_in_rv<1>  in;
  sc_out_rv<1> out;
  sc_inout_rv<4> inout;

  void body () {
    out.write(in);
    if (in.read() == 1) {
      out.write(1);
      inout.write(rand());
    } else {
      out.write("z");
      inout.write("zzzz");
    }
  }
 
  SC_CTOR(resolve) {
    SC_METHOD(body);
      sensitive << in;
  }
};

// Testbench to generate test vectors
int sc_main (int argc, char* argv[]) {
  sc_signal_rv<1> in1,in2;
  sc_signal_rv<1> out;
  sc_signal_rv<4> inout;

  resolve rs1("RESOLVE1");
    rs1.in(in1);
    rs1.out(out);
    rs1.inout(inout);
  resolve rs2("RESOLVE2");
    rs2.in(in2);
    rs2.out(out);
    rs2.inout(inout);

  sc_start(0);
  // Open VCD file
  sc_trace_file *wf = sc_create_vcd_trace_file("resolve");
    sc_trace(wf, in1, "in1");
    sc_trace(wf, in2, "in2");
    sc_trace(wf, out, "out");
    sc_trace(wf, inout, "inout");
  // Start the testing here
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_start(1);
  in1 = 0;
  in2 = 0;
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_start(1);
  in1 = 1;
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_start(1);
  in1 = 0;
  in2 = 1;
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_start(1);
  in2 = 0;
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_start(1);
  in1 = 1;
  in2 = 1;
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_start(1);
  in1 = 0;
  in2 = 0;
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_start(2);
  cout << "@" << sc_time_stamp() <<" in1 : " << in1
    <<" in2 : " << in2 <<" out : " << out <<" inout : " << inout << endl;
  sc_close_vcd_trace_file(wf);
  return 0;// Terminate simulation
};
