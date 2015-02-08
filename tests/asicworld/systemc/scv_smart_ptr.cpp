#include <scv.h>

class packet_t {
  public : 
    sc_uint<8>  addr;
    sc_uint<12> data;
};

SCV_EXTENSIONS(packet_t) {
  public:
    scv_extensions< sc_uint<8> > addr;
    scv_extensions< sc_uint<12> > data;
    SCV_EXTENSIONS_CTOR(packet_t) {
      SCV_FIELD(addr);
      SCV_FIELD(data);
    }
};

void do_something (scv_smart_ptr<packet_t> p) {
  cout << "address : " << p->addr << endl;
  cout << "data : " << p->data << endl;
  if (p->data == 0) {
    p-> data = rand();
  }
  if (p-> addr == 0) {
    p-> addr = rand();
  }
  cout << "The whole packet : " << endl;
  p->print();
};

int sc_main (int argc, char* argv[]) {
  scv_smart_ptr<packet_t> pkt_p("packet");
  do_something(pkt_p);
  return 0;
}
