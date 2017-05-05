

module paramtestANSI #(parameter f=3, k=3, parameter x=f+k) (input clk,input [f:k]d , output q);
  parameter p1=1;
  parameter [2:0] p2=1;
  localparam l1=p1+p2;
  localparam [2:0] l2=f+k;

  wire [f:k] w1=p1;
  wire [f:k] w2=l1;

  wire wk;

  assign wk=l1+p1;
  
endmodule
