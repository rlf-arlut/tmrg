#include <scv.h>

int sc_main (int argc, char* argv[]) {
  scv_smart_ptr< sc_uint<8> > data;
  cout <<"Value of data pre  randomize : " << endl;
  data->print();
  data->next(); // Randomize object data
  cout <<"Value of data post randomize : " << endl;
  data->print();
  return 0;
}
