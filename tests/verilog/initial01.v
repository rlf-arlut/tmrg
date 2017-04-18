module initial01;
  reg x;
  reg y;
  //tmrg triplicate x
  //tmrg do_not_triplicate y
  initial
    begin
      x=1'b1;
    end
    
  initial 
    y=1'b0;
endmodule

