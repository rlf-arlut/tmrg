module mymod #(parameter M=2)
  (input  logic clock,
   input  logic [M-1:0] d,
   output logic q);
  // tmrg default triplicate
  // tmrg do_not_triplicate d q

  logic ru1 [0:M-1];
//wire ru2a [0:M-1] = ru1; // _tmrg do_not_triplicate ru2
  wire ru2b [0:M-1]; // tmrg do_not_triplicate ru2
  assign ru2b = ru1;
  logic ru3a [0:M-1];
  logic ru3b [0:M-1];

  always @(posedge clock) begin
    ru1 <= d;
//  ru3a <= ru2a;
    ru3b <= ru2b;
  end

  logic [0:M-1] rp1;
  wire [0:M-1] rp2 = ru1; // tmrg do_not_triplicate rp2
  logic [0:M-1] rp3;

  always @(posedge clock) begin
    rp1 <= d;
    rp3 <= rp2;
  end

endmodule
