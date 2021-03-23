

module paramtestOrder #(parameter [2:0] f=3, k=3, parameter x=f) (input clk,input [f:k]d , output [f:k] q);
  parameter signed p1=1;
  parameter [2:0] p2=1;
  localparam l1=p1+p2;
  localparam signed [2:0] l2=f+k;

  wire [f:k] w1=p1;
  wire [f:k] w2=l1;

  wire [f:k]  w1Voted=w1;
  // tmrg do_not_triplicate wk
  assign q=l1+p1;
  
endmodule
