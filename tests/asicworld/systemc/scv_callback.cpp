#include <scv.h>

void my_callback ( scv_extensions_if& data, 
                   scv_extensions_if::callback_reason r) {
  if (r == scv_extensions_if::VALUE_CHANGE) {
     cout << "The data is assigned value : ";
     data.print();
     // Do what ever you want to do
  }
}

int sc_main(int argc, char** argv) {
  // Set the Seed to 1
  scv_random::set_global_seed(1);
  scv_smart_ptr<int> data;

  data->register_cb(my_callback);
  data->keep_only(0,3); 
  data->keep_out(1); 
  for (int i = 0; i < 10; i ++) {
    data->next();
    data->print();
  }
  return (0);
}
