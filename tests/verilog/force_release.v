module test;
  // tmrg do_not_touch
  reg a;
  initial begin
    force a=1'b0;
    #1;
    release a;
  end
endmodule
