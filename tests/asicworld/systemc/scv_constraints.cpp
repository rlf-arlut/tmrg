#include <scv.h>

struct packet_t {
  sc_uint<32> src_addr;
  sc_uint<32> dest_addr;
  sc_uint<16> length;
};
// nbcode "packet" end

//define an ostream for a packet object
ostream& operator<<(ostream& os, const packet_t& p) {
  os << "   src_addr : " << p.src_addr  << "\n"
     << "   dest_addr: " << p.dest_addr << "\n"
     << "   length   : " << p.length    << endl;
  return os;
}

// Create packet extension
template<>
class scv_extensions<packet_t> : public scv_extensions_base<packet_t> {
public:
  scv_extensions<sc_uint<32> > src_addr;
  scv_extensions<sc_uint<32> > dest_addr;
  scv_extensions<sc_uint<16> > length;

  SCV_EXTENSIONS_CTOR(packet_t) {
    //must be in order
    SCV_FIELD(src_addr);
    SCV_FIELD(dest_addr);
    SCV_FIELD(length);
  }
};

//Create a basic default constraint for the packet generator
struct packet_base_constraint : public scv_constraint_base {
  //create a packet object
  scv_smart_ptr<packet_t> packet;
  //put the base constraints on the packet variables
  SCV_CONSTRAINT_CTOR(packet_base_constraint) {
    // Soft Constraint
    SCV_SOFT_CONSTRAINT ( packet->length() < 1500 ); // Max Frame Size 
    SCV_SOFT_CONSTRAINT ( packet->length() > 64 );   // Mix Frame Size 
    // Hard Constraint
    SCV_CONSTRAINT ( packet->src_addr()   != packet->dest_addr());
    // Hard limit on min frame size
    SCV_CONSTRAINT ( packet->length() > 20 );  
  }
};

// Create a actual contraint for the testcase
struct packet_basic_constraint : public packet_base_constraint {
  //add config variable
  scv_smart_ptr<sc_uint<32> > dest_min;
  scv_smart_ptr<sc_uint<32> > dest_max;

  SCV_CONSTRAINT_CTOR(packet_basic_constraint) {
    //use the base constraint
    SCV_BASE_CONSTRAINT(packet_base_constraint);
    //add extra constraints
    SCV_CONSTRAINT ((packet->dest_addr() > dest_min()) &&  
                   (packet->dest_addr() < dest_max()) );
    SCV_CONSTRAINT (
      ((packet->src_addr() > (packet->dest_addr() + 0x100000) ) &&   
       (packet->src_addr() < (packet->dest_addr() + 0x200000) ) ) ||   
      ((packet->src_addr() < (packet->dest_addr() - 0x10000) )) &&   
       (packet->src_addr() > (packet->dest_addr() - 0xfffff) ) );   
    SCV_CONSTRAINT ( packet->length() == 64 );  
  }
};

int sc_main(int argc, char** argv) {
  // Set the Seed to 1
  scv_random::set_global_seed(1);
  //instatiate test specific constraints
  packet_basic_constraint pkt("Constrained Packet");
  // Disable randomization 
  pkt.dest_min->disable_randomization();
  pkt.dest_max->disable_randomization();
  // Set the values manually
  *pkt.dest_min = 0x100000;
  *pkt.dest_max = 0x800000;
  for(int i=0; i<5; ++i) {
    pkt.next();
    cout << pkt.packet->get_name() << *(pkt.packet) << endl;
  }
  cout << endl;
  return (0);
}
