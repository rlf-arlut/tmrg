module fsm05_slice(
  clkIn,
  clkOut,
  divNext,
  divNextA,
  divNextB,
  divNextC
);
wire [1:0] divNextVoted;
output [1:0] divNext;
input [1:0] divNextC;
input [1:0] divNextB;
input [1:0] divNextA;
input clkIn;
output clkOut;
reg  [1:0] div;
wire [1:0] divNext =  div-1;

majorityVoter #(.WIDTH(2)) divNextVoter (
    .inA(divNextA),
    .inB(divNextB),
    .inC(divNextC),
    .out(divNextVoted)
    );

always @( posedge clkIn )
  div <= divNextVoted;
assign clkOut =  div[1] ;
endmodule

module fsm05(
  clkInA,
  clkInB,
  clkInC,
  clkOutA,
  clkOutB,
  clkOutC
);
input clkInA;
input clkInB;
input clkInC;
output clkOutA;
output clkOutB;
output clkOutC;
wire [1:0] divNextC;
wire [1:0] divNextB;
wire [1:0] divNextA;

fsm05_slice fsm05A (
    .clkIn(clkInA),
    .clkOut(clkOutA),
    .divNext(divNextA),
    .divNextA(divNextA),
    .divNextB(divNextB),
    .divNextC(divNextC)
    );

fsm05_slice fsm05B (
    .clkIn(clkInB),
    .clkOut(clkOutB),
    .divNext(divNextB),
    .divNextA(divNextA),
    .divNextB(divNextB),
    .divNextC(divNextC)
    );

fsm05_slice fsm05C (
    .clkIn(clkInC),
    .clkOut(clkOutC),
    .divNext(divNextC),
    .divNextA(divNextA),
    .divNextB(divNextB),
    .divNextC(divNextC)
    );
endmodule
