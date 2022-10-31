module and_or_xor_gates_tmr (output c, d, e, input a, b);
  and and_inst(c, a, b);
  or  or_inst(d, a, b);
  xor xor_inst(e, a, b);
endmodule

module and_or_xor_gates_no_tmr (output c, d, e, input a, b);
  // tmrg default do_not_triplicate
  and and_inst(c, a, b);
  or  or_inst(d, a, b);
  xor xor_inst(e, a, b);
endmodule

