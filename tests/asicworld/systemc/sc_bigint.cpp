#include <systemc.h>

int sc_main (int argc, char* argv[]) {
  sc_bigint<128> large_size ;
  // Shift operator
  large_size =  1000 << 1;
  cout <<"Value of large_size : " << large_size << endl;
  
  return 1;
}
