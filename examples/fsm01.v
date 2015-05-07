module fsm01 (in,out,clk);
  // tmrg default triplicate
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
