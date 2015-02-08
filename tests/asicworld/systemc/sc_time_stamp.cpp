#include <systemc.h>

int sc_main (int argc, char* argv[]) {
  cout<<"Current time is "<< sc_time_stamp() << endl;
  sc_start(1);
  cout<<"Current time is "<< sc_time_stamp() << endl;
  sc_start(100);
  cout<<"Current time is "<< sc_time_stamp() << endl;
  sc_stop();
  cout<<"Current time is "<< sc_time_stamp() << endl;
  return 0;// Terminate simulation
}
