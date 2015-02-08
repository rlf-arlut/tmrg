#ifndef MEM_T_EXT_H
#define MEM_T_EXT_H

SCV_EXTENSIONS(mem_t) {
  public:
    scv_extensions< sc_uint<8> > addr;
    scv_extensions< sc_uint<32> > data;
    SCV_EXTENSIONS_CTOR(mem_t) {
      SCV_FIELD(addr);
      SCV_FIELD(data);
    }
};

#endif
