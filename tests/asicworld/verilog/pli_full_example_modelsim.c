#include "veriuser.h"
#include "pli_full_example.c"

s_tfcell veriusertfs[] = {
  {usertask, 0, 0, 0, counter_monitor, 0, "$counter_monitor"},
  {0}  // last entry must be 0 
};
