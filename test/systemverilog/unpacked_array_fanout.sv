module mymod #(parameter M=2)(
    input  logic clock,
    input  logic [M-1:0] d,
    output logic q
);
  // tmrg default triplicate
  // tmrg do_not_triplicate d q

  // Unpacked registers/wires (range)
  logic  ru1 [0:M-1];
  wire   ru2b [0:M-1]; // tmrg do_not_triplicate ru2
  assign ru2b = ru1;
  logic  ru3a [0:M-1];
  logic  ru3b [0:M-1];

  always @(posedge clock) begin
    ru1 <= d;
    ru3b <= ru2b;
  end
 
  // Unpacked registers/wires (size)
  logic ru10 [M];
  wire ru20b [M]; // tmrg do_not_triplicate ru20
  assign ru20b = ru10;
  logic ru30a [M];
  logic ru30b [M];

  always @(posedge clock) begin
    ru10 <= d;
    ru30b <= ru20b;
  end

/*
  // System verilog not complient assignments of unpacked wires
  // this code is commented by default as both tools used for tmrg CI
  // (iverilog/veriable) do not like this syntax

  wire ru2a [0:M-1] = ru1; // tmrg do_not_triplicate ru2
  wire ru20a [M] = ru10; // tmrg do_not_triplicate ru20
  always @(posedge clock) begin
    ru30a <= ru20a;
    ru30a <= ru20a;
  end
*/

  // Packed registers/wires (size)
  logic [0:M-1] rp1;
  wire [0:M-1] rp2 = ru1; // tmrg do_not_triplicate rp2
  logic [0:M-1] rp3;

  always @(posedge clock) begin
    rp1 <= d;
    rp3 <= rp2;
  end

endmodule
