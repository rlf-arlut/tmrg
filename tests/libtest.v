module complexLogic(input clk, input d, output q1, output q2);
  // tmrg default triplicate
  dff ff1(.clk(clk), .d(d), .q(q1));

  // tmrg do_not_triplicate ff2
  dff ff2(.clk(clk), .d(d), .q(q2));
endmodule

// _tmrg  libtest.v  --lib=lib.v

