module submodule #(parameter f=3) (input clk, input [f-1:0] d, output q);
  assign q = |d;
endmodule

module paramtest #(parameter f=3, parameter k=3) (input clk,input [f:k]d , output q);
  parameter p1=1;
  parameter p2=1;
  localparam l1=p1+p2;
  localparam l2=f+k;

  wire [f:k] w1=p1;
  wire [f:k] w2=l1;
  
  wire wk;

  assign wk=l1+p1;
  // tmrg default do_not_triplicate
  submodule sm(.clk(clk), .d({3{|l1}}), .q());
  // tmrg triplicate sm2
  submodule sm2(.clk(clk), .d({3{|l2}}), .q());

endmodule

