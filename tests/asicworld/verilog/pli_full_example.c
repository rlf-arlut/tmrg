#include "acc_user.h"
 
typedef char * string;
handle clk ;
handle reset ;
handle enable ;
handle dut_count ;
int count ;
int sim_time;
string high = "1";
void counter ();
int pli_conv (string in_string, int no_bits);
 
void counter_monitor() {
  acc_initialize();
  clk       = acc_handle_tfarg(1);
  reset     = acc_handle_tfarg(2);
  enable    = acc_handle_tfarg(3);
  dut_count = acc_handle_tfarg(4);
  acc_vcl_add(clk,counter,null,vcl_verilog_logic);
  acc_close();
}
	
void counter () {
  p_acc_value value;
  sim_time = tf_gettime();
  string i_reset = acc_fetch_value(reset,"%b",value);
  string i_enable = acc_fetch_value(enable,"%b",value);
  string i_count = acc_fetch_value(dut_count,"%b",value);
  string i_clk = acc_fetch_value(clk, "%b",value);
  int size_in_bits= acc_fetch_size (dut_count);
  int tb_count = 0;
  // Counter function goes here
  if (*i_reset == *high) {
    count = 0;
    io_printf("%d, dut_info : Counter is reset\n", sim_time);
  }
  else if ((*i_enable == *high) && (*i_clk == *high)) {
    if ( count == 15 ) {
      count = 0;
    } else {
      count = count + 1;
    }
  }
  // Counter Checker function goes checker logic goes here
  if ((*i_clk != *high) && (*i_reset != *high)) {
    tb_count = pli_conv(i_count,size_in_bits);
    if (tb_count != count) {
        io_printf("%d, dut_error : Expect value %d, Got value %d\n", 
            sim_time, count, tb_count);
  	tf_dofinish();
    } else {
        io_printf("%d, dut_info  : Expect value %d, Got value %d\n", 
            sim_time, count, tb_count);
    }
  }
}

// Multi-bit vector to integer conversion.
int pli_conv (string in_string, int no_bits) {
  int conv = 0;
  int i = 0;
  int j = 0;
  int bin = 0;
  for ( i = no_bits-1; i >= 0; i = i - 1) {
    if (*(in_string + i) == 49) {
      bin = 1;
    } else if (*(in_string + i) == 120) {
      io_printf ("%d, Warning : X detected\n", sim_time);
      bin = 0;
    } else if (*(in_string + i) == 122) {
      io_printf ("%d, Warning : Z detected\n", sim_time);
      bin = 0;
    } else {
      bin = 0;
    }
    conv = conv + (1 << j)*bin;
    j ++;
  } 
  return conv;
}

