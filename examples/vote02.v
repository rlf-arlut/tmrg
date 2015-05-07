module vote02 (in,out);
  input in;
  output out;
  wire combLogic;
  wire inVoted = in;
  assign combLogic = ~inVoted;
  wire combLogicVoted = combLogic;
  assign out = combLogicVoted;
endmodule
