#include <scv.h>

#define RND_SEED 1

class packet_t {
  public : 
    sc_uint<8>  addr;
    sc_uint<12> data;
    unsigned payload[2];
};

SCV_EXTENSIONS(packet_t) {
  public:
    scv_extensions< sc_uint<8> > addr;
    scv_extensions< sc_uint<12> > data;
    scv_extensions< unsigned [2] > payload;
    SCV_EXTENSIONS_CTOR(packet_t) {
      SCV_FIELD(addr);
      SCV_FIELD(data);
      SCV_FIELD(payload);
    }
};

int sc_main (int argc, char* argv[]) {
  scv_smart_ptr<packet_t> pkt_p("packet");
  scv_shared_ptr<scv_random> rand_p(new scv_random("gen", RND_SEED));
  pkt_p->set_random(rand_p);
  cout << "Packet Pre  Random: " << endl;
  pkt_p->print();
  // Disable randomization on addr field
  pkt_p->addr.disable_randomization();
  pkt_p->addr.write(100);
  //  Randomize whole packet
  pkt_p->next();
  cout << "Packet Post Random: " << endl;
  pkt_p->print();
  //  Randomize just one field
  pkt_p->payload.next();
  pkt_p->data.next();
  cout << "Packet Post Random: " << endl;
  pkt_p->print();

  return 0;
}
