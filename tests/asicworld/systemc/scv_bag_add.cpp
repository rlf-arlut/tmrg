#include <scv.h>

enum packet_types_t { NORMAL, RUNT, OVERSIZE };

class packet {
public:
  packet_types_t  ptype;
  sc_uint<48>     src;
  sc_uint<48>     dest;
  sc_uint<16>     length;

public:
  packet(); 
  packet(const packet & src); 
  const packet & operator=(const packet & src);
  void dump(void) const;
}; // class packet ..

// --------------------------------------------------------------
// ENUM Extension
SCV_ENUM_EXTENSIONS(packet_types_t) {
 public:
  SCV_ENUM_CTOR(packet_types_t) {
    SCV_ENUM(NORMAL);
    SCV_ENUM(RUNT);
    SCV_ENUM(OVERSIZE);
  };
};
// Packet Extension
SCV_EXTENSIONS(packet) {
 public:
    scv_extensions< packet_types_t > ptype;
    scv_extensions< sc_uint<48> > src;
    scv_extensions< sc_uint<48> > dest;
    scv_extensions< sc_uint<16> > length;

  SCV_EXTENSIONS_CTOR(packet) {
    SCV_FIELD(ptype);
    SCV_FIELD(src);
    SCV_FIELD(dest);
    SCV_FIELD(length);
  }
};

// --------------------------------------------------------------
// constructors & copy assignment
packet::packet() {
  ptype = NORMAL;
};

packet::packet(const packet & p) : ptype(p.ptype), src(p.src), dest(p.dest) { };

const packet & packet::operator=(const packet & p) {
  ptype  = p.ptype;
  length = p.length;
  src    = p.src;
  dest   = p.dest;
  return *this;
}; // packet & operator=

// We could use print() (from the scv_extensions utility interface)
// in place of this function.  However, the interest in this function
// is not so much what it does, but to demonstrate how to access
// functions within classes from higher levels in the program.
void packet::dump(void) const {
  const scv_extensions<packet> p = scv_get_const_extensions(*this);
  cout << " " << length;
  cout << " " << src;
  cout << " " << dest;
  cout << " " << p.ptype.get_enum_string(p.ptype) << endl;
}

// --------------------------------------------------------------
// Normal Packet Constraint
class normal_packet : virtual public scv_constraint_base {
public:
  scv_smart_ptr<packet> sp;
public:
  SCV_CONSTRAINT_CTOR(normal_packet) {
    SCV_CONSTRAINT(sp->src() <= 0x3FF);
    SCV_CONSTRAINT(sp->dest() <= 0x3FF);
    SCV_SOFT_CONSTRAINT(sp->src() != sp->dest());
    SCV_CONSTRAINT(sp->ptype() == NORMAL);
    SCV_SOFT_CONSTRAINT(sp->length() >= 64 && sp->length() <= 1500);
  } 
};
// Runt Packet Constraint
class runt_packet : virtual public scv_constraint_base {
public:
  scv_smart_ptr<packet> sp;
public:
  SCV_CONSTRAINT_CTOR(runt_packet) {
    SCV_CONSTRAINT(sp->src() > 0x3FF && sp->src() <= 0x4FF);
    SCV_CONSTRAINT(sp->dest() > 0x3FF && sp->dest() <= 0x4FF);
    SCV_SOFT_CONSTRAINT(sp->src() != sp->dest());
    SCV_CONSTRAINT(sp->ptype() == RUNT);
    SCV_SOFT_CONSTRAINT(sp->length() < 64 && sp->length() > 20);
  } 
};

// Runt Packet Constraint
class oversize_packet : virtual public scv_constraint_base {
public:
  scv_smart_ptr<packet> sp;
public:
  SCV_CONSTRAINT_CTOR(oversize_packet) {
    SCV_CONSTRAINT(sp->src() > 0x4FF && sp->src() <= 0x5FF);
    SCV_CONSTRAINT(sp->dest() > 0x4FF && sp->dest() <= 0x5FF);
    SCV_SOFT_CONSTRAINT(sp->src() != sp->dest());
    SCV_CONSTRAINT(sp->ptype() == OVERSIZE);
    SCV_SOFT_CONSTRAINT(sp->length() < 5000 && sp->length() > 1500);
  } 
};

// --------------------------------------------------------------
int sc_main(int argc, char** argv) {
  // Set the Seed to 1
  scv_random::set_global_seed(2);
  scv_smart_ptr<int> type;
  oversize_packet op ("OVR_PKT");
  normal_packet   np ("NOR_PKT");
  runt_packet     rp ("RNT_PKT");
  scv_smart_ptr<packet> smart_p_ptr;
  
  scv_bag<int> dist;
  dist.add(0, 40); // specify 1 as legal value and 40% weight 
  dist.add(1, 30); // specify 1 as legal value and 30% weight
  dist.add(2, 30); // specify 2 as legal value and 30% weight
  type->set_mode(dist); // set distribution of values 
  for (int i = 0; i < 10; i ++) {
    type->next();
    //type->print();
    if (type->read() == 0) {
      smart_p_ptr->use_constraint(np.sp);
    } else if (type->read() == 1) {
      smart_p_ptr->use_constraint(rp.sp);
    } else if (type->read() == 2) {
      smart_p_ptr->use_constraint(op.sp);
    }
    smart_p_ptr->next();
    smart_p_ptr->read().dump();
  }
  // Demo the scv_bag pair syntax and usage
  scv_smart_ptr<int> data; // Some data
  scv_bag<pair <int, int> > field_dist;
    field_dist.add( pair<int,int>(0,10),  20);
    field_dist.add( pair<int,int>(11,20), 20);
    field_dist.add( pair<int,int>(61,80), 30);
    field_dist.add( pair<int,int>(81,90), 30);
  data->set_mode(field_dist); 
  for (int i = 0; i < 10; i ++) {
    data->next();
    data->print();
  }
  return (0);
}
