#include <systemc.h>

int sc_main (int argc, char* argv[]) {
  // Declare the sc_bit
  sc_bit x;
  // Declare the sc_logic
  sc_logic y,z;
  // Asign values to x,y,x
  x = '1';
  y = '1';
  z = 'x';
  // sc_bit and sc_logic
  if (x == y) { 
    cout <<"x = y " << endl;
  } else {
    x = y; // Assign sc_logic to sc_bit
    cout <<"x != y " << endl;
    cout<<"New Value of x : "<< x << endl;
  }
  // sc_logic and sc_logic
  if (y != z) { 
    y = z; // Assign sc_bit to sc_logic 
    cout <<"y != z " << endl;
    cout<<"New Value of y : "<< y << endl;
  }
  // sc_logic and character literal
  if (y == 'x') { 
    cout<<"y equal to value 'X'"<< endl;
  }

  return 1;
}
