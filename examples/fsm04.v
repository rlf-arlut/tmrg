module fsm04 (in,out,clk);
  // tmrg default do_not_triplicate
  // tmrg triplicate state 
  // tmrg triplicate clk
  input in;
  input clk;
  output out;
  reg state;
  reg stateNext;
  assign out=state;

  always @(posedge clk)
    state <= stateNext;

  always @(state or in)
    stateNext = in ^ state;

endmodule
