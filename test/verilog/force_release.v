module test;
  // tmrg do_not_triplicate a
  reg a;
  initial begin
    force a=1'b0;
    #1;
    release a;
  end

  reg b;
  initial begin
    force b=1'b0;
    #1;
    release b;
  end
endmodule
