#include <systemc.h>

int sc_main (int argc, char* argv[]) {
  sc_biguint<128> a  = 30000;
  sc_biguint<128> b  = 20000;
  sc_biguint<256> c  = 0;
  // multiplication operator
  c = a * b;
  cout <<"Value of c : " << c << endl;
  
  return 1;
}
