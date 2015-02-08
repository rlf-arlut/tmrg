#include <scv.h>

int sc_main(int argc, char** argv) {
  // Set the Seed to 1
  scv_random::set_global_seed(1);
  scv_smart_ptr<int> data;
  data->keep_only(0,3); 
  data->keep_out(1); 
  for (int i = 0; i < 10; i ++) {
    data->next();
    data->print();
  }
  return (0);
}
