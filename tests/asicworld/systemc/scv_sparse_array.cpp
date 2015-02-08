#include "scv.h"

// Define a packet with a variable size payload
class packetT {
  public:
    packetT () {}
    virtual ~packetT() {}
    // Packet's data
    sc_uint<16> src;
    sc_uint<16> dest;
    sc_uint<16> length; // Number of items in the payload
    sc_uint<16> payload[1024];
    // Define an equal operator
    packetT& operator=(const packetT& rhs) {
      src=rhs.src; dest=rhs.dest; length=rhs.length;
      for(unsigned int i=0; (i<length) && (i<1024); i++)
        payload[i]=rhs.payload[i];
      return *this;
    }
    // Define a comparison operator
    friend bool operator==(const packetT& a, const packetT& b) {
      if (a.src != b.src) {return false;}
      if (a.dest != b.dest) {return false;}
      if (a.length != b.length) {return false;}
      for(unsigned int i=0; (i<a.length) && (i<1024); i++)
        if (a.payload[i] != b.payload[i]) {return false;}
      return true;
    }
    // Define a not-equal operator (some compilers do not
    // automatically create this from operator=)
    friend bool operator!=(const packetT& a, const packetT& b) {
      if (a.src != b.src) {return true;}
      if (a.dest != b.dest) {return true;}
      if (a.length != b.length) {return true;}
      for(unsigned int i=0; (i<a.length) && (i<1024); i++)
        if (a.payload[i] != b.payload[i]) {return true;}
      return false;
    }
    // Define ostream method to print data
    friend ostream& operator<< (ostream& os, const packetT& p) {
      os << "  src: "     <<  p.src
         << "  dest: "    <<  p.dest
         << "  length: "  <<  p.length 
         << "  payload: " <<  p.payload[0]
         << " .. "        <<  p.payload[p.length-1];
      return os;
    }
};

// Extensions to packetT
template<>
class scv_extensions<packetT> : public scv_extensions_base<packetT> {
public:
  scv_extensions< sc_uint<16>       > src;
  scv_extensions< sc_uint<16>       > dest;
  scv_extensions< sc_uint<16>       > length;
  scv_extensions< sc_uint<16>[1024] > payload;
  SCV_EXTENSIONS_CTOR(packetT) {
    //must be in order
    SCV_FIELD(src);
    SCV_FIELD(dest);
    SCV_FIELD(length);
    SCV_FIELD(payload);
  }
};

SC_MODULE(sctop) {
  SC_CTOR(sctop);
};

sctop::sctop(sc_module_name name) : sc_module(name)
{
  // Create a sparse packet array
  packetT defaultPacket;
  sc_int<64> upper_bound;
  upper_bound = ( ( (long long) 1 ) << 63 ) - 1;
  const sc_int<64> lower_bound = -(upper_bound+1);
  scv_sparse_array< sc_int<64>, packetT >
    packets("packets", defaultPacket,
            lower_bound, upper_bound);
  // Create an index to the sparse packet array
  scv_smart_ptr< sc_int<64> > index;
  const sc_int<64> low = sc_int<64>(-1e3);
  const sc_int<64> high = sc_int<64>(-1e2);
  index->keep_only(low, high);  // Only 901 possible values
  // Create packets and copy into array
  scv_smart_ptr<packetT> packet;
  packet->length.keep_only(10,1024);
  for (unsigned int i=0; i<10; ++i) {
    packet->src.next();
    packet->dest.next();
    packet->length.next();
    for(unsigned int j=0; j<packet->length; j++) {
      packet->payload[j].next();
    }
    index->next();
    packets[index->read()] = *packet;  // Uses equal operator
  }
  // Iterate through the range looking for packets in the
  // sparse array
  const unsigned int packetsPerLine = 50;
  unsigned int count = 0;
  for (sc_int<64> i=low; i<=high; i++) {
    if (count == 0) {
      scv_out << i << ": ";
    }
    if (packets[i] == defaultPacket) { // uses packetT == operator
      scv_out << ".";
    } else {
      scv_out << "*";
    }
    if (++count == packetsPerLine) {
      scv_out << endl;
      count = 0;
    }
  }
  // Iterate through again, this time printing each packet
  scv_out << endl << endl;
  for (sc_int<64> i=low; i<=high; i++) {
    if (packets[i] != defaultPacket) { // uses packetT == operator
      // Uses output operator
      scv_out <<  i << ": " << packets[i] << endl;
    }
  }
  scv_out << endl;
}

int sc_main(int argc, char** argv) {
  sctop top("top"); 
  sc_start();
  return 0;
}
