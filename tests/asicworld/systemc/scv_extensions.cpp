#include <scv.h>

int sc_main (int argc, char* argv[]) {
  // Int data type
  int data = 100; 
  // Get the bitwidth of the data
  int bitwidth = scv_get_extensions(data).get_bitwidth();
  cout << "Width of data is "<< bitwidth << endl;
  cout << "Value in data is ";
  // Get the value in data and print to stdio
  scv_get_extensions(data).print();
  return 0;
}
