#ifndef COUNTER_TB_PORTS_H
#define COUNTER_TB_PORTS_H

// Define Complex Type of Input and Out for DUT
struct tagInput {
  unsigned long  clk;
  unsigned long  d_out;
};

struct tagOutput {
  unsigned long  rst;
  int done;
};

typedef struct tagInput    INVECTOR;
typedef struct tagOutput  OUTVECTOR;

#endif
