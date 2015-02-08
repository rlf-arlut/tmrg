#include <systemc.h>

int sc_main (int argc, char* argv[]) {
  sc_lv<8>  data_bus  (sc_logic ('z')); // All bits are Z
  sc_lv<16> addr_bus  ; // All bits are X
  sc_logic  parity    ; 
  // Print Default value of data_bus
  cout <<"Value of data_bus : " << data_bus << endl;
  // Assign value to sc_bv
  data_bus = "00001011";
  cout <<"Value of data_bus : " << data_bus << endl;
  // Use range operator
  addr_bus.range(7,0) = data_bus;   
  cout <<"Value of addr_bus : " << addr_bus << endl;
  // Assign reverse to addr bus using range operator
  addr_bus.range(0,7) = data_bus;   
  cout <<"Value of addr_bus : " << addr_bus << endl;
  // Use bit select to set the value
  addr_bus[10] = "1";
  cout <<"Value of addr_bus : " << addr_bus << endl;
  // Use reduction operator
  parity  = data_bus.xor_reduce(); 
  cout <<"Value of parity   : " << parity << endl;

  return 1;
}
