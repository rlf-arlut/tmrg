#include <systemc.h>

int sc_main (int argc, char* argv[]) {
  sc_int<1>  bit_size    = 0;
  sc_int<4>  nibble_size = 1;
  sc_int<8>  byte_size   = 2;
  sc_int<32> dword_size  = 3;
  //sc_int<128> addr; sc_int can not be more then 64
  // Perform auto increment
  dword_size ++;
  cout <<"Value of dword_size : " << dword_size << endl;
  // Terse method addition
  byte_size += nibble_size;
  cout <<"Value of byte_size  : " << byte_size << endl;
  // Bit selection
  bit_size = dword_size[2];
  cout <<"Value of bit_size   : " << bit_size << endl;
  // Range selection
  nibble_size = dword_size.range(4,1); // Can not assign out of range
  cout <<"Value of nibble_size: " << nibble_size << endl;
  // Concatenated
  dword_size = (byte_size,byte_size,byte_size,byte_size);
  cout <<"Value of dword_size : " << dword_size << endl;

  return 1;
}
