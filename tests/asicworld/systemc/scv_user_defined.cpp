#include <scv.h>

struct packet_t {
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

int sc_main (int argc, char* argv[]) {
  packet_t  pkt; 
  pkt.addr = rand();
  pkt.data = rand();
  int bitwidth = scv_get_extensions(pkt.addr).get_bitwidth();
  cout << "Width of addr is "<< bitwidth << endl;
  bitwidth = scv_get_extensions(pkt.data).get_bitwidth();
  cout << "Width of data is "<< bitwidth << endl;
  scv_get_extensions(pkt).print();
  return 0;
}
