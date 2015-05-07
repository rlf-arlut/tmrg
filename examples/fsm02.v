module fsm02 (in,out,clk);
  // tmrg default triplicate
  input in;
  input clk;
  output out;
  reg state;
  reg stateNext;
  wire stateNextVoted=stateNext;
  assign out=state;

  always @(posedge clk)
    state <= stateNextVoted;

  always @(state or in)
    stateNext = in ^ state;

endmodule
