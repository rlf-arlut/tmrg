#include <scv.h>

//enum for one hot coding
enum onehot_t {
  STATE_0 = 0, STATE_1 = 1, STATE_2 = 2, STATE_3 = 4,
  STATE_4 = 8, STATE_5 = 16, STATE_6 = 32 };

struct data_t {
  sc_uint<8> field;
  unsigned   payload[5];
  onehot_t   state;
};

template<>
class scv_extensions<onehot_t> : public scv_enum_base<onehot_t> {
  public:
    SCV_ENUM_CTOR(onehot_t) {
      SCV_ENUM(STATE_0);
      SCV_ENUM(STATE_1);
      SCV_ENUM(STATE_2);
      SCV_ENUM(STATE_3);
      SCV_ENUM(STATE_4);
      SCV_ENUM(STATE_5);
      SCV_ENUM(STATE_6);
    }
};

template<>
class scv_extensions<data_t> : public scv_extensions_base<data_t> {
public:
  scv_extensions<sc_uint<8> > field;
  scv_extensions<unsigned   [5]> payload;
  scv_extensions<onehot_t   > state;
  SCV_EXTENSIONS_CTOR(data_t) {
    //must be in order
    SCV_FIELD(field);
    SCV_FIELD(payload);
    SCV_FIELD(state);
  }
};

int sc_main (int argc, char* argv[]) {
  data_t  data; 
  data.field = rand();
  for (int i=0; i<5; i++) {
    data.payload[i] = rand();
  }
  data.state = STATE_0;
  scv_get_extensions(data).print();
  return 0;
}
