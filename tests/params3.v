module submodule1 #(parameter f=3) (input clk, input [f-1:0] d, output q);
  // tmrg default triplicate
  assign q = |d;
endmodule

module submodule2 #(parameter f=3) (input clk, input [f-1:0] d, output q);
  // tmrg do_not_touch
  assign q = |d;
endmodule

module submodule3 #(parameter f=3) (input clk, input [f-1:0] d, output q);
  // tmrg default do_not_triplicate
  assign q = |d;
endmodule


module paramtest #(parameter f=3, parameter k=3) (input clk,input [f:k]d , output q);
  parameter p1=1;
  parameter [2:0] p2=1;
  localparam l1=p1+p2;
  localparam [2:0] l2=f+k;

  wire [f:k] w1=p1;
  wire [f:k] w2=l1;
  
  wire wk;

  assign wk=l1+p1;
  // tmrg default do_not_triplicate
  submodule1 sm(.clk(clk), .d({3{|l1}}), .q());
  // tmrg triplicate sm2
  submodule1 sm2(.clk(clk), .d({3{|l2}}), .q());

  // tmrg triplicate sm3
  submodule2 sm3(.clk(clk), .d(l2), .q());

  submodule2 sm4(.clk(clk), .d(p2), .q());

  // tmrg triplicate sm5
  submodule3 sm5(.clk(clk), .d(l2), .q());

  submodule3 sm6(.clk(clk), .d(p2), .q());

endmodule

