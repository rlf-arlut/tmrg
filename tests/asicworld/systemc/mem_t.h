#ifndef MEM_T_H
#define MEM_T_H

class mem_t {
  public:
    mem_t () {}
    virtual ~mem_t() {}

    sc_uint<8>      addr;
    sc_uint<32>     data;

    // Define an assign operator
    mem_t& operator=(const mem_t& rhs) {
      addr=rhs.addr; 
      data=rhs.data; 
      return *this;
    }

    // Define a comparison operator
    friend bool operator==(const mem_t& a, const mem_t& b) {
      if (a.addr != b.addr) {return false;}
      if (a.data != b.data) {return false;}
      return true;
    }

    // Define ostream method to print data
    friend ostream& operator<< (ostream& os, const mem_t& mem) {
      os << " Address : " << mem.addr << " Data : " << mem.data;
      return os;
    }
};

#endif
