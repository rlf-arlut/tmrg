`define SYN
 module MPA #(
  parameter          PIXEL = 1920
  )(
  input clk320,
  input T1
);
 // tmrg default triplicate
 // tmrg do_not_triplicate             IFL

`ifdef SYN
  wire [6:0] IFL;
`else
  real IFL [6:0], i , k[0:1];
  real z;
`endif

  reg m;
  always @(m) begin
`ifdef SYN
   $display("Test");
`endif
  end
endmodule
